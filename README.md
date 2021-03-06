# docker-nsupdate-ddns

This script pushes container/ip information from local Docker instance to a DNS server via the DNS update mechanism desribed in RFC 2136 (nsupdate).  nsupdate is implemented by ISC Bind9.

Every REFRESH_INTERVAL seconds, it queries all the Docker containers on the local host, finds their IP and pushes it with the name to the DNS server.

## Running

The script takes environment variables or a config file. A sample config file is provided in `config.sample`. The file name of the config file can be passed as argument, but defaults to `config`.

The names of the environment variables is the same as in the config file. Environment variables have precendence over the config file.

### Environment variables
```bash
docker run -d \
   -v /var/run/docker.sock:/var/run/docker.sock \
   -e DOCKER_SOCKET=/var/run/docker.sock \
   -e DOMAIN=int.mtak.nl \
   -e IGNORE_LABEL=nl.mtak.docker-nsupdate-ddns.ignore \
   -e HOSTNAME_LABEL=nl.mtak.docker-nsupdate-ddns.hostname \
   -e DEFAULT_NETWORK=10.100.0.192/26 \
   -e REFRESH_INTERVAL=5 \
   -e ONE_SHOT=True \
   -e NAMESERVER=10.100.0.11 \
   -e TSIG_NAME=dck1 \
   -e TSIG_KEY=SyYXDCJ4kIs3qhvI= \
   merijntjetak/docker-nsupdate-ddns:latest
```

### Config file
```bash
cat <<EOF >configfile
DOCKER_SOCKET=/var/run/docker.sock
DOMAIN=int.mtak.nl
IGNORE_LABEL=nl.mtak.docker-nsupdate-ddns.ignore
HOSTNAME_LABEL=nl.mtak.docker-nsupdate-ddns.hostname
DEFAULT_NETWORK=10.100.0.192/26
REFRESH_INTERVAL=5
ONE_SHOT=True
NAMESERVER=10.100.0.11
TSIG_NAME=dck1
TSIG_KEY=SyYXDCJ4kIs3qhvI=
EOF

docker run -d \
  -v `pwd`/configfile:/configfile \
  -v /var/run/docker.sock:/var/run/docker.sock \
  merijntjetak/docker-nsupdate-ddns:latest /configfile

```

### Configuration

- `DOCKER_SOCKET` - Sets the location of the Docker socket
- `DOMAIN` - Sets the domain in which the records are created. Needs to match the Bind zone.
- `HOSTNAME_LABEL` - Docker label to override the default record name with. Use with `docker --label=nl.mtak.docker-nsupdate-ddns.hostname=nginx` to get `nginx.int.mtak.nl`
- `DEFAULT_NETWORK` - Preferred network to find IP for, in case there are multiple networks
- `REFRESH_INTERVAL` - Interval between updates
- `ONE_SHOT` - Set to True for the script to update once and immediately quit (nice for debugging)
- `NAMESERVER` - Nameserver to push updates to
- `TSIG_NAME` - Name of the TSIG key
- `TSIG_KEY` - TSIG-KEY

### Bind9 integration

1. Generate a key

    `tsig-keygen clientname >/etc/bind/keys/clientname.key`

2. Include keys in your Bind9 configuration

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
