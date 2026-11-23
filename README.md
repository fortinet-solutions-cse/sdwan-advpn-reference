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

## Custom Design Option: Regional Internet Backhaul

This branch adds a design option on top of the standard Release 8.0 templates:

- **Global Hubs** (e.g. GH1, GH2) form a single ADVPN region. All Branches *and* all Regional Hubs connect to both of them.
  They are the BGP route-reflectors and the primary way of establishing ADVPN shortcuts between Branches.
  Branch tunnels: `GH1_<ol_type>`, `GH2_<ol_type>` (SD-WAN zone `gh_overlay`).
- **Regional Hubs** provide Internet backhauling (hub-and-spoke, no ADVPN) to the Branches of their region.
  Each Branch also connects to a **backup** Regional Hub in *another* region, used only when the primary fails.
  Branch tunnels: `PRH_<ol_type>` (primary, zone `prh_overlay`) and `BRH_<ol_type>` (backup, zone `brh_overlay`).
  Regional Hub dial-up tunnels: `EDGE_<ol_type>` (zone `edge_overlay`).
  All Regional Hubs share the same health-check loopback (`Lo-HC`, `rh_hc_server`, default 10.200.98.1), like the Global Hubs
  (`hub_hc_server`, default 10.200.99.1), so that the same SD-WAN health-checks fit every Branch.
- Branches peer directly (iBGP on loopbacks) with their Regional Hubs: they advertise their own LANs only and accept only the
  Regional Hub's `lan_prefixes` (local-preference 200 for primary, 150 for backup, above the copies reflected by the Global Hubs).
  The Regional Hubs are not route-reflectors, so they never become transit between Branches and Global Hubs.

The Regional Hubs are described in a separate template named **`RegionalHubs`** (an inventory of the Regional Hubs and of the
primary/backup choice per region), imported by the templates in the same way as the Project Template.
Branches select their region with the `inet_region` variable (optionally overriding the choice with `inet_hub` / `inet_backup_hub`).
Rendering fails if the backup Regional Hub belongs to the same region as the primary.

New templates: `08-Edge-RHOverlay.j2`, `09-Edge-RHRouting.j2` (Branches), `08-RH-Overlay.j2`, `09-RH-Routing.j2` and
`optional/12-RH-Firewall.j2` (Regional Hubs). Regional Hubs also receive all Edge templates (they are Spokes of the Global Hubs).
`optional/11-Edge-SDWAN.j2` and `optional/12-Edge-Firewall.j2` were extended accordingly (zones, Regional/Internet rules, static
default routes with priority 1/10/100 for primary/backup/underlay); in FortiManager, these parts are expected to be covered by the
SD-WAN and Policy templates.

For the offline rendering, put the Regional Hubs in an inventory group called `RH` and pass the `RegionalHubs` file with `-r`:

```
./render_config.py -p dynamic-bgp-on-lo/projects/Project.regional.nocert.j2 -r dynamic-bgp-on-lo/projects/RegionalHubs.regional.j2 -i dynamic-bgp-on-lo/projects/inventory.regional.json
```

The CSV converter accepts the Regional Hubs with `--rhubs inventory.RH.csv`.
The rendered example is available under "dynamic-bgp-on-lo/rendered/regional_backhaul".

## Credits and Feedback

The Jinja Orchestrator is maintained by a team of Consulting Systems Engineers at Fortinet. 

Feel free to report issues and provide your suggestions ([right here](https://github.com/fortinet-solutions-cse/sdwan-advpn-reference/issues)).
Or contact your representatives at Fortinet. 
