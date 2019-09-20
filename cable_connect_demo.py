from dcim.models import Device, Cable, RearPort
from extras.scripts import Script
from django.contrib.contenttypes.models import ContentType


def connect_multi_trunk(panels):

    cont_type = ContentType.objects.get_for_model(RearPort)

    types = [3500, 3040]  # type of cable, like OM3/OM4/OS2 ...
    colors = ['03a9f4', 'ff66ff']

    i = 0

    for pan in panels:

        term_a = RearPort.objects.get(device=pan['term_a'])

        term_b = RearPort.objects.get(device=pan['term_b'])

        cable = Cable(termination_a_type=cont_type, termination_a_id=term_a.pk, termination_b_type=cont_type, termination_b_id=term_b.pk, type=types[i], color=colors[i])

        cable.save()

        i += 1


def connect_single_trunk(panels):

    color = '795548'
    cat = 1610

    cont_type = ContentType.objects.get_for_model(RearPort)

    for pan in panels:

        a_side_rear_ports = []
        b_side_rear_ports = []

        for port in RearPort.objects.filter(device=pan['a_side']):
            a_side_rear_ports.append(port)

        for port in RearPort.objects.filter(device=pan['b_side']):
            b_side_rear_ports.append(port)

        for i in range(0, len(a_side_rear_ports)):

            cable = Cable(termination_a_type=cont_type, termination_a_id=a_side_rear_ports[i].pk, termination_b_type=cont_type, termination_b_id=b_side_rear_ports[i].pk, type=cat, color=color)

            cable.save()


def connect_cables():

    # to retrieve patch panels you are on your own, this script works with a list of dictionary (eg {'a_side': pp1, 'b_side': pp2})
    # each containing the two patch panels to be connected, it's on you to decide how retrieve them (eg. by ids, by names, by roles, by positions...)

    panels = []

    # here's the example with a given list of ids

    a_side_list = [101, 103, 105, 107, 109]
    b_side_list = [102, 104, 106, 108, 110]

    for i in range(0, len(a_side_list)):

        sides = {'a_side': Device.objects.get(pk=a_side_list[i]), 'b_side': Device.objects.get(pk=b_side_list[i])}

        panels.append(sides)

    connect_single_trunk(panels)  # for connections of devices that have only one rear port

    connect_multi_trunk(panels)  # for connections of devices that have at least two rear port


class CableConnectionDemo(Script):

    # this script will not work since querysets for patch panels are missing

    name = "Cable Creation Demo"
    description = "Demo that shows code used to create cables, THIS SCRIPT WON'T WORK"

    def run(self, data):

        connect_cables()
