# Supported Features

## Scope of configuration:

- Native support of heterogenous deployments (sites with different connectivity)
- Underlay interfaces and general device settings
- Overlay tunnels (within and between regions)
- Overlay routing (within and between regions)
- [Optional] SD-WAN configuration (recommended only when using without FortiManager)
- [Optional] Firewall Policies (recommended only when using without FortiManager)

## Underlay options:

- DHCP and static IP
- VLAN tagging
- FEX support
- FortiLink (SD-Branch) support
- DHCP Server for LAN clients
- DHCP Relay for LAN clients
- Underlay Loopback (dedicated source IP for all local-out traffic, e.g. routable public IP or provider-independent IP)

## List of supported overlay network designs:

- BGP on Loopback
- BGP per Overlay

## Overlay topology options:

- Single-regional and multi-regional
- ADVPN within and between regions
- Hub-to-Hub tunnels within and between regions
- Spoke-to-Hub connectivity options: One-to-One, Many-to-One and Full-Mesh
- IPSEC authentication: certificate-based and PSK 
- Redundant IPSEC tunnels ("monitor" feature)
- Overlay stickiness

## Other features:

- Multi-VRF (“Segmentation over Single Overlay”), including Internet access
- Automatic System Zone creation for FW policies
- QoS: ingress/egress shaping profile 