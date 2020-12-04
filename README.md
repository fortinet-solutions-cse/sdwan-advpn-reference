# Reference Configuration: SD-WAN with ADVPN on FOS 6.4.x

## Topology1: Separate Underlays

This base topology includes two separate underlay transport networks.
A typical example would be: Internet and MPLS.

The topology is multi-regional, with arbitrary number of regions and Regional Hubs.

### Features:

Corporate Access (CPE to CPE):

- Separate IPSEC overlay between Edge CPEs (Spokes) and each Regional Hub, over each underlay transport
  (hence, with 2 underlays + 2 Regional Hubs, each Edge CPE builds 4 IPSEC tunnels)

- Full-mesh IPSEC overlays between Regional Hubs, over each underlay transport  

- ADVPN shortcuts are enabled within each overlay

- ADVPN shortcuts are not possible between different overlays (e.g. between Internet and MPLS)

- Cross-regional ADVPN shortcut are enabled

- The traffic prefers to flow via ADVPN shortcut, when possible

- Overlay stickiness: the traffic prefers to stay within the same overlay end-to-end

- Cross-overlay traffic is possible as last resort, via the Hub
  (e.g. if source CPE is connected only to Internet and target CPE - only to MPLS)

Internet Access:

- Direct Internet Access (DIA) from each Edge CPE, using 1st underlay only (Internet)

- Remote Internet Access (RIA) via Regional Hub, using overlays over 2nd underlay only (MPLS)

- Application-aware SD-WAN rules with different SLA targets per application
