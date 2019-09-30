from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import View
from dcim import filters
from . import formss, tables
from dcim.models import Device, FrontPort, Interface
from utilities.views import ObjectListView


class PatchPanelListView(PermissionRequiredMixin, ObjectListView):
    # Netbox's default device list view with pre-filtered device selection by role
    permission_required = 'dcim.view_device'
    queryset = Device.objects.select_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack', 'primary_ip4', 'primary_ip6'
    ).filter(device_role__pk__in=[1, 2, 3])  # replace these ids with the ones from your environment
    filter = filters.DeviceFilter
    filter_form = formss.DeviceFilterForm
    table = tables.DeviceTable
    template_name = 'opendev/patch_list.html'


class PatchPanelTrace(View):

    def get_trace(self, front_port):

        # method that continues looping until an interface is found

        loc_term = front_port
        rem_term = loc_term.get_cable_peer()
        rem_term_data = {}

        while True:

            if isinstance(rem_term, Interface):

                # if an interface is found, the loop stops and data is saved

                rem_term_data['term_name'] = rem_term.name
                rem_term_data['device_name'] = rem_term.device.name
                rem_term_data['device_role'] = rem_term.device.device_role.color
                rem_term_data['device_pk'] = rem_term.device.pk
                break

            elif isinstance(rem_term, FrontPort):

                # when cable peer return a front port, the trace is followed trough the assigned rear port
                # to get the 'other side' of the trunk and this results are set as start point for the next loop iteration

                rear = rem_term.rear_port
                rear_position = rem_term.rear_port_position

                remote_rear = rear.get_cable_peer()

                try:

                    loc_term = FrontPort.objects.get(rear_port=remote_rear, rear_port_position=rear_position)
                    rem_term = loc_term.get_cable_peer()

                except:

                    rem_term_data = None
                    break

            elif rem_term is None:

                rem_term_data = None
                break

            else:

                rem_term_data = None
                break

        return rem_term_data

    def invert(self, front_port):

        # given a front port, get its relative rear port and rear port position, retrieve the cable peer of the rear port
        # with these data retrieve the 'other side' front port and start the trace from it

        rear = front_port.rear_port
        rear_position = front_port.rear_port_position

        remote_rear = rear.get_cable_peer()

        try:

            loc_term = FrontPort.objects.get(rear_port=remote_rear, rear_port_position=rear_position)

            rem_term_data = self.get_trace(loc_term)

        except:

            rem_term_data = None

        return rem_term_data

    def get(self, request, pk):

        single_trace = {}

        full_traces = []

        curr_patch = Device.objects.get(pk=pk)

        patch_name = curr_patch.name

        patch_role = curr_patch.device_role.color

        front_ports = FrontPort.objects.filter(device=curr_patch)

        for front in front_ports:

            single_trace['origin'] = front.name

            single_trace['front_term'] = self.get_trace(front)

            single_trace['rear_term'] = self.invert(front)

            full_traces.append(single_trace)

            single_trace = {}

        return render(request, 'opendev/patch_panel_trace.html', {'full_traces': full_traces, 'patch_name': patch_name, 'patch_role': patch_role})
