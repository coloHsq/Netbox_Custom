from __future__ import unicode_literals


from django import forms
from django.db.models import Count

from extras.forms import CustomFieldFilterForm

from utilities.forms import BootstrapMixin, FilterChoiceField, APISelectMultiple

from dcim.models import Site, RackGroup, Rack, RackRole, Device

from tenancy.models import Tenant


DEVICE_BY_PK_RE = r'{\d+\}'

INTERFACE_MODE_HELP_TEXT = """
Access: One untagged VLAN<br />
Tagged: One untagged VLAN and/or one or more tagged VLANs<br />
Tagged All: Implies all VLANs are available (w/optional untagged VLAN)
"""

    
class RackFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Rack
    q = forms.CharField(required=False, label='Search')
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('racks')),
        to_field_name='slug'
    )
    group_id = FilterChoiceField(
        queryset=RackGroup.objects.select_related('site').annotate(filter_count=Count('racks')),
        label='Rack group',
        null_label='-- None --'
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('racks')),
        to_field_name='slug',
        null_label='-- None --'
    )
    role = FilterChoiceField(
        queryset=RackRole.objects.annotate(filter_count=Count('racks')),
        to_field_name='slug',
        null_label='-- None --'
    )


class DeviceFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Device

    q = forms.CharField(
        required=False,
        label='Search'
    )

    site = FilterChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field="slug",
            filter_for={
                'rack_group_id': 'site',
                'rack_id': 'site',
            }
        )
    )
    rack_group_id = FilterChoiceField(
        queryset=RackGroup.objects.select_related(
            'site'
        ),
        label='Rack group',
        widget=APISelectMultiple(
            api_url="/api/dcim/rack-groups/",
            filter_for={
                'rack_id': 'rack_group_id',
            }
        )
    )
    rack_id = FilterChoiceField(
        queryset=Rack.objects.all(),
        label='Rack',
        null_label='-- None --',
        widget=APISelectMultiple(
            api_url="/api/dcim/racks/",
            null_option=True,
        )
    )
