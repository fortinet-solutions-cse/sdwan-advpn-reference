# Jinja CLI Templates for Fortinet SD-WAN/ADVPN

FortiManager 7.0.1+ includes built-in Jinja engine that allows you to use Jinja syntax for CLI Templates.
This repository contains generic, ready-to-use templates that generate our best-practice SD-WAN/ADVPN configuration.
These templates are easily tunable for your projects, as will be briefly explained below.

**[COMING SOON]** Our upcoming Secure SD-WAN Deployment Guide for Service Providers (Release 7.0) will contain more information
about using these templates for your projects.

Additionally, we provide a simple renderer written in Python, which you can use to render the templates without FortiManager.
It will generate a set of plain-text files with FOS configuration for each device, which you can simply copy-paste to your
FortiGate devices (or use the [Configuration Scripts](https://docs.fortinet.com/document/fortigate/7.0.6/administration-guide/780930/configuration-scripts) feature).
This method is handy to build a quick and simple lab or to quickly validate the changes made to your Jinja templates.


## Routing Design Flavors

Currently we provide two main routing design flavors - each under its own directory:

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


Please refer to our Deployment Guide or consult your Fortinet representatives, in order to select
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

- **inventory.json** is an example inventory file for the Python renderer.
  When deploying the solution with FortiManager, per-device mapping of ADOM variables is used instead of this file.
  Hence, it is only needed when using the Python renderer.


## How-To: Deploy with FortiManager

Follow these steps:

1. Download the selected design flavor

1. Edit the `Project` template to describe your project. Use your favorite plain text editor
   (how about trying [Atom](https://atom.io/) or [Visual Studio Code](https://code.visualstudio.com/)?).
   The guidelines to describe your project will follow below.
   There is no need to edit any other files.

1. Import the edited `Project` template into your FortiManager.
   Remember to set its type to "Jinja Script" and call it "Project".
   Create the missing variables, when prompted.

1. Import the rest of the templates from the set ("as is"), setting their type to "Jinja Script" as well.
   Create the missing variables, when prompted.  

   You DO NOT need to import the "optional" templates.

1. Create CLI Template Groups for your Hubs and Edges, as follows:

   - Edge-Template:
     - 01-Edge-Underlay
     - 02-Edge-Overlay
     - 03-Edge-Routing

   - Hub-Template
     - 01-Hub-Underlay
     - 02-Hub-Overlay
     - 03-Hub-Routing
     - 04-Hub-MultiRegion

1. Deploy your devices, assigning the above CLI Template Groups to them and filling in per-device values of the ADOM variables.


## How-To: Use the Python Renderer

1. Clone the repository

1. Edit the `Project` template to describe your project.

1. Prepare an inventory file, setting per-device variables

1. Render the desired design flavor, as follows:

    ```
    ./render_config.py -f <flavor_dir> -i <inventory_file> -p <project_template>
    ```

By default, the rendered configuration will be saved under "out" sub-directory.
Also by default, example Project and inventory files will be used under the selected flavor directory ("projects/Project.j2" and "projects/inventory.json" respectively).

Rendering example:

```
% ./render_config.py -f bgp-on-loopback -i inventory.json
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

The `Project` template contains comments inside that should be useful to understand its contents.
Pay special attention to the syntax - it must be a valid Jinja.
It is recommended to validate the syntax using any online Jinja validation tool, such as [this](https://j2live.ttl255.com/). If there are no syntax errors, the rendering
will return an empty result (since the `Project` template is only defining data structures).

The template contains the following sections:

- **Mandatory Global Definitions** for your project, such as your corporate LAN summary

- **Optional Settings** to control the resulting configuration (you can keep them all commented out for the default behavior)

- **Regions** describe the regions in your project, including the list of Hubs servicing each region

- **Profiles** describe device profiles, mainly physical connectivity of your different sites (LAN ports, WAN ports, whether DHCP is present etc.)

- **Hubs** describe all the Hubs in your project, mainly the overlays that they create (and how Edges can connect to them)

We recommend that you start from the pre-configured examples and adjust them as necessary!  
A complete up-to-date reference listing all the currently supported parameters in the Project template is available in [this](./Project_Template_Reference.md) file.

For more details, please refer to our Deployment Guide or consult your Fortinet representatives.


## Example Project

All the provided examples and the rendered configuration refer to the following project:

![](example_project.png)

**NOTE:** For the Multi-VRF flavor, there are two Customer VRFs used in our examples. The second VRF is not shown on the above diagram.
