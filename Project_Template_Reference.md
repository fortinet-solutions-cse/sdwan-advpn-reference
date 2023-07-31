# Project Template Reference

## Mandatory Parameters

These parameters must be configured for each project. Each parameter can be configured
simply as follows:

```
{% set <parameter> = <value> %}
```

The following table lists all the mandatory parameters:

| Parameter      |   Values    | Description                                                                              |     Example     |
|:---------------|:-----------:|:-----------------------------------------------------------------------------------------|:---------------:|
| lan_summary    | \<ip/mask\> | Subnet summarizing all corporate (internal) prefixes in the project                      |  '10.0.0.0/8'   |
| lo_summary     | \<ip/mask\> | Subnet summarizing all SD-WAN device loopbacks in the project _("BGP on Loopback" only)_ | '10.200.0.0/14' |
| tunnel_summary | \<ip/mask\> | A subnet summarizing all the tunnel subnets  in the project _("BGP per Overlay" only)_   | '10.200.0.0/14' |


## Regions

The `regions` dictionary describes all the regions in the project:

```
{# Regions #}
{% set regions = {
    'Region1': {
      {# Region1 parameters #}
    },
    'Region2': {
      {# Region2 parameters #}
    }
    {# ... #}
  }
%}
```

The following table lists all the parameters that must be configured for each region:

| Parameter   |    Values    | Description                                                                                                               |          Example           |
|:------------|:------------:|:--------------------------------------------------------------------------------------------------------------------------|:--------------------------:|
| as          |   \<asn\>    | Autonomous System number for the region                                                                                   |          '65001'           |
| lan_summary | \<ip/mask\>  | Subnet summarizing all corporate prefixes in the region _(not for Multi-VRF flavor and only when multireg_advpn = false)_ |       '10.0.0.0/14'        |
| lo_summary  | \<ip/mask\>  | Subnet summarizing all SD-WAN device loopbacks in the region _("BGP on Loopback" only)_                                   |      '10.200.1.0/24'       |
| hubs        | \<str list\> | List of Hubs serving the region*                                                                                          | [ 'site1-H1', 'site1-H2' ] |

\* - The Hub names referenced here must correspond to the Hubs defined [below](#hubs)


#### Additional parameters for the Multi-VRF flavor

| Parameter |    Values     | Description                                                                                   | Default |
|:----------|:-------------:|:----------------------------------------------------------------------------------------------|:-------:|
| pe_vrf    |    \<int\>    | ID of the VRF that will be used as the PE (transport) VRF, default for underlays and overlays |   32    |
| vrfs      | \<dict list\> | List of all the VRFs that will be used as CE (customer) VRFs in that region*                  |   [ ]   |

\* Each VRF is described by a dict with the following parameters:

| Parameter   |   Values    | Description                                                                                               |    Example    |
|:------------|:-----------:|:----------------------------------------------------------------------------------------------------------|:-------------:|
| id          |   \<int\>   | VRF ID                                                                                                    |       1       |
| lan_summary | \<ip/mask\> | Subnet summarizing all corporate prefixes in the region for this VRF _(only when multireg_advpn = false)_ | '10.0.0.0/14' |


## Profiles

The `profiles` dictionary describes all the device profiles in the project.
By device profiles we mainly mean the list of interfaces for each site,
with the respective options for each interface. Thus, the profile describes the
local topology and the connectivity options for each site:

```
{# Device Profiles #}
{% set profiles = {
    'Profile1': {
      'interfaces': [
        {
          {# Interface1 parameters #}
        },
        {
          {# Interface2 parameters #}
        }
        {# ... #}
      ]
    },
    'Profile2': {
      'interfaces': [
        {
          {# Interface1 parameters #}
        },
        {
          {# Interface2 parameters #}
        }
        {# ... #}
      ]
    }
    {# ... #}
  }
%}
```

NOTE: All the Edge devices and the Hubs must be assigned a profile!

Apart from the list of interfaces, the profile can also specify that a device is in HA cluster mode:

| Parameter | Values | Description                           | Example |
|:----------|:------:|:--------------------------------------|:-------:|
| ha        |  true  | Device is in HA cluster _(optional)*_ |         |

\* - By default, the device is considered NOT in HA cluster. When in HA cluster, certain configuration 
     will be skipped (mainly, the hostname will not be set, since the FortiManager forbids changing device hostname in HA mode).

Example:

```
{# Device Profiles #}
{% set profiles = {
    'Profile1': {
      'ha': true,
      'interfaces': [
        {# List of interfaces #}
      ]
    }
%}
```

Each deployed SD-WAN site will be assigned a profile.

The following tables lists all the supported parameters that can be configured for
each device interface:

#### Parameters for all interfaces

| Parameter |           Values            | Description                                                        |        Example         |
|:----------|:---------------------------:|:-------------------------------------------------------------------|:----------------------:|
| name      |           \<str\>           | Interface name                                                     |        'port1'         |
| role      | 'wan' / 'lan' / 'sd_branch' | Interface role (respectively: WAN-facing / LAN-facing / Fortilink) |                        |
| ip        |    \<ip/mask\> / 'dhcp'     | Interface IP address (with mask) / Enable DHCP client              | '10.0.1.1/24' / 'dhcp' |
| vlanid    |           \<int\>           | VLAN ID (for VLAN interfaces, _optional_)                          |          '10'          |
| parent    |           \<str\>           | Parent interface (for VLAN interfaces, _when vlan_id is set_)      |        'port1'         |
| access    |           \<str\>           | Custom list of services to allow access (such as FGFM, _optional_) |   'ping fgfm https'    |


#### Additional parameters for WAN-facing interfaces

| Parameter       | Values  | Description                                            |    Example     |
|:----------------|:-------:|:-------------------------------------------------------|:--------------:|
| ol_type         | \<str\> | Overlay to connect to over this interface*             |     'ISP1'     |
| ul_name         | \<str\> | Local underlay transport name _(optional)_             |     'ISP1'     |
| outbandwidth    | \<int\> | Total egress bandwidth _(optional)_                    |     '8000'     |
| inbandwidth     | \<int\> | Total ingress bandwidth _(optional)_                   |     '8000'     |
| shaping_profile | \<str\> | Shaping profile to apply _(optional)_                  | 'Edge_Shaping' |
| dia             |  true   | Interface used for Direct Internet Access _(optional)_ |                |

\* - The overlay types referenced here must correspond to those defined in the Hub dictionary [below](#hubs)


#### Additional parameters for LAN-facing interfaces

| Parameter | Values | Description                                 | Example |
|:----------|:------:|:--------------------------------------------|:-------:|
| advertise | false  | Advertise the prefix into BGP _(optional)*_ |         |

\* - By default, all the LAN-facing prefixes are advertised into BGP.


#### Additional parameters for the Multi-VRF flavor

| Parameter     | Values  | Description                                                                    |  Example   |
|:--------------|:-------:|:-------------------------------------------------------------------------------|:----------:|
| vrf           | \<int\> | VRF ID for this interface (CE VRF, for LAN-facing only) _(optional)_           |     1      |
| allow_dia     |  true   | Allow Internet access from this CE VRF* (for LAN-facing only) _(optional)_     |            |
| leak_npu_link | \<str\> | Name of the npu_link interface to create VRF leaking interfaces** _(optional)_ | 'npu_link' |

\* - We provide Internet access for CE VRFs by configuring VRF leaking into the PE VRF (where all underlays and overlays are located).
\*\* - Leave empty for VM and non-ASIC models in order to use software VDOM links.


### Overlay tunnel naming convention

An overlay tunnel will be generated from each WAN-facing interface in the Edge device profile to each Hub 
serving the device region. The target overlay (to which the tunnel will connect) is defined by the 
`ol_type` parameter. The default naming convention for the generated tunnels on the Edge device is:

```
H<hub_index>_<ol_type>
```

Optionally, a local underlay transport name can be added. This happens automatically, if the `ul_name` 
parameter is defined. The naming convention then becomes:

```
<ul_name>-H<hub_index>_<ol_type>
```

On the Hub side, the Dial-Up overlays are generated with the following naming convention:

```
EDGE_<ol_type>
```


## Hubs

The `hubs` dictionary describes all the Hubs serving the project:

```
{# Hubs #}
{% set hubs = {
    'hub1': {
      {# hub1 parameters #}
      'overlays': {
        'ol_type_1': {
          {# ol_type_1 parameters #}
        },
        'ol_type_2': {
          {# ol_type_2 parameters #}        
        }
        {# ... #}
      }
    },
    'hub2': {
      {# hub2 parameters #}
      'overlays': {
        'ol_type_1': {
          {# ol_type_1 parameters #}
        },
        'ol_type_2': {
          {# ol_type_2 parameters #}        
        }
        {# ... #}
      }
    }
    {# ... #}    
  }
%}
```

For each Hub, the following parameters must be defined:

| Parameter | Values | Description                          |    Example     |
|:----------|:------:|:-------------------------------------|:--------------:|
| lo_bgp    | \<ip\> | Loopback IP used for BGP termination | '10.200.1.253' |

Next, for each Hub, the `overlays` list will describe all the overlays terminated
on that Hub.

NOTE: These are the overlays referenced using `ol_type` parameter in the device profiles.
The Edge devices will build IPSEC tunnels to these overlays, using the information
defined here.

The following parameters must be defined for each overlay:

| Parameter  |   Values    | Description                                    |     Example     |
|:-----------|:-----------:|:-----------------------------------------------|:---------------:|
| wan_ip     |   \<ip\>    | Endpoint IP for the IPSEC tunnel               |  '100.64.2.1'   |
| network_id |   \<int\>   | IKEv2 Network ID for the IPSEC tunnel          |      '21'       |
| tunnel_net | \<ip/mask\> | IPSEC tunnel subnet _("BGP per Overlay" only)_ | '10.201.2.0/24' |


## Optional Parameters

These parameters can be optionally configured in the Project template.
They can be used to tweak the solution without manually editing the CLI Templates.

Each parameter can be configured simply as follows:

```
{% set <parameter> = <value> %}
```

The following table lists all the supported parameters, as well as their default values (applied when
they are not configured explicitly):

| Parameter              |    Values    | Description                                                                                   |      Default      |
|:-----------------------|:------------:|:----------------------------------------------------------------------------------------------|:-----------------:|
| create_hub2hub_zone    | true / false | Create System Zone for inter-regional Hub-to-Hub tunnels                                      |       true        |
| hub2hub_zone           |   \<str\>    | Name of System Zone for inter-regional Hub-to-Hub tunnels _(when create_hub2hub_zone = true)_ | 'hub2hub_overlay' |
| create_lan_zone        | true / false | Create System Zone for LAN interfaces (with 'role' = 'lan' in the profile)                    |       true        |
| lan_zone               |   \<str\>    | Name of System Zone for LAN interfaces _(when create_lan_zone = true)_                        |    'lan_zone'     |
| create_lan_dhcp_server | true / false | Configure DHCP Servers on LAN interfaces                                                      |       true        |
| cert_auth              | true / false | Certificate-based auth for IKE/IPSEC                                                          |       true        |
| hub_cert_template      |   \<str\>    | Certificate name on Hubs _(when cert_auth = true)_                                            |       'Hub'       |
| edge_cert_template     |   \<str\>    | Certificate name on Edge _(when cert_auth = true)_                                            |      'Edge'       |
| psk                    |   \<str\>    | Pre-shared secret for IKE/IPSEC _(when cert_auth = false)_                                    |     'S3cr3t!'     |
| overlay_stickiness     | true / false | Generate "overlay stickiness" policy routes on the Hubs _("BGP on Loopback" only)_            |       true        |
| intrareg_hub2hub       | true / false | Build intra-regional Hub-to-Hub tunnels for DC-to-DC traffic _("BGP on Loopback" only)_       |       false       |
| intrareg_advpn         | true / false | Enable ADVPN within each region                                                               |       true        |
| multireg_advpn         | true / false | Extend ADVPN across the regions                                                               |       false       |
| hub_hc_server          |    \<ip\>    | Health server IP on the Hubs (set on Lo-HC interface on the Hubs, probed by Edges)            |   '10.200.99.1'   |


#### Additional parameters for the Multi-VRF flavor

| Parameter            |    Values    | Description                                                                                            |      Default      |
|:---------------------|:------------:|:-------------------------------------------------------------------------------------------------------|:-----------------:|
| create_vrf_leak_zone | true / false | Create System Zones for VRF leaking interfaces for easier management of Internet access                |       true        |
| vrf_leak_zone        |   \<str\>    | Name of System Zone for all CE VRF ends of the leaking interfaces _(when create_vrf_leak_zone = true)_ | 'vrfs_leak_zone'  |
| pevrf_leak_zone      |   \<str\>    | Name of System Zone for all PE VRF ends of the leaking interfaces _(when create_vrf_leak_zone = true)_ | 'pevrf_leak_zone' |
| vrf_leak_summary     |    \<ip\>    | Subnet used for VRF leaking interfaces, with local significance only                                   | '10.200.255.0/24' |
| vrf_rt_as            |   \<asn\>    | Fictitious Autonomous System number used in MP-BGP RD/RT values (_has local significance only_)        |      '65000'      |

## Setting Per-Device Context

On the most important tasks when onboarding a new device will be to assign it to the
right region and the device profile, selecting one of the objects described in the Project template.

This assignment can be done using FortiManager ADOM variables `region` and `profile` respectively.

Apart from these two variables, several other per-device variables are used inside the provided
templates set, and hence it is important to set their values.

Finally, several parameters described in this reference will typically have different values for different sites.
Consider, for example, the IP address parameter under the device profile.
Each device will have its own IP address, while the Project template remains the same.

FortiManager ADOM variables can also be used to solve this problem. Any per-device value should be defined
as a variable, which can be then referred in the Project template. For example,
the following snippet will use the variable `lan_ip` to statically define different IP address
for each rendered device:

```
{# Device Profiles #}
{% set profiles = {
    'Silver': {
      'interfaces': [
        {
          'name': 'port5',
          'role': 'lan',
          'ip': lan_ip
        }
      ]
    },
  }
%}
```

To summarize, when onboarding a new device, the following three types of variables must be set:

1. The variables `region` and `profile`, correctly classifying the device in the project

1. The variables implicitly used by the provided templates

1. The variables explicitly used in your Project template

The following table summarizes the required per-device variables, except for the last category (which, of course, depends on your Project Template):

| Parameter        | Values      | Description                                                            | Example        |
|------------------|-------------|------------------------------------------------------------------------|----------------|
| region           | \<str\>     | One of the regions defined in Project template                         | 'West'         |
| profile          | \<str\>     | One of the profiles defined in Project template                        | 'Silver'       |
| hostname         | \<str\>     | Device hostname                                                        | 'site1-1'      |
| loopback         | \<ip\>      | Device main loopback IP                                                | '10.200.1.1'   |

The following table summarizes the required per-device variables from the last category, using the most complex Project Template provided in the examples folder
(`Project.dualreg.cert.j2`):

| Parameter        | Values      | Description                                                                    | Example        |
|------------------|-------------|--------------------------------------------------------------------------------|----------------|
| lan_ip           | \<ip/mask\> | LAN interface IP (and mask) _(only in 'Project.dualreg.cert.j2')_              | '10.0.1.1/24'  |
| mpls_wan_ip      | \<ip/mask\> | MPLS interface IP (and mask) _(only in 'Project.dualreg.cert.j2')_             | '172.16.0.1/2  |
| mpls_wan_gateway | \<ip\>      | Next-hop gateway for MPLS transport _(only in 'Project.dualreg.cert.j2')_      | '172.16.0.2'   |
| outbandwidth     | \<int\      | Egress WAN bandwidth _(only in 'Project.dualreg.cert.j2')_                     | '8000'         |
| inbandwidth      | \<int\      | Ingress WAN bandwidth _(only in 'Project.dualreg.cert.j2')_                    | '8000'         |
| shaping_profile  | \<str\      | Shaping profile to apply to WAN underlay _(only in 'Project.dualreg.cert.j2')_ | 'Edge_Shaping' |
