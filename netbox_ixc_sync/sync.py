import ipaddress
import logging

from ipam.models import IPAddress, Prefix, VRF

from .ixc_api import IXCWebserviceClient
from .models import SyncLog

logger = logging.getLogger('netbox.plugins.ixc_sync')


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
            if ip:  # só quem tem IP fixo
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
    1. Lê logins com IP fixo do IXC
    2. Filtra só os IPs do bloco (cfg.prefix)
    3. Cria/atualiza o IP /32 no NetBox, dentro da VRF (cfg.vrf_name),
       com descrição = razão do cliente
    4. Grava um SyncLog com o resultado
    """
    detalhes = []
    try:
        client = IXCWebserviceClient(cfg.host, cfg.token, cfg.verify_ssl)
        rede = ipaddress.ip_network(cfg.prefix, strict=False)

        # Garante a VRF (ex: Nicfibra)
        vrf_obj, _ = VRF.objects.get_or_create(name=cfg.vrf_name)

        # Garante o Prefix dentro da VRF
        Prefix.objects.get_or_create(prefix=cfg.prefix, vrf=vrf_obj)

        logins = buscar_logins_com_ip(client)
        cache_nomes = {}

        criados, atualizados, ignorados = 0, 0, 0

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

        resultado = {
            'success': True,
            'criados': criados,
            'atualizados': atualizados,
            'ignorados': ignorados,
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
            'total_ixc': 0,
            'mensagem': f'Erro: {e}',
            'detalhes': detalhes,
        }

    # Grava o log de auditoria
    SyncLog.objects.create(
        config=cfg,
        success=resultado['success'],
        criados=resultado['criados'],
        atualizados=resultado['atualizados'],
        ignorados=resultado['ignorados'],
        total_ixc=resultado['total_ixc'],
        mensagem=resultado['mensagem'],
        detalhes='\n'.join(resultado['detalhes']),
    )

    return resultado
