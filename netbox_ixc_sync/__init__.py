from netbox.plugins import PluginConfig


class IXCSyncConfig(PluginConfig):
    name = 'netbox_ixc_sync'
    verbose_name = 'IXCSoft Sync'
    description = 'Sincroniza clientes e IPs fixos do IXCSoft com o NetBox'
    version = '0.3.0'
    author = 'adrianfiio'
    base_url = 'ixc-sync'
    min_version = '4.6.0'

    default_settings = {
        'ixc_host': '',
        'ixc_token': '',
        'verify_ssl': False,
    }


config = IXCSyncConfig
