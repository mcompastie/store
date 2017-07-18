# vNSF & NS Store

SHIELD aims to set up a single, centralised digital store for virtual Network Security Functions (vNSFs) and Network Services (NSs). This approach allows Service Providers to offer new security features for protecting the network or extend already existing functionalities without the need of modifying core elements of the framework. The store acts as a repository for vNSFs and NSs that have been previously published.

The Store onboards vNSFs/NSs in a secure and trusted way. The onboarding process will ensure the provenance is from a trusted source and that the contents integrity can be assured. Once this is achieved the security information is stored for safekeeping and provided upon request so other components can check that the vNSF/NS has not been tampered with since it was onboarded.

The onboarding process also verifies the vNSF and NS associated descriptors to ensure the instantiation process by an Orchestrator is performed without hassle. This encompasses the check of all the descriptors for inconsistencies and validation of the network topology defined within them to prevent issues such as unwanted loops in the forwarding graphs or reference to undefined networks or missing ports.

# Installation

## Prerequisites

* [Python 3](https://www.python.org/)
* [Eve REST API framework](http://eve.readthedocs.io/en/stable/) which provides (amongst other goodies) [Flask](http://flask.pocoo.org/) for RESTful support, [Cerberus](http://python-cerberus.org/) for JSON validation and [MongoDB](https://www.mongodb.com/) for the actual vNSF & NS data store.
* [PyYAML](http://pyyaml.org/) to handle vNSF and NS descriptors

## Python virtual environment

The [environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) requirements are defined in the [requirements.txt](docker/store-requirements.txt) file.

## Docker

### Prerequisites

Install the following packages and versions following the manuals:

* [Docker](https://docs.docker.com/engine/installation/) (17.06.0+)
* [docker-compose](https://docs.docker.com/compose/install/) (3.0+)

Alternatively, install them through the steps below:

```bash
sudo apt-get install --no-install-recommends apt-transport-https curl software-properties-common python-pip
curl -fsSL 'https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | sudo apt-key add -
sudo add-apt-repository "deb https://packages.docker.com/1.13/apt/repo/ubuntu-$(lsb_release -cs) main"
sudo apt-get update
sudo apt-get -y install docker-engine
sudo pip install docker-compose
```

Finally, add current user to the docker group (allows issuing Docker commands w/o sudo):
```
sudo usermod -G docker $(whoami)
```

### Setup

TL;DR

* Run it with:

```bash
cd docker
./run.sh
```

Once everything is up and running the last lines on the screen should be something like:
```python
dev_1         |  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
dev_1         |  * Restarting with stat
dev_1         |  * Debugger is active!
dev_1         |  * Debugger pin code: <XXX-XXX-XXX>
```

* First-time setup (from another terminal window):

```bash
docker exec -it docker_data-store_1 bash
./setup-datastore.sh --please
```

After the first-time setup is finished, you should see that Mongo has been successfully installed.

At this point, two containers should be running; namely the store and the mongo database:

```bash
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
420133c8e114        docker_dev          "/usr/share/dev/st..."   14 minutes ago      Up 10 minutes       0.0.0.0:5000->5000/tcp   docker_dev_1
bea2622e00d3        mongo               "docker-entrypoint..."   14 minutes ago      Up 10 minutes       27017/tcp                docker_data-store_1
```

Troubleshooting is possible after accessing the container through its name (last column from above): `docker exec -it $docker_container_name bash`

### Containers

To have a pain-free installation a [docker environment](https://www.docker.com/) is provided. This uses a [docker-compose](https://docs.docker.com/compose/overview/) file to provide the orchestration for the containers to setup.

Going a step further on easing up the installation process [environment variables](https://docs.docker.com/compose/environment-variables/#setting-environment-variables-with-docker-compose-run) are defined in the [.env](docker/.env) file. Any specific tailoring for the Store environment instantiation should be done here.

The downside of all this auto-magically environment instantiation is that the actual docker files get a bit harder to read and a [setup orchestrator script](docker/run.sh) needs to be put in place to fill in the proper data in the docker files according to the variables defined in the [.env](docker/.env) file. The outcome of all of this tweaking is that the docker files are created as templates ([docker-compose.yml.tmpl](docker/docker-compose.yml.tmpl), [Dockerfile.datastore.tmpl](docker/Dockerfile.datastore.tmpl), [Dockerfile.dev.tmpl](docker/Dockerfile.dev.tmpl)) and the orchestrator script ([run.sh](docker/run.sh)) produces the proper docker files, builds them up and runs the containers so the Store is up and running.

### First-time setup

The first time the Store environment is set up one must create the data store to hold the vNSF & NS data for the Store. This is done by the [setup-datastore.sh](docker/setup-datastore.sh) script and the steps required are mentioned above.

# Deployment

The default settings deploy the Store API in the localhost and running on port 5000. To ensure the environment is up and running place a `GET` request to http://localhost:5000. The response should be a `200 OK` with the available endpoints presented in either XML:

```xml
<resource>
    <link rel="child" href="vnsfs/attestation" title="vnsfs/attestation"/>
    <link rel="child" href="vnsfs" title="vnsfs"/>
</resource>
```

or JSON format if the `Accept: application/json` HTTP header is set:

```json
{
    "_links": {
        "child": [{
                "href": "vnsfs",
                "title": "vnsfs"
            },
            {
                "href": "vnsfs/attestation",
                "title": "vnsfs/attestation"
            }
        ],
    }
}
```

# API Documentation

The documentation follows the [OpenAPI Specification](https://swagger.io/specification/) (fka Swagger RESTful API Documentation Specification) Version 2.0 and is defined in the [swagger.yaml](swagger.yaml) file. To have it in a user-friendly way simple paste its contents into the [Swagger Editor](https://editor.swagger.io/) and navigate the documentation Swagger style.

# Packaging

## vNSF Packaging

Please head to [vNSF Packaging](docs/vnsf/packaging.md) to understand how to package a vNSF for submission to the Store.

# Further reading

Please refer to the [Store documentation](docs/index.md) for additional insight on how the Store operates.
