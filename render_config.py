#!/usr/local/bin/python

import argparse, json, textwrap, jinja2
from ansible_collections.ansible.utils.plugins.filter.ipaddr import ipaddr
from os import listdir, chdir, path, makedirs

#############################################

parser = argparse.ArgumentParser(description='FOS Reference SD-WAN/ADVPN Config Renderer',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=textwrap.dedent("""\
                                 Examples:

                                 - Render the entire topology config with "BGP on Loopback" design flavor:
                                    ./render_config.py -f bgp-on-loopback -i inventory.json

                                 - Render the entire topology config with "BGP per Overlay" design flavor:
                                    ./render_config.py -f bgp-per-overlay -i inventory.json
                                 """))

parser.add_argument('-f', '--flavor', metavar='dir', required=True,
                    help='design flavor (specify directory name)')

parser.add_argument('-i', '--inventory', metavar='file', required=True,
                    help='device inventory file (in json format)')

parser.add_argument('-o', '--outdir', metavar='dir', default='out',
                    help='output directory (default="out")')

args = parser.parse_args()

#############################################

outdir = path.abspath(args.outdir)
makedirs(outdir, exist_ok=True)

flavor = args.flavor

env = jinja2.Environment(loader=jinja2.FileSystemLoader(flavor))
env.filters['ipaddr'] = ipaddr

with open(args.inventory, 'r') as inventoryFile:
    devices = json.load(inventoryFile)

for devgroup, devlist in devices.items():
    print("Rendering group '" + devgroup + "'...")

    list_of_templates = sorted(filter(lambda f: devgroup in f,
        listdir(flavor) +
        [ 'optional/' + j2 for j2 in listdir(flavor + '/optional') ]
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

print("Rendering complete.")