#!/usr/bin/env python3
import os
import re
import pynetbox
from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()
netbox_url          = os.environ['NETBOX_URL']
netbox_token        = os.environ['NETBOX_TOKEN']
netbox_key          = os.environ.get('NETBOX_KEY')
netbox_key_file     = os.environ.get('NETBOX_KEY_FILE')
ssl_verify          = os.environ.get('SSL_VERIFY', True)
zone                = os.environ['ZONE']
zone_template       = os.environ.get('ZONE_TEMPLATE','zone_template.tf.j2')
ttl                 = os.environ.get('TTL')
netbox_key_src      = 'private_key'
netbox_key_vlaue    = netbox_key
if netbox_key_file:
    netbox_key_src = 'private_key_file'
    netbox_key_vlaue = netbox_key_file
netboxcfg           = {
                      'url'           : netbox_url,
                      'token'         : netbox_token,
                      'ssl_verify'    : ssl_verify,
                      netbox_key_src  : netbox_key_vlaue  
                      }


def main():    
    nb = pynetbox.api(**netboxcfg)
    hosts = []
    nb_devices = nb.dcim.devices.filter(status=1)
    for nb_device in nb_devices:
        if nb_device.primary_ip4:
            host_ip = str(nb_device.primary_ip4).split('/')[0]
            resource_name = re.sub('[^0-9a-zA-Z]+', '_', nb_device.name)
            host_name = re.sub('[^0-9a-zA-Z]+', '-', nb_device.name)
            hosts.append(
                        {
                         'resource_name': resource_name, 
                         'host_name': host_name,
                         'ip': host_ip
                         }
                         )
    nb_vms = nb.virtualization.virtual_machines.filter(status=1)
    for nb_vm in nb_vms:
        if nb_vm.primary_ip4:
            host_ip = str(nb_vm.primary_ip4).split('/')[0]
            resource_name = re.sub('[^0-9a-zA-Z]+', '_', nb_vm.name)
            host_name = re.sub('[^0-9a-zA-Z..]+', '-', nb_vm.name)
            hosts.append(
                        {
                         'resource_name': resource_name, 
                         'host_name': host_name,
                         'ip': host_ip
                         }
                         )
    with open(zone_template, 'r') as read_file:
        template = Template(read_file.read())
    print(template.render(hosts=hosts, zone=zone, ttl=ttl))

    
if __name__ == "__main__":
    main()