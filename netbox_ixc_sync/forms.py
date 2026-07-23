from netbox.forms import NetBoxModelForm
from .models import IXCConfig


class IXCConfigForm(NetBoxModelForm):
    class Meta:
        model = IXCConfig
        fields = ('name', 'prefix', 'vrf_name', 'tags')
