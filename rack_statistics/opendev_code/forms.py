from __future__ import unicode_literals
from django import forms
from django.db.models import Count
from extras.forms import CustomFieldFilterForm
from utilities.forms import BootstrapMixin, FilterChoiceField
from dcim.models import Site, RackGroup, Rack, RackRole
from tenancy.models import Tenant

    
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
