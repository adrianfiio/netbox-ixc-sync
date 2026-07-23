import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import IXCConfig, SyncLog


class IXCConfigTable(NetBoxTable):
    name = tables.Column(linkify=True)
    prefix = tables.Column(verbose_name='Bloco')
    vrf_name = tables.Column(verbose_name='VRF')

    class Meta(NetBoxTable.Meta):
        model = IXCConfig
        fields = ('pk', 'id', 'name', 'host', 'prefix', 'vrf_name', 'verify_ssl')
        default_columns = ('name', 'host', 'prefix', 'vrf_name')


class SyncLogTable(NetBoxTable):
    config = tables.Column(linkify=True)
    timestamp = tables.DateTimeColumn(verbose_name='Data/Hora')
    success = columns.BooleanColumn(verbose_name='Sucesso')

    class Meta(NetBoxTable.Meta):
        model = SyncLog
        fields = (
            'pk', 'id', 'config', 'timestamp', 'success',
            'criados', 'atualizados', 'ignorados', 'total_ixc', 'mensagem',
        )
        default_columns = (
            'config', 'timestamp', 'success',
            'criados', 'atualizados', 'ignorados',
        )
