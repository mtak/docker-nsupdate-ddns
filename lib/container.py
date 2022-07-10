import docker

config = {}


def get_container_name(container):
    """
    Get name of container, try in the following order:
      - Check if hostname_label is set
      - Fall back to container Name
    """
    x = container.attrs['Name'][1:]

    if config['HOSTNAME_LABEL'] in container.attrs['Config']['Labels']:
        x = container.attrs['Config']['Labels'][config['HOSTNAME_LABEL']]

    x = x.replace("_", "-")  # Be compliant with RFC1035
    return x


def get_container_ip(container):
    """
    Get IP of container. Try in the following order
     - default_network
     - First found network
     - Fall back to ['NetworkSettings']['IPAddress']
    """
    x = container.attrs['NetworkSettings']['IPAddress']

    if next(iter(container.attrs['NetworkSettings']['Networks'])):
        network_name = next(
            iter(container.attrs['NetworkSettings']['Networks']))
        x = container.attrs['NetworkSettings']['Networks'][network_name]['IPAddress']

    if config['DEFAULT_NETWORK'] in container.attrs['NetworkSettings']['Networks']:
        x = container.attrs['NetworkSettings']['Networks'][config['DEFAULT_NETWORK']]['IPAddress']

    return x


def generate_container_list():
    client = docker.from_env()

    container_list = client.containers.list()
    ipam4 = {}

    for container in container_list:
        if config['IGNORE_LABEL'] in container.attrs['Config']['Labels']:
            continue

        container_name = get_container_name(container)
        container_ip = get_container_ip(container)
        if container_ip:
            ipam4[container_name] = container_ip

    return ipam4


def init(_config):
    global config
    config = _config
