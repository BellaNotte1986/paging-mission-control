import sys
from . import process_data

if len(sys.argv) != 2:
    print(f"Usage: python mission_control.py [input_data]")
    sys.exit(1)

records = process_data.read_records()
print(*records, sep="\n")
