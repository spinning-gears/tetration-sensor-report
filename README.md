# Tetration Sensor Report

The contents of this repository generate a CSV report of all sensors registered with Tetration. This is the same data available within the Tetration GUI, but some people prefer to browse this data offline with a tool like Excel.

This script will also look for duplicates like host name and save them to a separate CSV file. More details below.

## Running the script

Running `getSensorData.py --help` shows that the script has the following inputs:
- `--tetration`: the URL for the Tetration GUI
- `--credentials`: path to a JSON credentials file for Tetration
- `--csv`: *optional* argument that specifies the name to use for the file. If no name is specified, `sensors.csv` will be used.
- `--expand`: *optional* switch that specifies each interface of each sensor should occupy its own line in the report

The script uses the REST API to retrieve 250 sensors at a time. That number is specified by the locally declared `pageSize` variable, so you are free to change that in the script if your environment has different requirements.

The API returns time expressed in epoch format, so the script converts those fields to local time zone.

## Output

The output will look slightly different depending on whether or not you use the `--expand` switch.

### Without expand switch

A normal run of the script will produce a CSV file with one line per registered sensor (host). Many hosts will have multiple interfaces, and those interfaces will all be saved in JSON format inside one cell in the CSV.

In this mode, the script looks for and generates CSV reports for duplicate:
- host_name
- uuid

### With expand switch

When the `expand` switch is passed to the script, the CSV report will be much longer because each interface for each host will be its own line in the report. If a host has four interfaces, then its hostname and UUID will be displayed four times in the report.

This mode is most helpful when searching for specific IP addresses or MAC addresses.

In this mode, the script looks for and generates CSV reports for duplicate:
- IP address
- MAC address
