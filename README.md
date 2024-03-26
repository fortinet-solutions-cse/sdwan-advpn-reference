# Jinja Orchestrator 7.2 (for Fortinet SD-WAN/ADVPN)

This repository contains generic, ready-to-use Jinja templates that generate our best-practice SD-WAN/ADVPN configuration.
These templates are easily tunable for your projects. We call them the Jinja Orchestrator, because of the layer of abstraction that they provide.

Generally, there are two ways of using the Jinja Orchestrator:

- It can be used as part of the FortiManager-based SD-WAN deployment, thanks to the Jinja engine built into the FortiManager 7.0.1+. 
  The Jinja Orchestrator is used to generate the foundation of your SD-WAN project, supplemented by other templates available in the FortiManager. Our [Deployment Guide for MSSPs (Release 7.2)](https://docs.fortinet.com/document/fortigate/7.2.0/sd-wan-deployment-for-mssps/705134/introduction) contains more information about using the Jinja Orchestrator in this way.

- It can also be used for an offline rendering (without the FortiManager), thanks to a simple renderer written in Python.
  It will generate a set of plain-text files with FOS configuration for each device, which you can simply copy-paste to your FortiGate devices 
  (or use the [Configuration Scripts](https://docs.fortinet.com/document/fortigate/7.0.6/administration-guide/780930/configuration-scripts) feature). 
  This method is handy to build a quick and simple lab or to quickly validate the changes made to your Project Template. 

The main source of documentation for the Jinja Orchestrator - from a brief list of supported features to a detailed reference for each one of them - is available in the [Wiki](https://github.com/fortinet-solutions-cse/sdwan-advpn-reference/wiki).

We also recommend consulting the [Deployment Guide for MSSPs (Release 7.2)](https://docs.fortinet.com/document/fortigate/7.2.0/sd-wan-deployment-for-mssps/705134/introduction) for more information about the templates structure and their use in your projects.

Finally, feel free to report issues and provide your suggestions ([right here](https://github.com/fortinet-solutions-cse/sdwan-advpn-reference/issues)).


## Routing Design Flavors

Jinja Orchestrator 7.2 supports three main design flavors - each under its own directory:

- **"BGP per Overlay"** is the traditional routing design for our SD-WAN/ADVPN deployments,
  in which a separate IBGP session is established over each overlay between an Edge device and a Hub.
  This IBGP session is terminated on the tunnel IP of both sides. For each LAN prefix,
  multiple BGP routes are generated (one route per overlay), and all these routes
  are propagated across the network.

- **"BGP on Loopback"** is a new alternative supported for our SD-WAN/ADVPN deployments.
  With this routing design, a single IBGP session is established between an Edge device and a Hub.
  This IBGP session is terminated on the loopback interface on both sides, but the routes are
  recursively resolved via all available overlays. For each LAN prefix, a single BGP route
  is generated and propagated across the network.

- **"BGP on Loopback Multi VRF"** builds up on the previous flavor, adding Multi-VRF support
  with the new "SD-WAN Segmentation over a Single Overlay" feature (`vpn-id-ipip` encapsulation with VPNv4 BGP address family).
  As in the "BGP on Loopback" flavor, a single IBGP session is established between an Edge device and a Hub.
  That IBGP session will then carry all the routes with extended communities, allowing the neighbor to associate the routes with a specific VRF upon receiving them.
  Traffic is segmented from and into a specific VRF by using a specific encapsulation in the IPSec tunnels.

Please refer to our Reference Architecture and Deployment Guides or consult your Fortinet representatives, in order to select
a design flavor which is the most suitable for your project.


## File Structure

We provide a separate set of templates for each design flavor, each under its own directory.
Once you make your choice, simply use only the templates from the respective directory.

The file structure for all the design flavors is identical, as follows:

- **??-Edge-\*.j2, ??-Hub-\*.j2** - the templates configuring Underlay, Overlay and Routing pillars.
  Normally, there will be no need to edit these files, as they are already designed to generate our
  best-practice configuration.

- **projects** - this sub-directory contains:

  - Examples of Project Templates (**Project.\*.j2**). Those are the most crucial files from the users' perspective.
    This is where you "tune" the templates to your project(s).
    We recommend starting from one of the provided Project Templates and modifying it to match your requirements.
    Normally, this will be the only file that you must modify per project.

  - Example of inventory file in JSON format, listing the devices and their respective per-device variables.
    This file is used by the provided Python renderer.
    When using FortiManager, this file is not needed (but it will show you what per-device variables to set).

- **optional** - additional templates configuring Security and SD-WAN pillars.
  Normally, they are not used when configuring your solution with FortiManager.
  But they are used by the provided Python renderer, so that the generated FOS configuration is complete.

- **rendered** - sub-directory that contains a fully rendered FOS configuration, as an example.

Additionally, in the root directory you will find the Python renderer (**render_config.py**).


## How-To: Deploy with FortiManager

Please consult the [Deployment Guide for MSSPs (Release 7.2)](https://docs.fortinet.com/document/fortigate/7.2.0/sd-wan-deployment-for-mssps/705134/introduction).


## How-To: Offline Rendering (without FortiManager)

We provide a simple offline renderer written in Python. It is tested on Python 3.11 with the following required packages:

```bash
pip3 install jinja2 ansible netaddr
```

Once the required packages are installed, you can render the templates as follows:

1. Clone the repository

1. Edit the `Project` template to describe your project.

1. Prepare an inventory file, setting per-device variables

1. Render the desired design flavor, as follows:

    ```bash
    % ./render_config.py -f <flavor_dir> -i <inventory_file> -p <project_template>
    ```

By default, the rendered configuration will be saved under "out" sub-directory.

You can find an example of an inventory file under each flavor directory ("projects/inventory.json"). As you can see, the expected format is JSON, and it 
must list the Hubs and the Edges separately, as follows:

```json
{
  "Hub": {
    "hub1": {
      "var1": "val1",
      "var2": "val2"
    },
    "hub2": {
      "var1": "val1",
      "var2": "val2"
    }
    
  },

  "Edge": {
    "edge1": {
      "var1": "val1",
      "var2": "val2"
    },
    "edge2": {
      "var1": "val1",
      "var2": "val2"
    }
    
  }
}
```

Alternatively, you can use your inventory file in CSV format, as accepted by the [Import Model Devices from CSV](https://docs.fortinet.com/document/fortimanager/7.2.2/administration-guide/277097/import-model-devices-from-a-csv-file) feature in FortiManager 7.2+. You must still provide two separate CSV files: one for the Hubs and one for the Edges. Use the provided converter to generate a JSON inventory from your CSVs and simply chain its output to the renderer, as follows:

```bash
% inventory_from_csv.py --hubs inventory.Hubs.csv --edge inventory.Edge.csv | ./render_config.py -f bgp-on-loopback -p Project.j2
```

Rendering example:

```bash
% ./render_config.py -f bgp-on-loopback -p Project.j2 -i inventory.json
==============================================
FOS Reference SD-WAN/ADVPN Config Renderer 7.2
==============================================
Project Template: Project.j2
Inventory: inventory.json

Rendering group 'Hub'...
['01-Hub-Underlay.j2', '02-Hub-Overlay.j2', '03-Hub-Routing.j2', '04-Hub-MultiRegion.j2', 'optional/05-Hub-SDWAN.j2', 'optional/06-Hub-Firewall.j2']
Rendering device site1-H1...
Rendering device site1-H2...
Rendering device site2-H1...

Rendering group 'Edge'...
['01-Edge-Underlay.j2', '02-Edge-Overlay.j2', '03-Edge-Routing.j2', 'optional/05-Edge-SDWAN.j2', 'optional/06-Edge-Firewall.j2']
Rendering device site1-1...
Rendering device site1-2...
Rendering device site2-1...

Rendering complete.

% ls out
site1-1		site1-2		site1-H1	site1-H2	site2-1		site2-H1
```


## Describing Your Project

Please consult the [Wiki](https://github.com/fortinet-solutions-cse/sdwan-advpn-reference/wiki) page, check our [Deployment Guide for MSSPs (Release 7.2)](https://docs.fortinet.com/document/fortigate/7.2.0/sd-wan-deployment-for-mssps/705134/introduction) or consult your Fortinet representatives.


## Example Project

You will find several examples of Project Templates and inventory files under the "projects" sub-directory of each design flavor. 
The most complex example is in `Project.dualreg.cert.j2` with its corresponding inventory in `inventory.dualreg.json`.
The rendered FOS configuration (under the "rendered" sub-directory) also corresponds to this project. 

The following diagram describes this project:

![](example_project.png)

**NOTE:** For the Multi-VRF flavor, there are two Customer VRFs in this project. The second VRF is not shown on the above diagram.
