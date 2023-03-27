# Paging Mission Control

![Lint and Test](https://github.com/jonathan-d-zhang/paging-mission-control/actions/workflows/lint-test.yaml/badge.svg)

## Installation
This project requires Python 3.8+. You can install paging-mission-control using pip
```bash
python -m pip git+https://github.com/jonathan-d-zhang/paging-mission-control.git
```

## Usage
To run the program, use this command.
```bash
python -m paging_mission_control [input_data_file]
```
### Input Format
`paging_mission_control` expects newline separated records in a specific format, namely
```
timestamp|satellite_id|red_high|yellow_high|yellow_low|red_low|raw_value|component
```
where
- `timestamp` - a timestamp in the format `%Y%m%d %H:%M:%S.%f`. The time zone is assumed to be UTC. See [this link](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for info about the format codes.
- `satellite_id` - the id of the satellite that emitted the data in this row.
- `red_high`, `yellow_high`, `yellow_low`, `red_low` - boundary values for `raw_value`.
- `raw_value` - the raw value read by the satellite's sensor.
- `component` - the component being measured. Currently, only accepts BATT or TSTAT, for BATTery or ThermoSTAT.

## Prompt
The prompt for this project is in [prompt.md](prompt.md)
