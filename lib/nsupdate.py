import dns.update
import dns.query
import dns.tsigkeyring
import ipaddress
from datetime import datetime

config = {}


def add_records(records):
    keyring = dns.tsigkeyring.from_text(
        {config['TSIG_NAME']: config['TSIG_KEY']})

    for hostname, ip in records.items():
        print(datetime.now().isoformat(), end=" ")
        print("Adding record for " + hostname + "(" + ip + ")")

        rrtype = "A"
        address = ipaddress.ip_address(ip)
        if isinstance(address, ipaddress.IPv4Address):
            rrtype = "A"
        if isinstance(address, ipaddress.IPv6Address):
            rrtype = "AAAA"

        update = dns.update.Update(config['DOMAIN'], keyring=keyring)
        update.add(hostname, 60, rrtype, ip)
        dns.query.tcp(update, config['NAMESERVER'], timeout=2)


def delete_records(records):
    keyring = dns.tsigkeyring.from_text(
        {config['TSIG_NAME']: config['TSIG_KEY']})

    for hostname, ip in records.items():
        print(datetime.now().isoformat(), end=" ")
        print("Deleting record for " + hostname + "(" + ip + ")")

        update = dns.update.Update(config['DOMAIN'], keyring=keyring)
        update.delete(hostname)
        dns.query.tcp(update, config['NAMESERVER'], timeout=2)


def init(_config):
    global config
    config = _config
