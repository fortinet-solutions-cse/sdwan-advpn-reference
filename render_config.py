#!/usr/local/bin/python

import argparse, yaml, textwrap
from jinja2 import Template
from os import listdir, chdir, path, makedirs

#############################################

parser = argparse.ArgumentParser(description='FOS Reference SD-WAN/ADVPN Config Renderer',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=textwrap.dedent("""\
                                 Examples:

                                 - Render a single template for a single device:
                                    ./render_config.py -d deployment-example.yml -j topo1-separate-underlays/base/04-hub-firewall.conf.j2 dc1_fgt

                                 - Render the entire topology config for a single device:
                                    ./render_config.py -d deployment-example.yml -t topo1-separate-underlays dc1_fgt

                                 - Render the entire topology config for all devices:
                                    ./render_config.py -d deployment-example.yml -t topo1-separate-underlays
                                 """))
parser.add_argument('-d', '--deployment', metavar='yaml', required=True,
                    type=argparse.FileType('r'),
                    help='yaml with deployment variables')
parser.add_argument('-j', '--j2file', metavar='jinja2',
                    help='single jinja2 template to render')
parser.add_argument('-t', '--topology', metavar='dir',
                    help='entire topology to render (specify directory name)')
parser.add_argument('-o', '--outdir', metavar='dir', default='out',
                    help='output directory (default="out")')
parser.add_argument('device', nargs='?',
                    help='device to render (default=all)')
args = parser.parse_args()

#############################################

outdir = path.abspath(args.outdir)
makedirs(outdir, exist_ok=True)

deployment = yaml.safe_load(args.deployment)
list_of_devices = [ args.device ] if args.device else deployment['devices'].keys()

if args.topology:
    chdir(args.topology)

for dev in list_of_devices:
    deployment['this_dev'] = dev
    dev_type = deployment['profiles'][deployment['devices'][dev]['profile']]['type']
    if args.j2file:
        list_of_j2files = filter(lambda f: dev_type in f, [ args.j2file ])
    else:
        # Base templates
        list_of_j2files = sorted(filter(lambda f: dev_type in f, listdir('base')))
        # Plugin templates
        for p in filter(lambda f: dev_type in f and f in deployment['plugins'], listdir('plugins')):
            list_of_j2files.append(p)

    with open(outdir+'/'+dev, 'w') as outfile:
        print('Rendering device ' + dev + '...')
        for f in sorted(list_of_j2files):
            if args.topology:
                f = 'base/' + f if f in listdir('base') else 'plugins/' + f
            print('   Rendering ' + f + '...')
            print("######################################", file=outfile)
            print("# " + f, file=outfile)
            print("######################################", file=outfile)
            with open(f, 'r') as j2file:
                template = Template(j2file.read())
            print(template.render(deployment), file=outfile)
            print('', file=outfile)

print("Rendering complete.")
