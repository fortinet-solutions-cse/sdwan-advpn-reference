#!/usr/local/bin/python

import argparse, yaml, textwrap
from jinja2 import Template
from os import listdir, chdir

#############################################

parser = argparse.ArgumentParser(description='FOS Reference SD-WAN/ADVPN Config Renderer',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=textwrap.dedent("""\
                                 Examples:

                                 - Render a single template:
                                    ./render_config.py -d deployment-example.yml -j topo1-separate-underlays/base/04-hub-firewall.conf.j2 dc1_fgt

                                 - Render the entire topology config:
                                    ./render_config.py -d deployment-example.yml -j topo1-separate-underlays dc1_fgt
                                 """))
parser.add_argument('-d', '--deployment', metavar='yaml', required=True,
                    type=argparse.FileType('r'),
                    help='yaml with deployment variables')
parser.add_argument('-j', '--j2file', metavar='jinja2',
                    help='single jinja2 template to render')
parser.add_argument('-t', '--topology', metavar='dir',
                    help='entire topology to render (specify directory name)')
parser.add_argument('device',
                    help='device to render')
args = parser.parse_args()

#############################################

deployment = yaml.safe_load(args.deployment)
deployment['this_dev'] = args.device

dev_type = deployment['profiles'][deployment['devices'][args.device]['profile']]['type']

if args.topology:
    chdir(args.topology + '/base')
list_of_j2files = [ args.j2file ] if args.j2file else sorted(filter(lambda f: dev_type in f, listdir()))

for f in list_of_j2files:
    print("######################################")
    print("# " + f)
    print("######################################")
    with open(f, 'r') as j2file:
        template = Template(j2file.read())
    print(template.render(deployment))
    print()
