import ipaddress
import logging

from django.conf import settings
from ipam.models import IPAddress, Prefix, VRF

from .ixc_api import IXCWebserviceClient
from .models import SyncLog

logger = logging.getLogger('netbox.plugins.ixc_sync')


def _get_credenciais():
    """Lê host/token/ssl do PLUGINS_CONFIG (configuration.py)."""
    cfg = settings.PLUGINS_CONFIG.get('netbox_ixc_sync', {})
    return (
        cfg.get('ixc_host', ''),
        cfg.get('ixc_token', ''),
        cfg.get('verify_ssl', False),
    )


def buscar_logins_com_ip(client, page_size=100):
    """Busca todos os radusuarios ATIVOS que tenham IP fixo preenchido."""
    logins = []
    page = 1
    while True:
        params = {
            'qtype': 'radusuarios.ativo',
            'query': 'S',
            'oper': '=',
            'page': str(page),
            'rp': str(page_size),
            'sortname': 'radusuarios.id',
            'sortorder': 'asc',
        }
        data = client.listar('radusuarios', params)
        registros = data.get('registros', [])
        if not registros:
            break

        for reg in registros:
            ip = (reg.get('ip') or '').strip()
            if ip:
                logins.append({
                    'id_cliente': reg.get('id_cliente'),
                    'login': reg.get('login'),
                    'ip': ip,
                })

        total = int(data.get('total', 0))
        if page * page_size >= total:
            break
        page += 1

    return logins


def buscar_nome_cliente(client, id_cliente, cache):
    """Busca o nome (razao) do cliente no endpoint 'cliente', com cache."""
    if id_cliente in cache:
        return cache[id_cliente]

    params = {
        'qtype': 'cliente.id',
        'query': str(id_cliente),
        'oper': '=',
        'page': '1',
        'rp': '1',
        'sortname': 'cliente.id',
        'sortorder': 'asc',
    }
    data = client.listar('cliente', params)
    registros = data.get('registros', [])
    nome = registros[0].get('razao') if registros else f'Cliente {id_cliente}'
    cache[id_cliente] = nome
    return nome


def sincronizar(cfg):
    """
    Executa a sincronização usando as credenciais do ambiente
    e o bloco/VRF do perfil (cfg). Grava um SyncLog no final.

    Se cfg.remove_orphans estiver ativo, remove com segurança os IPs
    deste bloco/VRF que não existem mais no IXC.
    """
    detalhes = []
    try:
        host, token, verify_ssl = _get_credenciais()

        if not host or not token:
            raise ValueError(
                'Credenciais do IXC não configuradas. Defina ixc_host e '
                'ixc_token no PLUGINS_CONFIG (ver README).'
            )

        client = IXCWebserviceClient(host, token, verify_ssl)
        rede = ipaddress.ip_network(cfg.prefix, strict=False)

        vrf_obj, _ = VRF.objects.get_or_create(name=cfg.vrf_name)
        Prefix.objects.get_or_create(prefix=cfg.prefix, vrf=vrf_obj)

        logins = buscar_logins_com_ip(client)
        cache_nomes = {}

        criados, atualizados, ignorados, removidos = 0, 0, 0, 0

        # Guarda os IPs que existem no IXC e pertencem ao bloco
        ips_no_ixc = set()

        for item in logins:
            ip_str = item['ip']
            try:
                ip_addr = ipaddress.ip_address(ip_str)
            except ValueError:
                ignorados += 1
                continue

            if ip_addr not in rede:
                ignorados += 1
                continue

            nome = buscar_nome_cliente(client, item['id_cliente'], cache_nomes)
            descricao = f"{nome} ({item['login']})"
            ip_cidr = f'{ip_str}/32'
            ips_no_ixc.add(ip_cidr)

            obj = IPAddress.objects.filter(address=ip_cidr, vrf=vrf_obj).first()
            if obj:
                if obj.description != descricao:
                    obj.description = descricao
                    obj.save()
                    atualizados += 1
                    detalhes.append(f'Atualizado: {ip_cidr} [{cfg.vrf_name}] -> {nome}')
            else:
                IPAddress.objects.create(
                    address=ip_cidr,
                    vrf=vrf_obj,
                    description=descricao,
                    status='active',
                )
                criados += 1
                detalhes.append(f'Criado: {ip_cidr} [{cfg.vrf_name}] -> {nome}')

        # ---- Remoção segura de IPs órfãos ----
        # Só executa se: opção ativada E a leitura do IXC trouxe dados
        # (evita apagar tudo caso a API retorne vazio por falha).
        if cfg.remove_orphans and len(logins) > 0:
            # Todos os IPs /32 que estão no NetBox dentro desta VRF...
            ips_no_netbox = IPAddress.objects.filter(
                vrf=vrf_obj,
                address__net_contained_or_equal=cfg.prefix,
            )
            for ip_obj in ips_no_netbox:
                if str(ip_obj.address) not in ips_no_ixc:
                    detalhes.append(
                        f'Removido (órfão): {ip_obj.address} '
                        f'[{cfg.vrf_name}] -> {ip_obj.description}'
                    )
                    ip_obj.delete()
                    removidos += 1

        resultado = {
            'success': True,
            'criados': criados,
            'atualizados': atualizados,
            'ignorados': ignorados,
            'removidos': removidos,
            'total_ixc': len(logins),
            'mensagem': 'Sincronização concluída com sucesso.',
            'detalhes': detalhes,
        }

    except Exception as e:
        logger.exception('Erro na sincronização IXC')
        resultado = {
            'success': False,
            'criados': 0,
            'atualizados': 0,
            'ignorados': 0,
            'removidos': 0,
            'total_ixc': 0,
            'mensagem': f'Erro: {e}',
            'detalhes': detalhes,
        }

    SyncLog.objects.create(
        config=cfg,
        success=resultado['success'],
        criados=resultado['criados'],
        atualizados=resultado['atualizados'],
        ignorados=resultado['ignorados'],
        removidos=resultado['removidos'],
        total_ixc=resultado['total_ixc'],
        mensagem=resultado['mensagem'],
        detalhes='\n'.join(resultado['detalhes']),
    )

    return resultado
