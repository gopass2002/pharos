#pharos RESTful API

##### query node list
` GET /nodes `

모든 노드의 리스트를 조회

**Example request:**

```
GET /nodes HTTP/1.1
```

**Example response**
```
HTTP/1.0 200 OK
Content-Type: application/json

{
  "n": 1,
  "nodes": [
    {
      "_id": "545ca47d1ba8890fc20a19cc",
      "containers": 3,
      "host": "ubuntu-dev",
      "storage": true
    }
  ]
}
```
---

##### query node metics
` GET /nodes/<hostname>/metrics `

`hostname`의 metrics정보를 조회


**Example request:**

```
GET /nodes HTTP/1.1
```

**Example response**
```
HTTP/1.0 200 OK
Content-Type: application/json

{
  "Containers": [
    {
      "Command": [
        "/bin/sh",
        "-c",
        "exec docker-registry"
      ],
      "Created": "2014-11-06T05:44:45.492745708Z",
      "Host": "ubuntu-dev",
      "Id": "4f74b38bebe8049adf734c168ba877a7851ca3e8de6abc3c80f096c4d9947a8d",
      "Image": "registry",
      "Metrics": [
        0.0,
        2.85,
        13.709999999999999,
        1.6788528621457326,
        140574720.0,
        455532544.0,
        22114304.0,
        176402432.0,
        179765349.0,
        2230453.0
      ],
      "Name": "/evil_mccarthy",
      "Processes": [
        {
          "cmdline": [
            "/usr/bin/python",
            "/usr/local/bin/gunicorn",
            "--access-logfile",
            "-",
            "--error-logfile",
            "-",
            "--debug",
            "--max-requests",
            "100",
            "-k",
            "gevent",
            "--graceful-timeout",
            "3600",
            "-t",
            "3600",
            "-w",
            "4",
            "-b",
            "0.0.0.0:5000",
            "docker_registry.wsgi:application"
          ],
          "connections": [],
          "exe": "/usr/bin/python2.7",
          "metrics": [
            0.0,
            0.5,
            1.25,
            0.3800410223196444,
            31821824,
            99745792,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "gunicorn",
          "num_threads": 1,
          "open_files": [],
          "pid": 3070,
          "status": "sleeping"
        },
        {
          "cmdline": [
            "/usr/bin/python",
            "/usr/local/bin/gunicorn",
            "--access-logfile",
            "-",
            "--error-logfile",
            "-",
            "--debug",
            "--max-requests",
            "100",
            "-k",
            "gevent",
            "--graceful-timeout",
            "3600",
            "-t",
            "3600",
            "-w",
            "4",
            "-b",
            "0.0.0.0:5000",
            "docker_registry.wsgi:application"
          ],
          "connections": [],
          "exe": "/usr/bin/python2.7",
          "metrics": [
            0.0,
            0.46,
            1.25,
            0.379992104695456,
            31817728,
            99758080,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "gunicorn",
          "num_threads": 1,
          "open_files": [],
          "pid": 3071,
          "status": "sleeping"
        },
        {
          "cmdline": [
            "/usr/bin/python",
            "/usr/local/bin/gunicorn",
            "--access-logfile",
            "-",
            "--error-logfile",
            "-",
            "--debug",
            "--max-requests",
            "100",
            "-k",
            "gevent",
            "--graceful-timeout",
            "3600",
            "-t",
            "3600",
            "-w",
            "4",
            "-b",
            "0.0.0.0:5000",
            "docker_registry.wsgi:application"
          ],
          "connections": [],
          "exe": "/usr/bin/python2.7",
          "metrics": [
            0.0,
            0.49,
            1.26,
            0.379992104695456,
            31817728,
            99749888,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "gunicorn",
          "num_threads": 1,
          "open_files": [],
          "pid": 3074,
          "status": "sleeping"
        },
        {
          "cmdline": [
            "/usr/bin/python",
            "/usr/local/bin/gunicorn",
            "--access-logfile",
            "-",
            "--error-logfile",
            "-",
            "--debug",
            "--max-requests",
            "100",
            "-k",
            "gevent",
            "--graceful-timeout",
            "3600",
            "-t",
            "3600",
            "-w",
            "4",
            "-b",
            "0.0.0.0:5000",
            "docker_registry.wsgi:application"
          ],
          "connections": [],
          "exe": "/usr/bin/python2.7",
          "metrics": [
            0.0,
            0.47,
            1.25,
            0.3800410223196444,
            31821824,
            99766272,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "gunicorn",
          "num_threads": 1,
          "open_files": [],
          "pid": 3077,
          "status": "sleeping"
        },
        {
          "cmdline": [
            "/usr/bin/python",
            "/usr/local/bin/gunicorn",
            "--access-logfile",
            "-",
            "--error-logfile",
            "-",
            "--debug",
            "--max-requests",
            "100",
            "-k",
            "gevent",
            "--graceful-timeout",
            "3600",
            "-t",
            "3600",
            "-w",
            "4",
            "-b",
            "0.0.0.0:5000",
            "docker_registry.wsgi:application"
          ],
          "connections": [],
          "exe": "/usr/bin/python2.7",
          "metrics": [
            0.0,
            0.93,
            8.7,
            0.1587866081155317,
            13295616,
            56512512,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "gunicorn",
          "num_threads": 1,
          "open_files": [],
          "pid": 5465,
          "status": "sleeping"
        }
      ],
      "Started": "2014-11-06T05:44:45.724142141Z"
    },
    {
      "Command": [
        "/bin/sh",
        "-c",
        "/pharos/bin/lightkeeper"
      ],
      "Created": "2014-11-07T11:01:04.136528527Z",
      "Host": "ubuntu-dev",
      "Id": "b0c6eecae4daa061745c2665f0a50842d2b83fb1ef48757a3a7d30180a49f563",
      "Image": "gopass2002/pharos",
      "Metrics": [
        1.8,
        8.979999999999999,
        30.279999999999998,
        0.930951305929354,
        77950976.0,
        520167424.0,
        2015232.0,
        0.0,
        122821411550.0,
        3857874088.0
      ],
      "Name": "/pharos-lightkeeper",
      "Processes": [
        {
          "cmdline": [
            "/bin/sh",
            "-c",
            "/pharos/bin/lightkeeper"
          ],
          "connections": [],
          "exe": "/bin/dash",
          "metrics": [
            0.0,
            0.0,
            0.02,
            0.00797357274270846,
            667648,
            4550656,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "sh",
          "num_threads": 1,
          "open_files": [],
          "pid": 27101,
          "status": "sleeping"
        },
        {
          "cmdline": [
            "python",
            "/pharos/bin/lightkeeper"
          ],
          "connections": [
            [
              3,
              2,
              1,
              [
                "172.17.42.1",
                55465
              ],
              [
                "172.17.42.1",
                27017
              ],
              "ESTABLISHED"
            ]
          ],
          "exe": "/usr/bin/python2.7",
          "metrics": [
            0.0,
            0.44,
            5.93,
            0.33215066823920525,
            27811840,
            143101952,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "python",
          "num_threads": 1,
          "open_files": [],
          "pid": 27111,
          "status": "sleeping"
        },
        {
          "cmdline": [
            "python",
            "/pharos/bin/lightkeeper"
          ],
          "connections": [
            [
              3,
              2,
              1,
              [
                "172.17.42.1",
                55465
              ],
              [
                "172.17.42.1",
                27017
              ],
              "ESTABLISHED"
            ],
            [
              13,
              2,
              1,
              [
                "127.0.0.1",
                35518
              ],
              [
                "127.0.0.1",
                4343
              ],
              "ESTABLISHED"
            ],
            [
              11,
              2,
              1,
              [
                "172.17.42.1",
                60849
              ],
              [
                "172.17.42.1",
                2375
              ],
              "ESTABLISHED"
            ]
          ],
          "exe": "/usr/bin/python2.7",
          "metrics": [
            0.0,
            0.0,
            0.0,
            0.2942884271173871,
            24641536,
            229146624,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "python",
          "num_threads": 3,
          "open_files": [],
          "pid": 27117,
          "status": "sleeping"
        },
        {
          "cmdline": [
            "python",
            "/pharos/bin/lightkeeper"
          ],
          "connections": [
            [
              5,
              2,
              1,
              [
                "172.17.42.1",
                60848
              ],
              [
                "172.17.42.1",
                2375
              ],
              "ESTABLISHED"
            ],
            [
              3,
              2,
              1,
              [
                "172.17.42.1",
                55473
              ],
              [
                "172.17.42.1",
                27017
              ],
              "ESTABLISHED"
            ]
          ],
          "exe": "/usr/bin/python2.7",
          "metrics": [
            1.8,
            8.54,
            24.33,
            0.2965386378300533,
            24829952,
            143368192,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "python",
          "num_threads": 1,
          "open_files": [],
          "pid": 27118,
          "status": "running"
        }
      ],
      "Started": "2014-11-07T11:01:04.27876532Z"
    },
    {
      "Command": [
        "bash",
        "--login"
      ],
      "Created": "2014-11-06T06:11:34.711506374Z",
      "Host": "ubuntu-dev",
      "Id": "c16cb2c13c0b67ef9409b7f8eff0bffe8ec7fbab54576852e0a5101e3675c468",
      "Image": "master:5000/monitor",
      "Metrics": [
        0.0,
        0.02,
        0.1,
        0.024654482590951318,
        2064384.0,
        18599936.0,
        57315328.0,
        7962624.0,
        122821425845.0,
        3857888383.0
      ],
      "Name": "/stoic_babbage",
      "Processes": [
        {
          "cmdline": [
            "bash",
            "--login"
          ],
          "connections": [],
          "exe": "/bin/bash",
          "metrics": [
            0.0,
            0.02,
            0.1,
            0.024654482590951318,
            2064384,
            18599936,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "name": "bash",
          "num_threads": 1,
          "open_files": [],
          "pid": 13549,
          "status": "sleeping"
        }
      ],
      "Started": "2014-11-06T06:11:34.851602006Z"
    }
  ],
  "Host": "ubuntu-dev",
  "Metrics": [
    1.8,
    11.849999999999998,
    44.089999999999996,
    2.634458650666038,
    220590080.0,
    994299904.0,
    81444864.0,
    184365056.0,
    245822602744.0,
    7717992924.0
  ],
  "_id": "545ca670aaddcb5963a4e72b"
}
```

---

` GET /containers `

**Parameters**
* host: 호스트에 동작하는 container조회
* all: running상태 이외의 모든 상태의 container를 조회(true|false 기본 false)

**Example request:**

```
GET /containers?host=ubuntu-dev&status=all HTTP/1.1
```

**Example response**
```
HTTP/1.0 200 OK
Content-Type: application/json

{
  "containers": [
    {
      "Args": [
        "-c",
        "exec docker-registry"
      ],
      "Config": {
        "AttachStderr": false,
        "AttachStdin": false,
        "AttachStdout": false,
        "Cmd": [
          "/bin/sh",
          "-c",
          "exec docker-registry"
        ],
        "CpuShares": 0,
        "Cpuset": "",
        "Domainname": "",
        "Entrypoint": null,
        "Env": [
          "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
          "DOCKER_REGISTRY_CONFIG=/docker-registry/config/config_sample.yml",
          "SETTINGS_FLAVOR=dev"
        ],
        "ExposedPorts": {
          "5000/tcp": {}
        },
        "Hostname": "4f74b38bebe8",
        "Image": "registry",
        "Memory": 0,
        "MemorySwap": 0,
        "NetworkDisabled": false,
        "OnBuild": null,
        "OpenStdin": false,
        "PortSpecs": null,
        "SecurityOpt": null,
        "StdinOnce": false,
        "Tty": false,
        "User": "",
        "Volumes": null,
        "WorkingDir": ""
      },
      "Created": "2014-11-06T05:44:45.492745708Z",
      "Driver": "devicemapper",
      "ExecDriver": "native-0.2",
      "Host": "ubuntu-dev",
      "HostConfig": {
        "Binds": [
          "/tmp/registry:/tmp/registry"
        ],
        "CapAdd": null,
        "CapDrop": null,
        "ContainerIDFile": "",
        "Devices": [],
        "Dns": null,
        "DnsSearch": null,
        "ExtraHosts": null,
        "Links": null,
        "LxcConf": [],
        "NetworkMode": "bridge",
        "PortBindings": {
          "5000/tcp": [
            {
              "HostIp": "",
              "HostPort": "5000"
            }
          ]
        },
        "Privileged": false,
        "PublishAllPorts": false,
        "RestartPolicy": {
          "MaximumRetryCount": 0,
          "Name": ""
        },
        "VolumesFrom": null
      },
      "HostnamePath": "/var/lib/docker/containers/4f74b38bebe8049adf734c168ba877a7851ca3e8de6abc3c80f096c4d9947a8d/hostname",
      "HostsPath": "/var/lib/docker/containers/4f74b38bebe8049adf734c168ba877a7851ca3e8de6abc3c80f096c4d9947a8d/hosts",
      "Id": "4f74b38bebe8049adf734c168ba877a7851ca3e8de6abc3c80f096c4d9947a8d",
      "Image": "8e9a29f977a7e7c3569c35170d4152fc61055ec925a34d794bec8a906940fe99",
      "MountLabel": "",
      "Name": "/evil_mccarthy",
      "NetworkSettings": {
        "Bridge": "docker0",
        "Gateway": "172.17.42.1",
        "IPAddress": "172.17.0.2",
        "IPPrefixLen": 16,
        "MacAddress": "02:42:ac:11:00:02",
        "PortMapping": null,
        "Ports": {
          "5000/tcp": [
            {
              "HostIp": "0.0.0.0",
              "HostPort": "5000"
            }
          ]
        }
      },
      "Path": "/bin/sh",
      "ProcessLabel": "",
      "ResolvConfPath": "/var/lib/docker/containers/4f74b38bebe8049adf734c168ba877a7851ca3e8de6abc3c80f096c4d9947a8d/resolv.conf",
      "State": {
        "ExitCode": 0,
        "FinishedAt": "0001-01-01T00:00:00Z",
        "Paused": false,
        "Pid": 5465,
        "Restarting": false,
        "Running": true,
        "StartedAt": "2014-11-06T05:44:45.724142141Z"
      },
      "Volumes": {
        "/tmp/registry": "/tmp/registry"
      },
      "VolumesRW": {
        "/tmp/registry": true
      },
      "_id": "545ca670aaddcb5963a4e725"
    },
  ],
  "n": 3
}
```

---
` GET /containers `

**Parameters**
* host: 호스트에 동작하는 container조회
* all: running상태 이외의 모든 상태의 container를 조회(true|false 기본 false)

**Example request:**

```
GET /containers?host=ubuntu-dev&status=all HTTP/1.1
```

**Example response**
```
HTTP/1.0 200 OK
Content-Type: application/json

{
  "Command": [
    "/bin/sh",
    "-c",
    "exec docker-registry"
  ],
  "Created": "2014-11-06T05:44:45.492745708Z",
  "Host": "ubuntu-dev",
  "Id": "4f74b38bebe8049adf734c168ba877a7851ca3e8de6abc3c80f096c4d9947a8d",
  "Image": "registry",
  "Metrics": [
    0.0,
    2.77,
    13.02,
    1.6788528621457326,
    140574720.0,
    455532544.0,
    22114304.0,
    176402432.0,
    179765349.0,
    2230453.0
  ],
  "Name": "/evil_mccarthy",
  "Processes": [
    {
      "cmdline": [
        "/usr/bin/python",
        "/usr/local/bin/gunicorn",
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
        "--debug",
        "--max-requests",
        "100",
        "-k",
        "gevent",
        "--graceful-timeout",
        "3600",
        "-t",
        "3600",
        "-w",
        "4",
        "-b",
        "0.0.0.0:5000",
        "docker_registry.wsgi:application"
      ],
      "connections": [],
      "exe": "/usr/bin/python2.7",
      "metrics": [
        0.0,
        0.47,
        1.13,
        0.3800410223196444,
        31821824,
        99745792,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "name": "gunicorn",
      "num_threads": 1,
      "open_files": [],
      "pid": 3070,
      "status": "sleeping"
    },
    {
      "cmdline": [
        "/usr/bin/python",
        "/usr/local/bin/gunicorn",
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
        "--debug",
        "--max-requests",
        "100",
        "-k",
        "gevent",
        "--graceful-timeout",
        "3600",
        "-t",
        "3600",
        "-w",
        "4",
        "-b",
        "0.0.0.0:5000",
        "docker_registry.wsgi:application"
      ],
      "connections": [],
      "exe": "/usr/bin/python2.7",
      "metrics": [
        0.0,
        0.46,
        1.11,
        0.379992104695456,
        31817728,
        99758080,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "name": "gunicorn",
      "num_threads": 1,
      "open_files": [],
      "pid": 3071,
      "status": "sleeping"
    },
    {
      "cmdline": [
        "/usr/bin/python",
        "/usr/local/bin/gunicorn",
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
        "--debug",
        "--max-requests",
        "100",
        "-k",
        "gevent",
        "--graceful-timeout",
        "3600",
        "-t",
        "3600",
        "-w",
        "4",
        "-b",
        "0.0.0.0:5000",
        "docker_registry.wsgi:application"
      ],
      "connections": [],
      "exe": "/usr/bin/python2.7",
      "metrics": [
        0.0,
        0.48,
        1.12,
        0.379992104695456,
        31817728,
        99749888,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "name": "gunicorn",
      "num_threads": 1,
      "open_files": [],
      "pid": 3074,
      "status": "sleeping"
    },
    {
      "cmdline": [
        "/usr/bin/python",
        "/usr/local/bin/gunicorn",
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
        "--debug",
        "--max-requests",
        "100",
        "-k",
        "gevent",
        "--graceful-timeout",
        "3600",
        "-t",
        "3600",
        "-w",
        "4",
        "-b",
        "0.0.0.0:5000",
        "docker_registry.wsgi:application"
      ],
      "connections": [],
      "exe": "/usr/bin/python2.7",
      "metrics": [
        0.0,
        0.45,
        1.13,
        0.3800410223196444,
        31821824,
        99766272,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "name": "gunicorn",
      "num_threads": 1,
      "open_files": [],
      "pid": 3077,
      "status": "sleeping"
    },
    {
      "cmdline": [
        "/usr/bin/python",
        "/usr/local/bin/gunicorn",
        "--access-logfile",
        "-",
        "--error-logfile",
        "-",
        "--debug",
        "--max-requests",
        "100",
        "-k",
        "gevent",
        "--graceful-timeout",
        "3600",
        "-t",
        "3600",
        "-w",
        "4",
        "-b",
        "0.0.0.0:5000",
        "docker_registry.wsgi:application"
      ],
      "connections": [],
      "exe": "/usr/bin/python2.7",
      "metrics": [
        0.0,
        0.91,
        8.53,
        0.1587866081155317,
        13295616,
        56512512,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "name": "gunicorn",
      "num_threads": 1,
      "open_files": [],
      "pid": 5465,
      "status": "sleeping"
    }
  ],
  "Started": "2014-11-06T05:44:45.724142141Z",
  "_id": "545ca670aaddcb5963a4e726"
}
```
