"""
Copyright (c) 2018 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Doron Chosnek"
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

# pylint: disable=invalid-name

import argparse
import csv
import json
import time

import requests.packages.urllib3
from tetpyclient import RestClient

requests.packages.urllib3.disable_warnings()

# =============================================================================
# FUNCTIONS
# -----------------------------------------------------------------------------

def getSensors(restclient, pageSize=100, expand_interfaces=False):
    """ Retrieves data about all sensors for the given restclient.

    Arguments:
        restclient {RestClient} -- the restclient to use for API calls so this
            function doesn't have to know anything about authentication
        pageSize {integer} -- number of records to return in each API call; no
            real reason to change this in most cases
    
    Returns:
        {list} -- a list of dictionaries containing every sensor parameter

    """
    offset = ""
    sensorList = []
    while True:
        resp = restclient.get('/openapi/v1/sensors?limit=' + str(pageSize) + '&offset=' + offset)
        if resp.status_code == 200:
            for result in resp.json()["results"]:
                if expand_interfaces:
                    for intf in result["interfaces"]:
                        temp_dict = result.copy()
                        temp_dict.update(intf)
                        temp_dict.pop("interfaces", None)
                        sensorList.append(temp_dict)
                else:
                    # result["interfaces"] = len(result["interfaces"])
                    sensorList.append(result)
        else:
            print "[ERROR] reading from offset '{}' at the sensors API. Response:".format(offset)
            print resp, resp.text
            break
        
        # this is the control for this while loop
        if 'offset' in resp.json().iterkeys():
            offset = resp.json()["offset"]
        else:
            break
    
    return sensorList


def convertEpochTime(source, field):
    """Converts time expressed in seconds to a human readable date.

    Arguments:
        source {list}: list of dictionaries that may contain multiple keys

        field {string}: the key in the dictionary to be converted

    Returns:
        {list} - list of dictionaries with one new field in each dictionary
    """
    new_field = field + "_converted"
    for entry in source:
        if field in entry.keys():
            entry[new_field] = time.ctime(int(entry[field]))
    return source


def writeToCsv(source, filename):
    """Writes to CSV if there is supplied dictionary is not empty.

    Arguments:
        source {list}: list of dictionaries to write to CSV

        filename {string}: name to use when creating CSV
    """
    if len(source):
        myKeys = source[0].keys()
        # deleted_at is a key that appears for sensors that have been deleted
        # but not yet garbage collected in Tetration; it will be rare to see
        # this key but we make sure it is included just in case
        if "deleted_at" not in myKeys:
            myKeys.append('deleted_at')
        if "deleted_at_converted" not in myKeys:
            myKeys.append('deleted_at_converted')

        with open(filename, 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, myKeys)
            dict_writer.writeheader()
            dict_writer.writerows(source)
        print str(len(source)) + " records saved to " + filename
        
    return None


def saveDuplicates(source, field):
    """Looks for duplicate values in the specified field. Takes a list of
    dictionaries, and saves every dictionary that has a duplicate of another
    dictionary in the specified field. For example, in the below list of
    dictionaires, the first two records have the same hostname. If this
    function is asked to look at the 'host' field, it would save th first two
    entries. If it were asked to look at 'uuid' or 'ip', it would not save any.
    [
        {'uuid':'123', 'host':'database', 'ip':'172.16.30.1'},
        {'uuid':'456', 'host':'database', 'ip':'172.16.30.2'},
        {'uuid':'789', 'host':'application', 'ip':'172.16.30.3'}
    ]

    Arguments:
        source {list}: list of dictionaries to search

        field {string}: key value for which to find duplicates
    """
    # first we capture which duplicates exist
    existing = []
    duplicates = []
    for entry in source:
        if entry[field] in existing:
            duplicates.append(entry[field])
        else:
            existing.append(entry[field])
    
    # now that we have the list of duplicates, we save all records that have
    # that value
    dupesToCsv = []
    unique_duplicates = set(duplicates)
    for entry in source:
        if entry[field] in unique_duplicates:
            dupesToCsv.append(entry)
    
    # if duplicates were found, save them to a CSV file
    if len(dupesToCsv):
        myFilename = str(field) + '_duplicates.csv'
        writeToCsv(dupesToCsv, myFilename)
    
    return None


# =============================================================================
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # ARGPARSE

    parser = argparse.ArgumentParser(description='Remove one specific VRF and its associated elements.')
    parser.add_argument('--tetration', help="URL of Tetration instance")
    parser.add_argument('--credentials', default='api_credentials.json', help="path to credentials file")
    parser.add_argument('--csv', default='sensors.csv', help="name of CSV output file")
    parser.add_argument('--expand', action='store_true', help="display each interface on its own line")
    args = parser.parse_args()

    restclient = RestClient(
        args.tetration,
        credentials_file=args.credentials,
        verify=False
    )
    requests.packages.urllib3.disable_warnings()
    
    # -------------------------------------------------------------------------
    # Dump sensors to CSV

    toCSV = getSensors(restclient, pageSize=250, expand_interfaces=args.expand)

    # add fields to each line in the CSV with human-readable version of time/date
    # for the fields that are expressed in seconds
    toCSV = convertEpochTime(toCSV, "last_config_fetch_at")
    toCSV = convertEpochTime(toCSV, "last_software_update_at")
    toCSV = convertEpochTime(toCSV, "deleted_at")

    # dump to the specified CSV file
    writeToCsv(toCSV, args.csv)

    # if the user chose an expanded view, then we can check for MAC and IP
    # duplicates, but things like UUID and host name will definitely be
    # duplicated since that is the purpose of the expanded view (to show
    # each interface on its own row and duplicate all other fields)
    if args.expand:
        saveDuplicates(toCSV, 'ip')
        saveDuplicates(toCSV, 'mac')
    else:
        saveDuplicates(toCSV, 'uuid')
        saveDuplicates(toCSV, 'host_name')
