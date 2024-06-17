import os
import stat
import sys
from dotenv import dotenv_values
import time

from docker_nsupdate_ddns.lib import *
import logging

config = {}
ipam4_old = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s [%(levelname)s] %(message)s')
LOG = logging.getLogger(__name__)


def main():
    global config
    config = get_config()
    check_required_vars(config)

    if not eval(config['ONE_SHOT']):
        while True:
            loop()
            time.sleep(int(config['REFRESH_INTERVAL']))

    loop()
    LOG.info("Ending the process as ONE_SHOT is True")


def check_required_vars(_config):
    # Check for all required config
    required_vars = [
        'DOCKER_SOCKET',
        'DOMAIN',
        'IGNORE_LABEL',
        'HOSTNAME_LABEL',
        'DEFAULT_NETWORK',
        'REFRESH_INTERVAL',
        'ONE_SHOT',
        'NAMESERVER',
        'TSIG_NAME'
    ]
    missing_vars = []
    for item in required_vars:
        if item in _config:
            LOG.info(f"Detected config value: {item}={_config[item]}")
        else:
            missing_vars.append(item)
    if len(missing_vars) > 1:
        LOG.error(f"Missing required config: {', '.join(missing_vars)}")
        exit(1)

    # Check if docker socket is correct
    try:
        if not stat.S_ISSOCK(os.stat(_config['DOCKER_SOCKET']).st_mode):
            LOG.error(f"{_config['DOCKER_SOCKET']} not a docker socket file, exiting...")
            exit(1)
    except Exception as e:
        LOG.error(f"Docker socket {_config['DOCKER_SOCKET']} not found.", e)
        raise e


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

    return x


def determine_additions(ipam, ipam_old):
    return {k: v for k, v in ipam.items() if k not in ipam_old}


def determine_deletions(ipam, ipam_old):
    return {k: v for k, v in ipam_old.items() if k not in ipam}
    pass


if __name__ == "__main__":
    main()
