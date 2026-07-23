import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import IXCConfig, SyncLog


class IXCConfigTable(NetBoxTable):
    name = tables.Column(linkify=True)
    prefix = tables.Column(verbose_name='Bloco')
    vrf_name = tables.Column(verbose_name='VRF')
    remove_orphans = columns.BooleanColumn(verbose_name='Remove órfãos')

    class Meta(NetBoxTable.Meta):
        model = IXCConfig
        fields = ('pk', 'id', 'name', 'prefix', 'vrf_name', 'remove_orphans')
        default_columns = ('name', 'prefix', 'vrf_name', 'remove_orphans')


class SyncLogTable(NetBoxTable):
    config = tables.Column(linkify=True)
    timestamp = tables.DateTimeColumn(verbose_name='Data/Hora')
    success = columns.BooleanColumn(verbose_name='Sucesso')

    class Meta(NetBoxTable.Meta):
        model = SyncLog
        fields = (
            'pk', 'id', 'config', 'timestamp', 'success',
            'criados', 'atualizados', 'ignorados', 'removidos',
            'total_ixc', 'mensagem',
        )
        default_columns = (
            'config', 'timestamp', 'success',
            'criados', 'atualizados', 'ignorados', 'removidos',
        )
