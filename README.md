<meta property="og:image" content="https://avatars1.githubusercontent.com/u/8240809?v=2&amp;s=400" />
![pharos main logo](https://raw.githubusercontent.com/DockerKorea/pharos/master/docs/images/logo_horizontal.png)
--

pharos
======
pharos is a management tool to control and monitor 'Containers' of Docker(https://www.docker.com/) on a distributed cluster.

Main Features
  - 
  - An interface, provided as RESTful API by LightTower in order to monitor metrics (CPU, Memory, Disk I/O, Network I/O) of Container(s) of each process on a distributed system (These metrics are collected by LightKeeper).
    - Command Line Interface & Web Interface (not implemented yet: pharos web interface (https://github.com/DockerKorea/pharos-web)
  - An API wrapping pub&sub model (of ZeroMQ) for life cycle events such as start, die, kill and stop of Containers, and Alert event which is given as resources are used unormally out of thier limits set by users with the metrics.
      - For now, this function is under habby development and those life cycle events are broadcasted by Lighttower.

![pharos architecher](https://raw.githubusercontent.com/DockerKorea/pharos/master/docs/images/pharos-architecher.png)

#####pharos docker hub repository (https://registry.hub.docker.com/u/gopass2002/pharos)


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
daemon              : run lightkeeper daemons
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

#### Monitor Node Metrics
Monitor the summery of metrics being used by Containers running on nodes
```
$ bin/pharos top_node ubuntu-dev

RESOURCE USAGE SUMMARY
 HOSTNAME            : ubuntu-dev
 CONTAINERS          : 9
 CPU                 : 96.7% (user: 4.01% system: 7.36%)
 MEMORY              : 12.97% (rss: 1G vms: 3G)
 DISK IO             : read: 3G(0B/sec) write: 47M(0B/sec)
 NETWROK             : recv: 0B(0B/sec) sent: 6G(0B/sec)

   CONTAINER_ID                IMAGE                 NAME    CPU    MEM            DISK         NETWORK
     1d4deacc17               stress      /dreamy_meitner  15.2%  2.17%           0B/0B           0B/0B
     3bf9041389    gopass2002/pharos  /pharos-lightkeeper   4.9%   1.2%           0B/0B           0B/0B
     3fdb6c2926               stress        /jovial_mayer   0.0%   0.3%           0B/0B           0B/0B
     49dea14195               stress  /stupefied_lovelace  16.9%  1.33%           0B/0B           0B/0B
     5ed4e65d22               stress        /happy_wilson   0.0%  1.22%           0B/0B           0B/0B
     65c92d0ce8               stress      /focused_euclid  15.0%  1.49%           0B/0B           0B/0B
     66e3e7adc3               stress      /berserk_mclean  15.2%  1.65%           0B/0B           0B/0B
     76030a48af               stress   /nostalgic_feynman  14.3%  2.11%           0B/0B           0B/0B
     b95f1bbe89               stress     /furious_wozniak  15.2%  1.49%           0B/0B           0B/0B
     
```

#### Monitor Container Metrics
Monitor the metrics used by a certain Container (per process)
```
$ bin/pharos top_container ubuntu-dev 172c72072f03

CONTAINER RESOURCE USAGE SUMMARY
 CONTAINER ID        : 172c72072f033773261c91da544cbfb58e2d6238770989859bbfcd15f98e1c53
 PROCESSES           : 19
 CPU                 : 172.2% (user: 3.89% system: 3.54%)
 MEMORY              : 1.13% (rss: 90M vms: 417M)
 DISK IO             : read: 417M(0B/sec) write: 4M(0B/sec)
 NETWROK             : recv: 0B(0B/sec) sent: 116K(1K/sec)

PID    VIRT    RES     CPU%   MEM%   DISK I/O   NET I/O    TASKS COMMAND LINE
26491  17M     1M      0.0%   0.02%  0B/0B      0B/98B     1     bash
27056  6M      636K    0.0%   0.01%  0B/0B      0B/98B     1     ping 8.8.8.8
27329  12M     256K    0.0%   0.0%   0B/0B      0B/98B     1     nsenter-exec --nspid 26491 --console /dev/pts/9 -- bash
27330  17M     1M      0.0%   0.02%  0B/0B      0B/98B     1     bash
27434  7M      636K    0.0%   0.01%  0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27435  7M      100K    13.4%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27436  7M      100K    12.5%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27437  135M    83M     14.3%  1.05%  0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27438  7M      100K    11.6%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27439  7M      100K    12.5%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27440  135M    288K    10.8%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27441  7M      100K    10.8%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27442  7M      100K    12.5%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27443  7M      100K    11.7%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27444  7M      100K    12.6%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27445  7M      100K    11.7%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27446  7M      100K    11.7%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27447  7M      100K    13.5%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s
27448  7M      100K    12.6%  0.0%   0B/0B      0B/98B     1     stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 20s

CONTAINER INFOMATION
HOST      : ubuntu-dev           IMAGE     : stress
CREATED   : 2014-11-03 11:33:44  STARTED   : 2014-11-03 11:33:44
COMMAND   : bash
```
