from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class IXCConfig(NetBoxModel):
    """Configuração de conexão com o IXCSoft."""
    name = models.CharField(max_length=100, default='IXC Principal')
    host = models.CharField(
        max_length=255,
        help_text='Ex: https://SEU_DOMINIO/webservice/v1'
    )
    token = models.CharField(
        max_length=255,
        help_text='Token gerado no cadastro do usuário (id:hash)'
    )
    verify_ssl = models.BooleanField(
        default=False,
        help_text='Marque apenas se o certificado for válido (não auto-assinado)'
    )
    prefix = models.CharField(
        max_length=50,
        help_text='Bloco a sincronizar. Ex: 181.191.116.0/22'
    )
    vrf_name = models.CharField(
        max_length=100,
        default='Nicfibra',
        help_text='Nome da VRF onde os IPs serão criados. Ex: Nicfibra'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Configuração IXC'
        verbose_name_plural = 'Configurações IXC'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_ixc_sync:ixcconfig', args=[self.pk])


class SyncLog(NetBoxModel):
    """Log de auditoria de cada sincronização executada."""
    config = models.ForeignKey(
        to=IXCConfig,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    criados = models.IntegerField(default=0)
    atualizados = models.IntegerField(default=0)
    ignorados = models.IntegerField(default=0)
    total_ixc = models.IntegerField(default=0)
    mensagem = models.TextField(blank=True)
    detalhes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Log de Sincronização'
        verbose_name_plural = 'Logs de Sincronização'

    def __str__(self):
        return f'{self.config.name} - {self.timestamp:%d/%m/%Y %H:%M:%S}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_ixc_sync:synclog', args=[self.pk])
