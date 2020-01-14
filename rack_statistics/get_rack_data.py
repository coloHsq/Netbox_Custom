from __future__ import unicode_literals
import json
import datetime
from dcim.models import Device, Rack, FrontPort, PowerOutlet

"""
before start using the whole thing, you have to run this script, better way it's to schedule it daily
"""

# in order to make this script work properly, you need to assign a value the constants below (role name, not the id)
POWER_RACK = 'Insert your role here'
MULTI_MODE_CABLING = 'Insert your role here'
SINGLE_MODE_CABLING = 'Insert your role here'
COPPER_CABLING = 'Insert your role here'
POWER_CABLING = 'Insert your role here'

queryset = Rack.objects.exclude(role__name=POWER_RACK)  # if there's power rack in your environment, exclude them
rack_dictionary = {}
rack_data = {}


def get_port_stats(devices, port):
    """
    get number of free/total for devices ot the same role(the division done before)
    """
    i = 0
    tot = 0
    port_data = []
    for device in devices:
        for p in port.objects.filter(device=device):
            tot += 1
            if p.get_cable_peer() is None:
                i += 1
    port_data.append(i)  # number of available ports
    port_data.append(tot)  # number of total ports
    return port_data


for rack in queryset:
    single_devices = []
    multi_devices = []
    copper_devices = []
    power_devices = []
    # for every rack, fill the above lists with the "role defined" devices
    for device in Device.objects.filter(rack=rack):
        if device.device_role.name == MULTI_MODE_CABLING:
            multi_devices.append(device)
        elif device.device_role.name == SINGLE_MODE_CABLING:
            single_devices.append(device)
        elif device.device_role.name == COPPER_CABLING:
            copper_devices.append(device)
        elif device.device_role.name == POWER_CABLING:
            power_devices.append(device)
        else:
            pass
    rack_data['multi'] = get_port_stats(multi_devices, FrontPort)
    rack_data['single'] = get_port_stats(single_devices, FrontPort)
    rack_data['copper'] = get_port_stats(copper_devices, FrontPort)
    rack_data['power'] = get_port_stats(power_devices, PowerOutlet)
    rack_dictionary[rack.pk] = rack_data
    rack_data = {}
    # the final result is a dictionary (k: rack_id, v: dict) of dictionaries,
    # where every dict represents data for a single rack

# add datetime at the end of the execution
rack_dictionary['dateTime'] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

with open(r'/opt/netbox/netbox/opendev/rackJson.json', 'w') as outfile:
    json.dump(rack_dictionary, outfile)  # convert to json and store to file
