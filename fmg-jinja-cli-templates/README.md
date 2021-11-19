# FMG Jinja CLI Templates for SD-WAN with ADVPN

FortiManager 7.0.1+ includes built-in Jinja engine that allows you to use Jinja syntax for CLI Templates.
This repository contains a set of generic templates that configure underlay, overlay and routing of the SD-WAN/ADVPN solution.

In order to fine-tune it to your project, you must fill in `Project.j2` template which is then imported by all other templates.
No modifications should be necessary to the rest of files.


## How-To

Follow these simple steps:

1. Download the templates

1. Edit `Project.j2` to describe your project. Use your favorite plain text editor
   (how about trying [Atom](https://atom.io/) or [Visual Studio Code](https://code.visualstudio.com/)?).
   The guidelines to describe your project will follow below.
   There is no need to edit any other files.

1. Import the edited `Project` template into your FMG (the extension `.j2` will be omitted automatically).
   Remember to set its type to "Jinja Script".
   Create the missing meta fields, if prompted.

1. Import the rest of the templates from this folder ("as is"), setting their type to "Jinja Script" as well.
   Create the missing meta fields, if prompted.

1. Create CLI Template Groups for your Hubs and Edges:

   - Edge-Template:
     - 01-Edge-Underlay
     - 02-Edge-Overlay
     - 03-Edge-Routing

   - Hub-Template
     - 01-Hub-Underlay
     - 02-Hub-Overlay
     - 03-Hub-Routing
     - 04-Hub-MultiRegion

1. Deploy your devices, filling in per-device meta fields and assigning the above CLI Template Groups to them.


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
