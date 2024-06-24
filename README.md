# docker-nsupdate-ddns

This script pushes container/ip information from local Docker instance to a DNS server via the DNS update mechanism desribed in RFC 2136 (nsupdate).  nsupdate is implemented by ISC Bind9.

Every REFRESH_INTERVAL seconds, it queries all the Docker containers on the local host, finds their IP and pushes it with the name to the DNS server.

## Configuration
The script takes environment variables or a config file. A sample config file is provided in [`sample.config.env`](sample.config.env).

The file name of the config file can be passed as argument, but defaults to `/config.env`.

The names of the environment variables is the same as in the config file. Environment variables have precendence over the config file.

| Config           | Required | Default Value                         | Description                                                                                                                                                                                                                                             |
|------------------|----------|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| DOMAIN           | Yes      |                                       | Sets the domain in which the records are created. Needs to match the Bind zone.                                                                                                                                                                         |
| NAMESERVER       | Yes      |                                       | Nameserver to push updates to.                                                                                                                                                                                                                          |
| TSIG_NAME        | Yes      |                                       | TSIG key name for secure updates.                                                                                                                                                                                                                       |
| TSIG_KEY         | Yes      |                                       | TSIG key value for secure updates.                                                                                                                                                                                                                      |
| DOCKER_SOCKET    | No       | /var/run/docker.sock                  | Sets the location of the Docker socket.                                                                                                                                                                                                                 |
| HOSTNAME_LABEL   | No       | nl.mtak.docker-nsupdate-ddns.hostname | Docker label to override the default record name with. Use with `docker --label=nl.mtak.docker-nsupdate-ddns.hostname=nginx` to get `nginx.int.mtak.nl` _If the label value present on the container, use it as hostname otherwise the container name._ |
| IGNORE_LABEL     | No       | nl.mtak.docker-nsupdate-ddns.ignore   | Container label to exclude containers from DNS updates.                                                                                                                                                                                                 |
| DNS_RECORD_TTL   | No       | 60                                    | Time to Live (TTL) for DNS records (seconds).                                                                                                                                                                                                           |
| DEFAULT_NETWORK  | No       |                                       | Preferred network name to find IP for, in case there are multiple networks.                                                                                                                                                                             |
| REFRESH_INTERVAL | No       | 60                                    | Interval between checks for container changes (seconds).                                                                                                                                                                                                |
| ONE_SHOT         | No       | False                                 | Run once and exit instead of continuously monitoring.                                                                                                                                                                                                   |

### Environment variables
```bash
docker run -d \
   -v /var/run/docker.sock:/var/run/docker.sock \
   -e DOMAIN=int.mtak.nl \
   -e NAMESERVER=10.100.0.11 \
   -e TSIG_NAME=dck1 \
   -e TSIG_KEY=SyYXDCJ4kIs3qhvI= \
   -e DOCKER_SOCKET=/var/run/docker.sock \
   -e HOSTNAME_LABEL=nl.mtak.docker-nsupdate-ddns.hostname \
   -e IGNORE_LABEL=nl.mtak.docker-nsupdate-ddns.ignore \
   -e DNS_RECORD_TTL=60 \
   -e DEFAULT_NETWORK=10.100.0.192/26 \
   -e REFRESH_INTERVAL=60 \
   -e ONE_SHOT=true \
   merijntjetak/docker-nsupdate-ddns:latest
```

### Config file
```bash
cat <<EOF > configfile
DOMAIN=int.mtak.nl
NAMESERVER=10.100.0.11
TSIG_NAME=dck1
TSIG_KEY=SyYXDCJ4kIs3qhvI=
DOCKER_SOCKET=/var/run/docker.sock
HOSTNAME_LABEL=nl.mtak.docker-nsupdate-ddns.hostname
IGNORE_LABEL=nl.mtak.docker-nsupdate-ddns.ignore
DNS_RECORD_TTL=60
DEFAULT_NETWORK=10.100.0.192/26
REFRESH_INTERVAL=60
ONE_SHOT=False
EOF

docker run -d \
  -v `pwd`/configfile:/configfile \
  -v /var/run/docker.sock:/var/run/docker.sock \
  merijntjetak/docker-nsupdate-ddns:latest /configfile

```

### Bind9 integration

1. Generate a key

    `tsig-keygen clientname > /etc/bind/keys/clientname.key`

2. Include keys in your Bind9 `named.config` configuration file

    `include "/etc/bind/keys/*";`

3. Allow updates to your zone:

    ```
    zone "int.mtak.nl" {
        type master;
        file "/etc/bind/db/int.mtak.nl.zone";
        update-policy {
                grant clientname zonesub ANY;
        };
    };
    ```

## Design
### Requirements

- [x] Eventual redundancy (Bind9 zone transfers to secondary)
- [x] Support for multiple individual Docker servers
- [ ] IPv6 support
- [x] Detect hostname in decreasing order of priority:
    - label
    - Container name
- [x] Forward-only
- [ ] Clean up DNS (DNS is stateful but the script isn't, so there might be a mismatch)

### Nice to have

- Add tests

### Alternatives

CoreDNS didn't fit the requirements, because zone transfers out of a CoreDNS server do not
include the records from the coredns-dockerdiscovery plugin.

K3s and k8s would probably do this, but incur significant complexity over a standalone Docker instance. 
