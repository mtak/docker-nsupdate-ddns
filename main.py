#!/usr/bin/env python3

import os
import stat
import sys
from dotenv import dotenv_values
import time

from lib import *

config = {}
ipam4_old = {}


def main():
    global config
    config = get_config()

    try:
        stat.S_ISSOCK(os.stat(config['DOCKER_SOCKET']).st_mode)
    except Exception as e:
        print(e)
        print(
            "Docker socket " +
            config['DOCKER_SOCKET'] +
            " not found, exiting...")
        sys.exit(1)

    if not config['ONE_SHOT']:
        while True:
            loop()
            time.sleep(config['REFRESH_INTERVAL'])

    loop()


def loop():
    container.init(config)
    ipam4 = container.generate_container_list()
    global ipam4_old

    additions4 = determine_additions(ipam4, ipam4_old)
    deletions4 = determine_deletions(ipam4, ipam4_old)

    nsupdate.init(config)
    nsupdate.delete_records(deletions4)
    nsupdate.add_records(additions4)

    ipam4_old = ipam4


def get_config():
    config_file = sys.argv[1] if len(sys.argv) >= 2 else 'config'

    x = {
        **dotenv_values(os.path.join(os.getcwd(), config_file)),
        **os.environ
    }

    print("Config values:")
    for item in ['DOCKER_SOCKET', 'DOMAIN', 'HOSTNAME_LABEL', 'DEFAULT_NETWORK', 'REFRESH_INTERVAL', 'ONE_SHOT', 'NAMESERVER', 'TSIG_NAME']:
        print(item, end=": ")
        print(x[item])

    return x


def determine_additions(ipam, ipam_old):
    return {k: v for k, v in ipam.items() if k not in ipam_old}


def determine_deletions(ipam, ipam_old):
    return {k: v for k, v in ipam_old.items() if k not in ipam}
    pass


if __name__ == "__main__":
    main()
