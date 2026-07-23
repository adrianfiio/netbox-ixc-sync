# NetBox IXC Sync

[![NetBox](https://img.shields.io/badge/NetBox-4.6%2B-blue.svg)](https://github.com/netbox-community/netbox)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-orange.svg)](https://github.com/adrianfiio/netbox-ixc-sync/releases)

Plugin para o **NetBox v4.6+** que integra com o **IXCSoft** e sincroniza automaticamente os clientes com **IP fixo** para o IPAM do NetBox.

Ao clicar em **Sincronizar**, o plugin lê os logins do IXCSoft, filtra apenas os IPs que pertencem a um bloco definido por você (ex: `203.0.113.0/24`) e cria cada IP `/32` dentro de uma VRF, com a razão social do cliente na descrição. Opcionalmente, também remove os IPs de clientes que não existem mais no IXC.

> 💡 O bloco e a VRF são **configuráveis por perfil**. Você pode criar quantas configurações quiser (uma por bloco/cliente) sem editar código.

---

## 📑 Índice

- [Como funciona](#-como-funciona)
- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração das credenciais](#-configuração-das-credenciais)
- [Uso](#-uso)
- [Remoção de IPs órfãos](#-remoção-de-ips-órfãos-clientes-cancelados)
- [Usando com vários blocos / clientes](#-usando-com-vários-blocos--clientes)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Solução de problemas](#-solução-de-problemas)
- [Roadmap](#-roadmap)
- [Licença](#-licença)

---

## 🔄 Como funciona

```
┌─────────────┐     API REST      ┌───────────────┐      ORM       ┌──────────┐
│   IXCSoft   │ ────────────────► │ netbox-ixc-sync│ ────────────► │  NetBox  │
│ radusuarios │  clientes com     │   (plugin)     │  cria/remove   │  IPAM +  │
│  + cliente  │  IP fixo          │                │  IPs /32       │   VRF    │
└─────────────┘                   └───────────────┘                └──────────┘
```

Fluxo da sincronização:

1. Lê os logins (`radusuarios`) **ativos** do IXCSoft que tenham **IP fixo** preenchido.
2. Busca a **razão social** do cliente (`cliente.razao`).
3. Filtra apenas os IPs que pertencem ao **bloco** configurado (ex: `203.0.113.0/24`).
4. Cria/atualiza cada IP como **/32** no NetBox, dentro da **VRF** configurada (ex: `MinhaVRF`).
5. Preenche a **descrição** do IP com `Razão Social (login)`.
6. *(Opcional)* Remove do NetBox os IPs do bloco que não existem mais no IXC.
7. Registra um **log de auditoria** de cada execução.

---

## ✨ Funcionalidades

- 🔌 Cliente Python nativo para a API do IXCSoft.
- 🔎 Filtro por bloco/prefixo (só sincroniza o que você quer).
- 🌐 Criação de IPs `/32` dentro de uma VRF configurável.
- 🏷️ Descrição do IP com a razão social do cliente + login.
- 🗑️ Remoção opcional e segura de IPs órfãos (clientes cancelados).
- 🧩 Suporte a **múltiplos blocos/clientes** (uma configuração por perfil).
- 🖱️ Botão **Sincronizar** direto na interface do NetBox.
- 📜 Log de auditoria completo de todas as sincronizações.
- 🔐 Credenciais (token/URL) protegidas — nunca no banco ou no Git.

---

## 📋 Requisitos

| Componente | Versão |
|------------|--------|
| NetBox     | >= 4.6.0 |
| Python     | >= 3.10 |
| IXCSoft    | Token de API (formato `id:hash`) com permissão de leitura em `radusuarios` e `cliente` |

---

## 🚀 Instalação

> Execute os comandos como o usuário do NetBox e dentro do virtualenv dele.

### 1. Clonar e instalar o plugin

```bash
source /opt/netbox/venv/bin/activate
cd /opt
git clone https://github.com/adrianfiio/netbox-ixc-sync.git
cd netbox-ixc-sync
pip install -e .
```

### 2. Ativar o plugin e configurar as credenciais

Edite `/opt/netbox/netbox/netbox/configuration.py` (veja a seção
[Configuração das credenciais](#-configuração-das-credenciais)).

### 3. Aplicar migrations e reiniciar

```bash
cd /opt/netbox/netbox
python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

### 4. (Recomendado) Tornar a instalação persistente

```bash
echo "-e /opt/netbox-ixc-sync" >> /opt/netbox/local_requirements.txt
```

---

## 🔐 Configuração das credenciais

Por segurança, o **token e a URL do IXCSoft NÃO ficam no banco de dados** —
eles são definidos no `configuration.py`, que fica apenas no seu servidor
(nunca vai para o Git).

Edite `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = ['netbox_ixc_sync']

PLUGINS_CONFIG = {
    'netbox_ixc_sync': {
        'ixc_host': 'https://SEU_DOMINIO/webservice/v1',
        'ixc_token': 'SEU_ID:SEU_HASH_DO_TOKEN',
        'verify_ssl': False,
    }
}
```

> Se você já tem outros plugins, adicione `'netbox_ixc_sync'` à lista `PLUGINS`
> existente e inclua a chave `'netbox_ixc_sync'` dentro do `PLUGINS_CONFIG`
> já existente — não crie blocos duplicados.

`verify_ssl: False` é o correto para certificados auto-assinados (padrão do IXC).

Reinicie após alterar:

```bash
sudo systemctl restart netbox netbox-rq
```

---

## ⚙️ Uso

1. No menu lateral do NetBox: **IXCSoft Sync → Configurações IXC → Adicionar**.
2. Preencha (os campos vêm **em branco** — os valores abaixo são apenas exemplos):

   | Campo | Exemplo |
   |-------|---------|
   | **Nome** | `Bloco Matriz` |
   | **Bloco (Prefix)** | `203.0.113.0/24` |
   | **VRF** | `MinhaVRF` |
   | **Remover IPs órfãos** | desmarcado (ver seção abaixo) |

3. Salve, abra a configuração e clique em **Sincronizar agora**. 🚀
4. Veja o resultado em **IXCSoft Sync → Logs de Sincronização**.

Resultado no NetBox:

```
VRF: MinhaVRF
└─ Prefix: 203.0.113.0/24
    ├─ 203.0.113.10/32 → "FULANO DA SILVA (login123)"
    ├─ 203.0.113.25/32 → "EMPRESA XYZ LTDA (login456)"
    └─ ...
```

---

## 🗑️ Remoção de IPs órfãos (clientes cancelados)

Se você marcar **"Remover IPs órfãos"** na configuração, a cada sincronização
o plugin também **remove do NetBox** os IPs que não existem mais no IXC —
por exemplo, clientes cancelados que perderam o IP fixo.

A remoção é **segura**:

- ✅ Só afeta IPs **dentro do bloco e da VRF daquela configuração** — nunca mexe em nada de fora.
- ✅ Só executa se a leitura do IXC retornou dados (evita apagar tudo se a API falhar).
- ✅ Cada remoção fica registrada no **log**, com o IP e a descrição.

> ⚠️ Recomenda-se testar primeiro com a opção **desmarcada** e conferir os logs
> antes de ativar a remoção automática.

---

## 🧩 Usando com vários blocos / clientes

Para adicionar um novo bloco ou cliente, **não é preciso editar código** —
basta criar uma nova configuração na tela.

| Nome         | Bloco               | VRF            |
|--------------|---------------------|----------------|
| Bloco Matriz | `203.0.113.0/24`    | `MinhaVRF`     |
| Cliente B    | `198.51.100.0/24`   | `VRF-ClienteB` |
| Filial Sul   | `192.0.2.0/24`      | `VRF-Sul`      |

Cada configuração tem seu **próprio botão Sincronizar** e gera seus próprios logs.

---

## 🗂️ Estrutura do projeto

```
netbox-ixc-sync/
├── LICENSE
├── README.md
├── CHANGELOG.md
├── setup.py
├── pyproject.toml
└── netbox_ixc_sync/
    ├── __init__.py
    ├── ixc_api.py
    ├── models.py
    ├── sync.py
    ├── forms.py
    ├── tables.py
    ├── views.py
    ├── urls.py
    ├── navigation.py
    ├── migrations/
    │   ├── __init__.py
    │   ├── 0001_initial.py
    │   └── 0002_orphans.py
    └── templates/
        └── netbox_ixc_sync/
            ├── ixcconfig.html
            └── synclog.html
```

---

## 🔧 Solução de problemas

| Problema | Causa provável | Solução |
|----------|----------------|---------|
| **Erro 401 (Unauthorized)** | Formato do token/autenticação diferente | Verifique o token e o header em `ixc_api.py` |
| **"Credenciais não configuradas"** | `PLUGINS_CONFIG` sem host/token | Confira o `configuration.py` e reinicie o NetBox |
| **Nenhum IP criado** | Campo do IP diferente no seu IXC | Confirme se o campo é `radusuarios.ip`; ajuste em `sync.py` |
| **Nome do cliente errado** | Campo diferente no seu IXC | O plugin usa `cliente.razao`; ajuste em `sync.py` |
| **SSL / certificado inválido** | Certificado auto-assinado | Deixe `verify_ssl: False` |

Ver logs em tempo real:

```bash
sudo journalctl -u netbox -f
```

---

## 🗺️ Roadmap

- [x] Sincronização manual por botão
- [x] Log de auditoria
- [x] Credenciais protegidas via configuration.py
- [x] Suporte a múltiplos blocos/clientes
- [x] Remoção de IPs órfãos (clientes cancelados)
- [ ] Sincronização automática agendada (cron / RQ scheduler)
- [ ] Suporte a IPv6
- [ ] Vínculo opcional do cliente como Tenant

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE).

MIT © [adrianfiio](https://github.com/adrianfiio)

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie sua branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit (`git commit -m 'feat: nova funcionalidade'`)
4. Push (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request
