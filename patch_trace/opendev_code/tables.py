import django_tables2 as tables
from django_tables2.utils import Accessor

from tenancy.tables import COL_TENANT
from utilities.tables import BaseTable
from dcim.models import Device

DEVICE_LINK = """
<a href="{% url 'opendev:patchPanelTrace' pk=record.pk %}">
    {{ record.name|default:'<span class="label label-info">Unnamed device</span>' }}
</a>
"""

STATUS_LABEL = """
<span class="label label-{{ record.get_status_class }}">{{ record.get_status_display }}</span>
"""

DEVICE_ROLE = """
{% load helpers %}
<label class="label" style="color: {{ record.device_role.color|fgcolor }}; background-color: #{{ record.device_role.color }}">{{ value }}</label>
"""


class DeviceTable(BaseTable):
    name = tables.TemplateColumn(
        order_by=('_nat1', '_nat2', '_nat3'),
        template_code=DEVICE_LINK
    )
    status = tables.TemplateColumn(template_code=STATUS_LABEL, verbose_name='Status')
    tenant = tables.TemplateColumn(template_code=COL_TENANT)
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')])
    rack = tables.LinkColumn('dcim:rack', args=[Accessor('rack.pk')])
    device_role = tables.TemplateColumn(DEVICE_ROLE, verbose_name='Role')
    device_type = tables.LinkColumn(
        'dcim:devicetype', args=[Accessor('device_type.pk')], verbose_name='Type',
        text=lambda record: record.device_type.display_name
    )

    class Meta(BaseTable.Meta):
        model = Device
        fields = ('name', 'status', 'tenant', 'site', 'rack', 'device_role', 'device_type')
