#!/usr/bin/env python3

import argparse, textwrap, json, csv

#############################################

parser = argparse.ArgumentParser(description='Generate JSON inventory from CSV',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=textwrap.dedent("""\
                                 Parses CSV files prepared for the "Import Model Devices from CSV" feature supported in FortiManager 7.2+.
                                 Accepts two CSV files (with Hubs and with Edges separately). 
                                 Optionally, accepts also a JSON file with the default values of the variables.
                                 Produces a single JSON inventory file, in the format accepted by the "render_config.py" renderer. 

                                 Therefore, designed to be used as follows:
                                 
                                 inventory_from_csv.py --hubs inventory.Hubs.csv --edge inventory.Edge.csv | ./render_config.py -p Project.j2
                                 inventory_from_csv.py --hubs inventory.Hubs.csv --edge inventory.Edge.csv --defaults var_defaults.json | ./render_config.py -p Project.j2

                                 """))

parser.add_argument('--hubs', metavar='file',
                    help='Hubs inventory file in CSV format (optional)')

parser.add_argument('--edge', metavar='file',
                    help='Edge inventory file in CSV format (optional)')

parser.add_argument('--rhubs', metavar='file',
                    help='Regional Hubs inventory file in CSV format (optional, Regional Internet Backhaul design)')

parser.add_argument('--defaults', metavar='file',
                    help='Default variables file in JSON format (optional)')


args = parser.parse_args()

#############################################

def parseCSV(csvFile):
  dev_dict = {}
  if csvFile:
    with open(csvFile, 'r', encoding='utf-8-sig') as f:
      for d in csv.DictReader(f):
        dev_name = d.pop('Name')
        d.pop('Serial Number')
        d.pop('Device Blueprint')
        dev_dict[dev_name] = { k : v for k, v in d.items() if v }
      
  return dev_dict

def parseDefaults(jsonFile):
  defaults = {}
  if jsonFile:
    with open(jsonFile, 'r') as f:
      defaults = json.load(f)
  return defaults

json_inventory = {
  "defaults": parseDefaults(args.defaults),
  "Hub": parseCSV(args.hubs),
  "Edge": parseCSV(args.edge)
}
if args.rhubs:
  json_inventory["RH"] = parseCSV(args.rhubs)

print(json.dumps(json_inventory, indent = 3))    
