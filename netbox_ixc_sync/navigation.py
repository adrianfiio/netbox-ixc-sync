from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

config_item = PluginMenuItem(
    link='plugins:netbox_ixc_sync:ixcconfig_list',
    link_text='Configurações IXC',
    buttons=(
        PluginMenuButton(
            link='plugins:netbox_ixc_sync:ixcconfig_add',
            title='Adicionar',
            icon_class='mdi mdi-plus-thick',
        ),
    ),
)

log_item = PluginMenuItem(
    link='plugins:netbox_ixc_sync:synclog_list',
    link_text='Logs de Sincronização',
)

menu = PluginMenu(
    label='IXCSoft Sync',
    groups=(
        ('IXCSoft', (config_item, log_item)),
    ),
    icon_class='mdi mdi-sync',
)
