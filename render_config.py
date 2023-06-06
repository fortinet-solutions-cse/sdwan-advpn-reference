#!/usr/local/bin/python

import argparse, json, textwrap, jinja2, shutil
from ansible_collections.ansible.utils.plugins.filter.ipaddr import ipaddr
from os import listdir, chdir, path, makedirs, remove

print("==============================================")
print("FOS Reference SD-WAN/ADVPN Config Renderer 7.2")
print("==============================================")

#############################################

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 usage=textwrap.dedent("""\
                                 Minimum required arguments are -f <flavor_dir> and -p <project_template>
                                 NOTE: To avoid confusion, we NO LONGER have the default choice for the Project Template and the inventory!
                                 Try --help for more details.
                                 """),
                                 epilog=textwrap.dedent("""\
                                 
                                 NOTE: Unlike in previous versions, we NO LONGER have the default choice for the Project Template and the inventory!
                                 You have to specify them explicitly! If the inventory file is not specified using '-i', it will be read from stdin.

                                 Examples:

                                 - Render the entire topology config with "BGP on Loopback" design flavor:
                                    ./render_config.py -f bgp-on-loopback -i inventory.json -p Project.j2

                                 - Render the entire topology config with "BGP per Overlay" design flavor:
                                    ./render_config.py -f bgp-per-overlay -i inventory.json -p Project.j2

                                 - Render the entire topology config with "BGP on Loopback" design flavor, using CSV inventory file:
                                    ./inventory_from_csv.py --hub inventory.Hub.csv --edge inventory.Edge.csv | ./render_config.py -f bgp-on-loopback -p Project.j2

                                 """))

parser.add_argument('-f', '--flavor', metavar='dir', required=True,
                    help='design flavor (specify directory name)')

parser.add_argument('-p', '--project', metavar='file', required=True,
                    help='Project Template')

parser.add_argument('-i', '--inventory', metavar='file',
                    help='device inventory file in json format (default = read from stdin)')

parser.add_argument('-o', '--outdir', metavar='dir', default='out',
                    help='output directory (default="out")')

parser.add_argument('--skip-optional', action='store_true',
                    help="skip optional templates")

args = parser.parse_args()

#############################################

outdir = path.abspath(args.outdir)
makedirs(outdir, exist_ok=True)

flavor = args.flavor
project = args.project
inventory = args.inventory or 0

print("Project Template: " + path.relpath(project))
print("Inventory: " + (path.relpath(inventory) if inventory else "reading from stdin..."))
shutil.copyfile(project, flavor + '/Project')

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(flavor),
    undefined=jinja2.StrictUndefined
)
env.filters['ipaddr'] = ipaddr

with open(inventory, 'r') as inventoryFile:
    devices = json.load(inventoryFile)

for devgroup, devlist in devices.items():
    print()
    print("Rendering group '" + devgroup + "'...")

    list_of_templates = sorted(filter(lambda f: devgroup in f,
        listdir(flavor) +
        [ 'optional/' + j2 for j2 in listdir(flavor + '/optional') if not args.skip_optional ]
    ))
    print(list_of_templates)

    for devname, devmeta in devlist.items():
        print("Rendering device " + devname + "...")
        with open(outdir + '/' + devname, 'w') as outfile:
            for j2 in list_of_templates:
                rendered = env.get_template(j2).render(devmeta)
                # Delete empty lines (cosmetic)
                rendered_stripped = '\n'.join(l for l in rendered.split('\n') if l.strip())

                print("######################################", file=outfile)
                print("# " + j2, file=outfile)
                print("######################################", file=outfile)
                print(rendered_stripped, file=outfile)
                print('', file=outfile)

print()
print("Rendering complete.")
remove(flavor + '/Project')
