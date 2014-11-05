<meta property="og:image" content="https://avatars1.githubusercontent.com/u/8240809?v=2&amp;s=400" />
![pharos main logo](https://raw.githubusercontent.com/DockerKorea/pharos/master/docs/images/logo_horizontal.png)
--

pharos
======
pharos is a management tool to control and monitor 'Containers' of Docker(https://www.docker.com/) on a distributed cluster.

##### Main Features
  - An interface, provided as RESTful API by LightTower in order to monitor metrics (CPU, Memory, Disk I/O, Network I/O) of Container(s) of each process on a distributed system (These metrics are collected by LightKeeper).
    - Command Line Interface & Web Interface (not implemented yet: pharos web interface (https://github.com/DockerKorea/pharos-web)
  - An API wrapping pub&sub model (of ZeroMQ) for life cycle events such as start, die, kill and stop of Containers, and Alert event which is given as resources are used unormally out of thier limits set by users with the metrics.
      - For now, this function is under habby development and those life cycle events are broadcasted by Lighttower.

![pharos architecher](https://raw.githubusercontent.com/DockerKorea/pharos/master/docs/images/pharos-architecher.png)

#####pharos docker hub repository (https://registry.hub.docker.com/u/gopass2002/pharos)

---

#### requirements
- mongodb

#### Installation

```
$ git clone https://github.com/DockerKorea/pharos.git
$ cd pharos    
$ python setup.py install  
# or (The install way above might not work appropriately. 
#      So, please use environment variables in order to install it.)
$ pip install -r requirements.txt
$ export PYTHONPATH=<Pharos home dir>/src/python
$ export PATH=<Pharos home dir>/bin
```

#### configuration
```
$ cp etc/pharos_config_sample.yml ~/pharos-conifg.yml
$ export PHAROS_CONFIG=~/pharos-config.yml 
$ vi ~/pharos-config.yml 

# edit this
pharos:
    metrics_collect_interval: 1    # The period of collecting metrics of Containers
    storage_type: mongodb    # Storage type (MongoDB only for now)
    lighttower:    # LightTower configuration
        lighttower_host: localhost    # Host for LightTower
        lgihttower_event_boradcast_port: 4242    # Port to broadcast events
        lighttower_event_collect_port: 4343     # Port to collect events from LightKeeper
        lighttower_remote_api_port: 4444    # REST API port

    lightkeeper:    # LightKeeper configuration
        lightkeeper_rpc_port: 5555    # LigjtKeeper RPC Server configuration (deprecated)

docker:    # Docker daemon configurations of each node
    docker_bridge_ip: 172.17.42.1    # Bridge IP used by Docker Containers
    docker_unix_socket_path: /var/run/docker.sock    # Unix socket path of Docker remote API
    docker_remote_api_port: 2375    # TCP port of Docker remote API
    docker_api_version: v1.14    # Version of Docker remote API

mongodb:    # MongoDB configurations of each node
    mongos_port: 27017    # mongos port which can be connected from outside.

```

#### Command Line Interface
A tool providing basic operations of pharos
```
$ bin/pharos

Usage: pharos COMMAND [arg...]

Commands:
run              : run lightkeeper daemons
add_node            : add node
top_container       : display <host> <container> metrics
top_node            : display <host> node metrics
remove_node         : remove node
nodes               : list nodes
containers          : list containers
```

## RUN
MongoDB should be installed to run pharos and its configuration should be set appropriatly.

#### Run LightTower
LightTower has to be run first to use CLI, web interface of pharos as it uses LightTower RESTful API
```
$ bin/lighttower
start monitor
 * Running on http://0.0.0.0:4444/
```
#### Add Node
Add a node to monitor.
```
$ bin/pharos add_node ubuntu-dev
5457646d1ba8895140f07775
$ bin/pharos nodes
-----------------------------------------------------------------------------------------------------
ID                             HOSTNAME             DOCKER     STORAGE    CONTAINERS   IP
-----------------------------------------------------------------------------------------------------
5457646d1ba8895140f07775       ubuntu-dev           OK         OK         1            127.0.1.1
```

#### Run LightKeeper
Start LightKeeper to collect metrics of Containers

```
$ bin/pharos daemon ubuntu-dev
starting lightkeeper at ubuntu-dev
successfully start lightkeeper
```

#### List Containers
List containers
```
containers
CONTAINER ID    IMAGE                                      COMMNAD                      STATUS      NAMES                        HOST
0e373b8a5b24    ubuntu                                     "ping 8.8.8.8"               running     /grave_elion                 ubuntu-dev
2a0855496d3c    stress                                     "bash "                      running     /berserk_bell                ubuntu-dev
9c6f047d0ccd    gopass2002/pharos                          "/bin/sh -c /pharos/bin/l    running     /pharos-lightkeeper          ubuntu-dev
```

#### Monitor Node Metrics
Monitor the summery of metrics being used by Containers running on nodes
```
$ bin/pharos top_node ubuntu-dev

RESOURCE USAGE SUMMARY
 HOSTNAME            : ubuntu-dev
 CONTAINERS          : 3
 CPU                 : 1.8% (user: 0.05% system: 0.19%)
 MEMORY              : 0.99% (rss: 79M vms: 550M)
 DISK IO             : read: 550M(0B/sec) write: 10M(0B/sec)
 NETWROK             : recv: 0B(0B/sec) sent: 221G(72K/sec)

   CONTAINER_ID                          IMAGE                           NAME    CPU    MEM            DISK         NETWORK
     0e373b8a5b                         ubuntu                    grave_elion   0.0%  0.01%           0B/0B          0B/98B
     2a0855496d                         stress                   berserk_bell   0.0%  0.05%           0B/0B           0B/0B
     9c6f047d0c              gopass2002/pharos             pharos-lightkeeper   1.8%  0.93%           0B/0B          0B/72K
     
```

#### Monitor Container Metrics
Monitor the metrics used by a certain Container (per process)
```
$ bin/pharos top_container 2a0855496d

CONTAINER RESOURCE USAGE SUMMARY
 CONTAINER ID        : 2a0855496d3ccd55dd8d0566aae6ddccc85a3419ddb22d3a7be5a671aa0fe7f7
 PROCESSES           : 18
 CPU                 : 137.8% (user: 0.06% system: 0.08%)
 MEMORY              : 2.53% (rss: 201M vms: 411M)
 DISK IO             : read: 411M(0B/sec) write: 6M(0B/sec)
 NETWROK             : recv: 0B(0B/sec) sent: 152M(0B/sec)

PID    VIRT    RES     CPU%   MEM%   TASKS COMMAND LINE
6464   12M     256K    0.0%   0.0%   1     nsenter-exec --nspid 30858 --console /dev/pts/13 -- bash
6466   17M     1M      0.0%   0.02%  1     bash
12350  7M      636K    0.0%   0.01%  1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12351  7M      100K    19.1%  0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12352  7M      100K    6.9%   0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12353  135M    92M     7.8%   1.16%  1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12354  7M      100K    6.9%   0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12355  7M      100K    7.8%   0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12356  135M    102M    7.8%   1.29%  1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12357  7M      100K    6.9%   0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12358  7M      100K    7.8%   0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12359  7M      100K    6.9%   0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12360  7M      100K    6.9%   0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12361  7M      100K    19.1%  0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12362  7M      100K    7.8%   0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12363  7M      100K    7.0%   0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
12364  7M      100K    19.1%  0.0%   1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 50s
30858  17M     1M      0.0%   0.02%  1     bash

CONTAINER INFOMATION
HOST      : ubuntu-dev           IMAGE     : stress
CREATED   : 2014-11-05 07:39:05  STARTED   : 2014-11-05 07:39:05
COMMAND   : bash
```
