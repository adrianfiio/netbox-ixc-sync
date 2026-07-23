from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View

from netbox.views import generic
from . import forms, sync, tables
from .models import IXCConfig, SyncLog


# ----------------- IXCConfig -----------------
class IXCConfigListView(generic.ObjectListView):
    queryset = IXCConfig.objects.all()
    table = tables.IXCConfigTable


class IXCConfigView(generic.ObjectView):
    queryset = IXCConfig.objects.all()

    def get_extra_context(self, request, instance):
        logs = SyncLog.objects.filter(config=instance)[:10]
        return {'logs': logs}


class IXCConfigEditView(generic.ObjectEditView):
    queryset = IXCConfig.objects.all()
    form = forms.IXCConfigForm


class IXCConfigDeleteView(generic.ObjectDeleteView):
    queryset = IXCConfig.objects.all()


# ----------------- Ação Sincronizar -----------------
class IXCSyncView(View):
    """Executa a sincronização e redireciona de volta."""

    def get(self, request, pk):
        cfg = get_object_or_404(IXCConfig, pk=pk)
        try:
            resultado = sync.sincronizar(cfg)
            if resultado['success']:
                messages.success(
                    request,
                    f"Sincronização OK: {resultado['criados']} criados, "
                    f"{resultado['atualizados']} atualizados, "
                    f"{resultado['ignorados']} ignorados "
                    f"(total lido do IXC: {resultado['total_ixc']})."
                )
            else:
                messages.error(request, resultado['mensagem'])
        except Exception as e:
            messages.error(request, f'Erro inesperado: {e}')

        return redirect(reverse('plugins:netbox_ixc_sync:ixcconfig', args=[pk]))


# ----------------- SyncLog -----------------
class SyncLogListView(generic.ObjectListView):
    queryset = SyncLog.objects.all()
    table = tables.SyncLogTable


class SyncLogView(generic.ObjectView):
    queryset = SyncLog.objects.all()


class SyncLogDeleteView(generic.ObjectDeleteView):
    queryset = SyncLog.objects.all()
