#!/usr/bin/env python3

import argparse, json, textwrap, jinja2, shutil, atexit
from ansible_collections.ansible.utils.plugins.filter.ipaddr import ipaddr
from os import listdir, chdir, path, makedirs, remove

print("===============================================")
print("Jinja Orchestrator 7.6: Offline Config Renderer")
print("===============================================")

#############################################

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 usage=textwrap.dedent("""\
                                 Minimum required argument is -p <project_template>
                                 NOTE: To avoid confusion, we NO LONGER have the default choice for the Project Template and the inventory!
                                       But we DO have a default choice of the design flavor, since it is now unified.
                                 Try --help for more details.
                                 """),
                                 epilog=textwrap.dedent("""\
                                 
                                 NOTE: Unlike in previous versions, we NO LONGER have the default choice for the Project Template and the inventory!
                                 You have to specify them explicitly! If the inventory file is not specified using '-i', it will be read from stdin.
                                 But we DO use the default design flavor ("dynamic-bgp-on-lo"), unless you customize it with '-f'.

                                 Examples:

                                 - Render the entire topology config with the default design flavor:
                                    ./render_config.py -p Project.j2 -i inventory.json

                                 - Render the entire topology config with a custom design flavor:
                                    ./render_config.py -f my-custom-design -p Project.j2 -i inventory.json

                                 - Render the entire topology config using CSV inventory file:
                                    ./inventory_from_csv.py --hub inventory.Hub.csv --edge inventory.Edge.csv | ./render_config.py -p Project.j2

                                 - Render a Regional Internet Backhaul topology (with Regional Hubs inventory):
                                    ./render_config.py -p Project.j2 -r RegionalHubs.j2 -i inventory.json

                                 """))

parser.add_argument('-f', '--flavor', metavar='dir', default='dynamic-bgp-on-lo',
                    help='design flavor (specify directory name, default = dynamic-bgp-on-lo)')

parser.add_argument('-p', '--project', metavar='file', required=True,
                    help='Project Template')

parser.add_argument('-i', '--inventory', metavar='file',
                    help='device inventory file in json format (default = read from stdin)')

parser.add_argument('-o', '--outdir', metavar='dir', default='out',
                    help='output directory (default="out")')

parser.add_argument('-r', '--regional-hubs', metavar='file',
                    help='Regional Hubs template (optional, imported by the templates as "RegionalHubs")')

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
shutil.copyfile(project, flavor + '/00-Project')
# Regional Hubs inventory: always present, so that the templates can import it unconditionally
if args.regional_hubs:
    print("Regional Hubs: " + path.relpath(args.regional_hubs))
    shutil.copyfile(args.regional_hubs, flavor + '/RegionalHubs')
else:
    open(flavor + '/RegionalHubs', 'w').close()

# Remove the temporary copies on exit, also when rendering fails
@atexit.register
def cleanup():
    for f in [ '00-Project', 'RegionalHubs' ]:
        if path.exists(flavor + '/' + f):
            remove(flavor + '/' + f)

# Device group -> template name tokens ("NN-<token>-Name.j2")
# Regional Hubs are Spokes of the Global Hubs, so they also get the Edge templates
group_templates = {
    'Hub': [ 'Hub' ],
    'Edge': [ 'Edge' ],
    'RH': [ 'Edge', 'RH' ]
}

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(flavor),
    undefined=jinja2.StrictUndefined
)
env.filters['ipaddr'] = ipaddr

with open(inventory, 'r') as inventoryFile:
    devices = json.load(inventoryFile)

defaults = devices.pop('defaults', {})
for devgroup, devlist in devices.items():
    print()
    print("Rendering group '" + devgroup + "'...")

    tokens = group_templates.get(devgroup, [ devgroup ])
    list_of_templates = sorted(filter(lambda f: any('-' + t + '-' in f for t in tokens),
        listdir(flavor) +
        [ 'optional/' + j2 for j2 in listdir(flavor + '/optional') if not args.skip_optional ]
    ))
    print(list_of_templates)

    for devname, devmeta in devlist.items():
        print("Rendering device " + devname + "...")
        with open(outdir + '/' + devname, 'w') as outfile:
            print("execute batch start", file=outfile)
            for j2 in list_of_templates:
                rendered = env.get_template(j2).render(defaults|devmeta)
                # Delete empty lines (cosmetic)
                rendered_stripped = '\n'.join(l for l in rendered.split('\n') if l.strip())

                print("######################################", file=outfile)
                print("# " + j2, file=outfile)
                print("######################################", file=outfile)
                print(rendered_stripped, file=outfile)
                print('', file=outfile)
            print("execute batch end", file=outfile)

print()
print("Rendering complete.")
