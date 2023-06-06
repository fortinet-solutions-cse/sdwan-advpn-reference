#!/usr/local/bin/python

import argparse, textwrap, json, csv

#############################################

parser = argparse.ArgumentParser(description='Generate JSON inventory from CSV',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=textwrap.dedent("""\
                                 Parses CSV files prepared for the "Import Model Devices from CSV" feature supported in FortiManager 7.2+.
                                 Accepts two CSV files (with Hubs and with Edges separately). 
                                 Produces a single JSON inventory file, in the format accepted by the "render_config.py" renderer. 

                                 Therefore, designed to be used as follows:
                                 
                                 inventory_from_csv.py --hubs inventory.Hubs.csv --edge inventory.Edge.csv | ./render_config.py -f bgp-on-loopback -p Project.j2
                                 inventory_from_csv.py --hubs inventory.Hubs.csv --edge inventory.Edge.csv | ./render_config.py -f bgp-per-overlay -p Project.j2

                                 """))

parser.add_argument('--hubs', metavar='file',
                    help='Hubs inventory file in CSV format (optional)')

parser.add_argument('--edge', metavar='file',
                    help='Edge inventory file in CSV format (optional)')

args = parser.parse_args()

#############################################

def parseCSV(csvFile):
  dev_dict = {}
  if csvFile:
    with open(csvFile, 'r', encoding='utf-8-sig') as f:
      for d in csv.DictReader(f):
        dev_name = d.pop('name')
        d.pop('sn')
        d.pop('device blueprint')
        dev_dict[dev_name] = { k : v for k, v in d.items() }
      
  return dev_dict

json_inventory = {
  "Hub": parseCSV(args.hubs),
  "Edge": parseCSV(args.edge)
}

print(json.dumps(json_inventory, indent = 3))    
