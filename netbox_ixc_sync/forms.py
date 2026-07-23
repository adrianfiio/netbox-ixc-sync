from netbox.forms import NetBoxModelForm
from .models import IXCConfig


class IXCConfigForm(NetBoxModelForm):
    class Meta:
        model = IXCConfig
        fields = ('name', 'host', 'token', 'verify_ssl', 'prefix', 'vrf_name', 'tags')
