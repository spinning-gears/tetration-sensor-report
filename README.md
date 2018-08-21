# Tetration Sensor Report

The contents of this repository generate a CSV report of all sensors registered with Tetration. This is the same data available within the Tetration GUI, but some people prefer to browse this data offline with a tool like Excel. The API returns time expressed in epoch format, so the script converts those fields to local time zone.

This script will also look for duplicates like host name and save them to a separate CSV file. More details below.

## Running the script

Running `getSensorData.py --help` shows that the script has the following inputs:
- `--tetration`: the URL for the Tetration GUI
- `--credentials`: path to a JSON credentials file for Tetration
- `--csv`: *optional* argument that specifies the name to use for the file. If no name is specified, `sensors.csv` will be used.
- `--expand`: *optional* switch that specifies each interface of each sensor should occupy its own line in the report
- `--last_config_fetch`: *optional* fetch only sensors whose last config fetch has been **more** than this integer number of days ago
- `--last_software_update`: *optional* fetch only sensors whose last software update has been **more** than this integer number of days ago
- `--filter_deleted`: *optional* does not include sensors that have been deleted but still show up in Tetration because they haven't been garbage-collected

The script uses the REST API to retrieve 250 sensors at a time. That number is specified by the locally declared `pageSize` variable, so you are free to change that in the script if your environment has different requirements.

### Examples

Generate a CSV named `sensors.csv` containing all sensors.
```bash
python getSensorData.py --tetration https://example.com
```
Generate a CSV named `sensors.csv` containing all sensors that have not retrieved their configuration from Tetration in 10 days *or more*.
```bash
python getSensorData.py --tetration https://example.com --last_config_fetch 10
```
Generate a CSV named `sensors.csv` containing all sensors that have not retrieved their configuration from Tetration in 10 days *or more* while while ignoring sensors that have been deleted from Tetration. Deleted sensors remain in the database for some number of hours before being "garbage collected".
```bash
python getSensorData.py --tetration https://example.com --last_config_fetch 10 --filter_deleted
```
Generate a CSV named `unique.csv` containing all sensors that have not been deleted.
```bash
python getSensorData.py --tetration https://example.com --csv unique.csv --filter_deleted
```
Generate a CSV named `expanded.csv` containing every interface of every host. Sensors and host names will appear multiple times if a host has multiple interfaces. More details about this can be found below.
```bash
python getSensorData.py --tetration https://example.com --csv expanded.csv --expand
```
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
