# Reference Configuration: SD-WAN with ADVPN on FOS 6.4.x

## Base1: Separate Underlays

This base topology includes two separate underlay transport networks.
A typical example would be: Internet and MPLS.

### Features:

Corporate Access (CPE to CPE):

- Separate IPSEC overlay between Edge CPEs (Spokes) and each Regional Hub, over each underlay transport
  (hence, with 2 underlays + 2 Regional Hubs, each Edge CPE builds 4 IPSEC tunnels)

- ADVPN shortcuts are enabled within each overlay

- ADVPN shortcuts are not possible between different overlays (e.g. between Internet and MPLS)

- The traffic prefers to flow via ADVPN shortcut, when possible

- Overlay stickiness: the traffic prefers to stay within the same overlay end-to-end

- Cross-overlay traffic is possible as last resort, via the Hub
  (e.g. if source CPE is connected only to Internet and target CPE - only to MPLS)

Internet Access:

- Direct Internet Access (DIA) from each Edge CPE

- Remote Internet Access (RIA) via Regional Hub over one of the underlays (e.g. MPLS)

- Application-aware SD-WAN rules with different SLA targets per application
