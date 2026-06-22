# [EXPERIMENTAL VERSION] Jinja Orchestrator 8.0 (for Fortinet SD-WAN/ADVPN)

This repository contains generic, ready-to-use Jinja templates that generate our best-practice SD-WAN/ADVPN configuration.
These templates are easily tunable for your projects.
We call them the **Jinja Orchestrator**, because of the layer of abstraction that they provide.

The detailed documentation is now available in the [Wiki](https://github.com/fortinet-solutions-cse/sdwan-advpn-reference/wiki).

## FortiManager-based Deployment

The Jinja Orchestrator can be used as part of the FortiManager-based SD-WAN deployment, thanks to the Jinja engine built into the
FortiManager 7.0.1+. The Jinja Orchestrator is used to generate the foundation of your SD-WAN project, supplemented by other templates available in the FortiManager. Our [Deployment Guide for MSSPs (Release 7.6)](https://docs.fortinet.com/document/fortigate/7.6.0/sd-wan-deployment-for-mssps/) contains more information about using the Jinja Orchestrator in this way.

## Offline Rendering

The Jinja Orchestrator can also be used for an offline rendering (without the FortiManager), thanks to a simple renderer written in Python. 
It will generate a set of plain-text files with FOS configuration for each device, which you can simply copy-paste to your
FortiGate devices (or use the [Configuration Scripts](https://docs.fortinet.com/document/fortigate/7.0.6/administration-guide/780930/configuration-scripts) feature). This method is handy to build a quick and simple lab or to quickly validate the changes made to your 
Project Template. 

The following prerequisites must be installed prior to using the offline renderer (tested on Python 3.11):

```
pip3 install jinja2 ansible netaddr
```

Usage: 

```
./render_config.py -p <project_template> -i <inventory_file>
```

Several Project Template and inventory examples can be found under "dynamic-bgp-on-lo/project" directory. But keep in mind that those are 
merely examples! As you can see, the inventory file is in JSON format, it lists the Hubs and the Edges (Spokes) separately and it also 
supports default variables (that will be applied to all devices).

Note that you can also use your inventory file in CSV format, as accepted by the [Import Model Devices from CSV](https://docs.fortinet.com/document/fortimanager/7.6.2/administration-guide/277097) feature in FortiManager 7.2+.
You must still provide two separate CSV files: one for the Hubs and one for the Edges.
Use the provided converter to generate a JSON inventory from your CSVs and simply chain its output to the renderer, as follows:

```
./inventory_from_csv.py --hubs inventory.Hubs.csv --edge inventory.Edge.csv | ./render_config.py -p Project.j2
```

The offline rendering differs from the FortiManager-based rendering, because it must cover the entire configuration - including those parts
which would be otherwise covered by the other FortiManager templates. That is why, by default, additional Jinja templates are rendered -
those under the "dynamic-bgp-on-lo/optional" sub-directiory. These optional templates can be skipped by adding `--skip-optional` flag.

By default, the rendered configuration will be saved under the "out" sub-directory. This can be customized with `-o` flag.

## Example Projects

Under "dynamic-bgp-on-lo/rendered", you will find a couple of fully rendered example projects.
The diagrams for each project can be found in each respective subfolder. 
Each example project has been rendered using the provided offline renderer ("render_config.py") and a pair of Project and inventory files
from "dynamic-bgp-on-lo/projects".

Here is the summary of the example projects:

| Subfolder        | Description                                                 | Project Template                    | Inventory File                   |
|------------------|-------------------------------------------------------------|-------------------------------------|----------------------------------|
| single_hub       | Simple SD-WAN project: one Hub, two Spokes                  | Project.singlehub.generic.nocert.j2 | inventory.singlehub.generic.json |
| deployment_guide | Dual-region project from the Depoloyment Guide for MSSPs    | Project.dualreg.cert.j2             | inventory.dualreg.json           |
| mixed            | Dual-region project from the Managed SD-WAN HoL (CustomerU) | Project.dualreg.mixed.nocert.j2     | inventory.dualreg.mixed.json     |
| multi_vrf        | Dual-region multi-VRF project                               | Project.dualreg.multivrf.nocert.j2  | inventory.dualreg.multivrf.json  |

It is important to emphasize that these projects are **just examples**!
By no means do they limit what you can do with the Jinja Orchestrator.
It can be helpful to start from one of the example Project Templates when you prepare your own. 

For example, you can render the same configuration as in the "deployment_guide" subfolder, by running the following:

```
./render_config.py -p dynamic-bgp-on-lo/projects/Project.dualreg.cert.j2 -i dynamic-bgp-on-lo/projects/inventory.dualreg.json
```

## Credits and Feedback

The Jinja Orchestrator is maintained by a team of Consulting Systems Engineers at Fortinet. 

Feel free to report issues and provide your suggestions ([right here](https://github.com/fortinet-solutions-cse/sdwan-advpn-reference/issues)).
Or contact your representatives at Fortinet. 
