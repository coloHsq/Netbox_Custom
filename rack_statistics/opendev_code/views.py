from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import View
import json
from dcim import filters
from . import forms
from dcim.models import Rack

RACK_POWER = 'insert the role name here'
FREE = 0
TOTAL = 1
FILTER_DICT = {
    'unit': 'free_u',
    'mm': 'f_multi',
    'sm': 'f_single',
    'cu': 'f_copper',
    'pow': 'f_power',
    'kw': 'kw',
   }


def sort_rack_list(sort, rack_list, request):
    sorted_rack_list = sorted(rack_list, key=lambda sorted_rack: sorted_rack[FILTER_DICT[sort]], reverse=True)
    par = request.GET.copy()
    par.pop('sort')
    params = par.urlencode()
    return sorted_rack_list, params


class RackStats(View):
    # queryset = Rack.objects.select_related('site', 'group', 'tenant', 'role').exclude(role__name=RACK_POWER)
    # If there are power racks on your netbox instance(pdu, ups...), exclude them from this view

    queryset = Rack.objects.select_related('site', 'group', 'tenant', 'role')

    def get(self, request):
        # data are written on a json file by a daily running script to avoid long loading times
        with open('/opt/netbox/netbox/opendev/rackJson.json') as rack_file:
            rack_data = json.load(rack_file)
        rack_status = {}  # single rack data
        rack_list = []  # list containing all racks data
        self.queryset = filters.RackFilter(request.GET, self.queryset).qs  # apply filter chosen on web page
        for rack in self.queryset:
            '''
            ex : 
            f_multi = 'f' stands for 'free'
            t_multi = 't' stands for 'total'
            multi is for multi mode
            single is for single mode
            '''
            try:
                rack_data_file = rack_data[str(rack.pk)]
                rack_status['pk'] = rack.pk
                rack_status['name'] = rack.name
                try:
                    rack_status['role'] = rack.role.name
                except:
                    rack_status['role'] = '---'
                rack_status['height'] = rack.u_height
                rack_status['free_u'] = len(rack.get_available_units())
                # ports information are stored in a list where the first element represents the available ones
                # and the second is the total (free + occupied)
                rack_status['f_multi'] = rack_data_file['multi'][FREE]
                rack_status['t_multi'] = rack_data_file['multi'][TOTAL]
                rack_status['f_single'] = rack_data_file['single'][FREE]
                rack_status['t_single'] = rack_data_file['single'][TOTAL]
                rack_status['f_copper'] = rack_data_file['copper'][FREE]
                rack_status['t_copper'] = rack_data_file['copper'][TOTAL]
                rack_status['f_power'] = rack_data_file['power'][FREE]
                rack_status['t_power'] = rack_data_file['power'][TOTAL]
                # In my environment I've the possibility to import real time power consumption,
                # so there's a predisposition for it
                rack_status['kw'] = -1
                rack_status['pow_unit'] = ''
                rack_list.append(rack_status)
                rack_status = {}
            except:
                pass

        time = rack_data['dateTime']  # shows the datetime of the latest update
        params = request.GET.urlencode()
        sort = request.GET.get('sort', None)
        if sort:
            rack_list, params = sort_rack_list(sort, rack_list, request)

        return render(request, 'opendev/rack_stats.html',
                      {'rack_list': rack_list, 'time': time, 'params': params,
                       'filter_form': forms.RackFilterForm})
