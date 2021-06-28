# FOS Reference Configuration: SD-WAN with ADVPN

## Intro

This repository contains FortiOS configuration templates for different SD-WAN topologies with ADVPN.
All the templates are written in Jinja. Deployment variables can be defined in YAML, as demonstrated in
several examples (see `example-*.yml` under each topology).

A simple renderer written in python is also provided (see `render_config.py`).
It can render a single template for a specified device or an entire topology for all devices defined in YAML.

Required python3 modules to run the renderer:

```
pip3 install requests pyyaml jinja2
```

Usage example:

```
% ./render_config.py -d topo1-separate-underlays/example-1reg-2hub.yml -t topo1-separate-underlays
Rendering device dc1_fgt...
   Rendering base/01-hub-overlay.conf.j2...
   Rendering base/02-hub-routing.conf.j2...
   Rendering base/03-hub-sdwan.conf.j2...
   Rendering plugins/035-hub-h2e.j2...
   Rendering base/04-hub-firewall.conf.j2...
   Rendering plugins/hub-lan.conf.j2...
Rendering device dc2_fgt...
   Rendering base/01-hub-overlay.conf.j2...
   Rendering base/02-hub-routing.conf.j2...
   Rendering base/03-hub-sdwan.conf.j2...
   Rendering plugins/035-hub-h2e.j2...
   Rendering base/04-hub-firewall.conf.j2...
   Rendering plugins/hub-lan.conf.j2...
Rendering device branch1_fgt...
   Rendering base/01-edge-overlay.conf.j2...
   Rendering base/02-edge-routing.conf.j2...
   Rendering base/03-edge-sdwan.conf.j2...
   Rendering base/04-edge-firewall.conf.j2...
   Rendering plugins/edge-h2e.j2...
Rendering device branch2_fgt...
   Rendering base/01-edge-overlay.conf.j2...
   Rendering base/02-edge-routing.conf.j2...
   Rendering base/03-edge-sdwan.conf.j2...
   Rendering base/04-edge-firewall.conf.j2...
   Rendering plugins/edge-h2e.j2...
Rendering complete.

% ls -l out
total 112
-rw-r--r--@ 1 dperets  staff  12650 Dec 10 12:17 branch1_fgt
-rw-r--r--@ 1 dperets  staff  12650 Dec 10 12:17 branch2_fgt
-rw-r--r--@ 1 dperets  staff   9511 Dec 10 12:17 dc1_fgt
-rw-r--r--@ 1 dperets  staff   9511 Dec 10 12:17 dc2_fgt
```

## Topology 1: Separate Underlays

Requirements: FOS 6.4.5+

This base topology includes two separate underlay transport networks.
A typical example would be: Internet and MPLS.

The topology is multi-regional, with arbitrary number of regions and Regional Hubs.

### Features:

Corporate Access (CPE to CPE):

- Separate IPSEC overlay between Edge CPEs (Spokes) and each Regional Hub, over each underlay transport
  (hence, with 2 underlays + 2 Regional Hubs, each Edge CPE builds 4 IPSEC tunnels)

- Full-mesh IPSEC overlays between Regional Hubs, over each underlay transport  

- IBGP sessions over each overlay (both within regions and between regions)

- ADVPN shortcuts are enabled within each overlay

- ADVPN shortcuts are not possible between different overlays (e.g. between Internet and MPLS)

- Cross-regional ADVPN shortcuts are enabled

- The traffic prefers to flow via ADVPN shortcut, when possible

- Overlay stickiness: the traffic prefers to stay within the same overlay end-to-end

- Cross-overlay traffic is possible as last resort, via the Hub
  (e.g. if source CPE is connected only to Internet and target CPE - only to MPLS)

Internet Access:

- Direct Internet Access (DIA) from each Edge CPE, using 1st underlay only (Internet)

- Remote Internet Access (RIA) via Regional Hub, using overlays over 2nd underlay only (MPLS)

- Application-aware SD-WAN rules with different SLA targets per application

Plugins (optional):

- LAN behind Hubs:

  - IPSEC tunnels between Hubs of the same region (for Hub-to-Hub traffic only)

  - Cross-regional Spoke-to-Hub ADVPN shortcuts are enabled

- Hub-to-Edge traffic support with Remote SLA Probing ("Bi-directional SD-WAN")

  - **IMPORTANT:** This plugin is currently implemented only for a single-region topology

  - SLA measured by Edge CPEs and signaled to the Hubs by means of a special BGP community

  - This BGP community is then mapped to route-tag and used in SD-WAN rules on Hubs


## Topology 2: Interconnected Underlays

Requirements: FOS 6.4.5+

This base topology includes two interconnected underlay transport networks.
A typical example would be: two Internet links (e.g. two ISPs).

The topology is multi-regional, with arbitrary number of regions and Regional Hubs.

### Features:

Corporate Access (CPE to CPE):

- Full-mesh IPSEC overlays between Edge CPEs (Spokes) and each Regional Hub
  (hence, with 2 ISPs on CPE and Hub, each Edge CPE builds 4 IPSEC tunnels to each Hub)

- Full-mesh IPSEC overlays between Regional Hubs, over each underlay transport  

- IBGP sessions over each overlay (both within regions and between regions)

- ADVPN shortcuts are enabled within each overlay

- Cross-overlay ADVPN shortcuts are enabled (e.g. across different ISPs)

- Cross-regional ADVPN shortcuts are enabled

- The traffic prefers to flow via ADVPN shortcut, when possible

- Overlay stickiness: the traffic prefers to stay within the same overlay end-to-end

Internet Access:

- Direct Internet Access (DIA) from each Edge CPE, using the best of the available links
