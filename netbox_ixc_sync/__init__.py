from netbox.plugins import PluginConfig


class IXCSyncConfig(PluginConfig):
    name = 'netbox_ixc_sync'
    verbose_name = 'IXCSoft Sync'
    description = 'Sincroniza clientes e IPs fixos do IXCSoft com o NetBox'
    version = '0.1.0'
    author = 'Nicfibra'
    base_url = 'ixc-sync'
    min_version = '4.6.0'


config = IXCSyncConfig
