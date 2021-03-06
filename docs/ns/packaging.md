# Network Service Packaging

## Contents


### Elements

To foster Network Service reuse and remove SHIELD applicability barriers the SHIELD Network Service package format extends existing formats by introducing:

* a digitally-signed security manifest to prove provenance and integrity
* support for including Orchestrator-specific Network Service package format
* a .tar.gz package format to enclose everything

A SHIELD Network Service package (`.tar.gz` file) comprises:

| Element | Format | Purpose |
|-|-|-
| manifest.yaml | YAML | Security manifest which defines the tamper-proof metadata to ensure the Network Service in operation wasn't tampered with since when it was onboarded
| *&lt;ns_package_file\>* | Orchestrator specific | The Network Service package to onboard into the Network Service Orchestrator

### Structure

The structure of a SHIELD Network Service package is as follows:

```bash
.
├── manifest.yaml           # SHIELD security manifest
└── <ns_package_file>       # Orchestrator-specific Network Service package
```

This packaging is Orchestrator agnostic and allows for onboarding an existing Network Services into SHIELD simply by providing a security manifest tailored to the Network Service in question. Once this is done it is just a matter of producing a .tar.gz file with the contents mentioned and submit it to the Store.

### Datamodel

#### Security manifest (`manifest.yaml`)

**Elements**

| Field | Purpose |
|-|-
| manifest:ns | Defines a SHIELD Network Service package
| schema_version | Identifies the version of the manifest descriptor schema that is used to describe the shield package.
| type | The type of Network Service the manifest describes. Allowed values: `OSM`
| package | Network Service file name within the SHIELD package. This file name, contents and format is Orchestrator specific. This manifest only identifies the file which holds the Network Service package
| hash | The message digest for the NS package mentioned in the package field
| descriptor | Network Service Descriptor file within the Network Service-specific package. Tipically a path to the actual file itself
| properties | Network Service characterization and purpose-related details

**Example**

```yaml
manifest:ns:
    schema_version: '1.2'
    type: OSM
    package: cirros_ns.tar.gz
    descriptor: cirros_ns/cirros_nsd.yaml
    properties:
        capabilities: ['Virtual Cirr OS']
```

## Examples


### OSM Network Service packaging

#### Elements

The SHIELD Network Service package is a wrapper that contains the following elements, marked as *(M)*andatory or *(O)*ptional:

Element | Contents | Source
-|-|-
manifest.yaml | (M) package contents definition along with the security information | SHIELD
*&lt;ns_name\>*_nsd.yaml | (M) Network Service descriptor information. Follows the [OSM Information Model](https://osm.etsi.org/wikipub/images/2/26/OSM_R2_Information_Model.pdf) (page 12) | OSM
checksums.txt | (M) image file(s) hash(es) | OSM
icons | (O) used on the OSM Composer | OSM
README | (O) Network Service related information | OSM

#### Structure

The structure of a SHIELD Network Service package is as follows:

```bash
.
├── manifest.yaml           # SHIELD
└── <ns_name>.tar.gz        # OSM Network Service package
```

The structure of the OSM Network Service package is:

```bash
.
├── <ns_name>_ns              # OSM
    ├── checksums.txt         # OSM
    ├── icons                 # OSM
    ├── README                # OSM
    └── <ns_name>_nsd.yaml    # OSM
```

#### Example

**Security manifest** (`manifest.yaml`)

```yaml
manifest:ns:
    schema_version: '1.2'
    type: OSM
    package: cirros_ns.tar.gz
    descriptor: cirros_ns/cirros_nsd.yaml
    properties:
        capabilities: ['Virtual Cirr OS']```

**OSM Network Service Descriptor** (`cirros_nsd.yaml`)

```yaml
nsd:nsd-catalog:
    nsd:
    -   id: cirros_nsd
        name: cirros_ns
        short-name: cirros_ns
        description: Generated by OSM pacakage generator
        vendor: OSM
        version: '1.0'

        # Place the logo as png in icons directory and provide the name here
        logo: osm_2x.png

        # Specify the VNFDs that are part of this NSD
        constituent-vnfd:
            # The member-vnf-index needs to be unique, starting from 1
            # vnfd-id-ref is the id of the VNFD
            # Multiple constituent VNFDs can be specified
        -   member-vnf-index: 1
            vnfd-id-ref: cirros_vnfd
        scaling-group-descriptor:
        -   name: "scaling_cirros"
            vnfd-member:
            -   count: 1
                member-vnf-index-ref: 1
            min-instance-count: 0
            max-instance-count: 10
            scaling-policy:
            -   scaling-type: "manual"
                cooldown-time: 10
                threshold-time: 10
                name: manual_scale
        vld:
        # Networks for the VNFs
            -   id: cirros_nsd_vld1
                name: cirros_nsd_vld1
                type: ELAN
                # vim-network-name: <update>
                # provider-network:
                #     overlay-type: VLAN
                #     segmentation_id: <update>
                vnfd-connection-point-ref:
                # Specify the constituent VNFs
                # member-vnf-index-ref - entry from constituent vnf
                # vnfd-id-ref - VNFD id
                # vnfd-connection-point-ref - connection point name in the VNFD
                -   nsd:member-vnf-index-ref: 1
                    nsd:vnfd-id-ref: cirros_vnfd
                    # NOTE: Validate the entry below
                    nsd:vnfd-connection-point-ref: eth0
```

#### SHIELD Package Generation

TBD
