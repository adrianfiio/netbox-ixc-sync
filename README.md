# NetBox IXC Sync

[![NetBox](https://img.shields.io/badge/NetBox-4.6%2B-blue.svg)](https://github.com/netbox-community/netbox)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.1-orange.svg)](https://github.com/adrianfiio/netbox-ixc-sync/releases)

Plugin para o **NetBox v4.6+** que integra com o **IXCSoft** e sincroniza automaticamente os clientes com **IP fixo** para o IPAM do NetBox.

Ao clicar em **Sincronizar**, o plugin lê os logins do IXCSoft, filtra apenas os IPs que pertencem a um bloco definido por você (ex: `181.191.116.0/22`) e cria cada IP `/32` dentro de uma VRF, com a razão social do cliente na descrição.

> 💡 O bloco e a VRF são **configuráveis por perfil**. Você pode criar quantas configurações quiser (uma por bloco/cliente) sem editar código.

---

## 📑 Índice

- [Como funciona](#-como-funciona)
- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração das credenciais](#-configuração-das-credenciais-variáveis-de-ambiente)
- [Uso](#-uso)
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
│ radusuarios │  clientes com     │   (plugin)     │  cria IPs /32  │  IPAM +  │
│  + cliente  │  IP fixo          │                │  na VRF        │   VRF    │
└─────────────┘                   └───────────────┘                └──────────┘
```

Fluxo da sincronização:

1. Lê os logins (`radusuarios`) **ativos** do IXCSoft que tenham **IP fixo** preenchido.
2. Busca a **razão social** do cliente (`cliente.razao`).
3. Filtra apenas os IPs que pertencem ao **bloco** configurado (ex: `181.191.116.0/22`).
4. Cria/atualiza cada IP como **/32** no NetBox, dentro da **VRF** configurada (ex: `Nicfibra`).
5. Preenche a **descrição** do IP com `Razão Social (login)`.
6. Registra um **log de auditoria** de cada execução.

---

## ✨ Funcionalidades

- 🔌 Cliente Python nativo para a API do IXCSoft.
- 🔎 Filtro por bloco/prefixo (só sincroniza o que você quer).
- 🌐 Criação de IPs `/32` dentro de uma VRF configurável.
- 🏷️ Descrição do IP com a razão social do cliente + login.
- 🧩 Suporte a **múltiplos blocos/clientes** (uma configuração por perfil).
- 🖱️ Botão **Sincronizar** direto na interface do NetBox.
- 📜 Log de auditoria completo de todas as sincronizações.
- 🔐 Credenciais (token/URL) protegidas via variáveis de ambiente — nunca no banco ou no Git.

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
# Ative o virtualenv do NetBox
source /opt/netbox/venv/bin/activate

# Clone o repositório
cd /opt
git clone https://github.com/adrianfiio/netbox-ixc-sync.git
cd netbox-ixc-sync

# Instale em modo editável
pip install -e .
```

### 2. Ativar o plugin

Edite `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = ['netbox_ixc_sync']
```

*(a configuração completa com credenciais está na próxima seção)*

### 3. Aplicar migrations e reiniciar

```bash
cd /opt/netbox/netbox
python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

### 4. (Recomendado) Tornar a instalação persistente

Para o plugin sobreviver a upgrades do NetBox, adicione-o ao arquivo de requisitos locais:

```bash
echo "-e /opt/netbox-ixc-sync" >> /opt/netbox/local_requirements.txt
```

---

## 🔐 Configuração das credenciais (variáveis de ambiente)

Por segurança, o **token e a URL do IXCSoft NÃO ficam no banco de dados**. Eles são lidos de variáveis de ambiente.

### 1. Definir as variáveis de ambiente

```bash
sudo nano /etc/netbox/netbox.env
```

Adicione:

```env
IXC_HOST=https://SEU_DOMINIO/webservice/v1
IXC_TOKEN=7:521683b205bb5bfc28f16e06efc717112b457ba6008b3f875fa7964177c0a191
IXC_VERIFY_SSL=false
```

> `IXC_VERIFY_SSL=false` é o correto para certificados auto-assinados (padrão do IXC).

### 2. Ligar as variáveis ao plugin

Edite `/opt/netbox/netbox/netbox/configuration.py`:

```python
import os

PLUGINS = ['netbox_ixc_sync']

PLUGINS_CONFIG = {
    'netbox_ixc_sync': {
        'ixc_host': os.environ.get('IXC_HOST', ''),
        'ixc_token': os.environ.get('IXC_TOKEN', ''),
        'verify_ssl': os.environ.get('IXC_VERIFY_SSL', 'false').lower() == 'true',
    }
}
```

### 3. Reiniciar

```bash
sudo systemctl restart netbox netbox-rq
```

> ✅ Com isso o token nunca aparece no banco, no código ou no Git. Na tela do plugin você configura apenas o **Bloco** e a **VRF**.

---

## ⚙️ Uso

1. No menu lateral do NetBox: **IXCSoft Sync → Configurações IXC → Adicionar**.
2. Preencha (os campos vêm **em branco** — os valores abaixo são apenas exemplos):

   | Campo | Exemplo |
   |-------|---------|
   | **Nome** | `Bloco Matriz` |
   | **Bloco (Prefix)** | `181.191.116.0/22` |
   | **VRF** | `Nicfibra` |

3. Salve e abra a configuração criada.
4. Clique em **Sincronizar agora**. 🚀
5. Veja o resultado em **IXCSoft Sync → Logs de Sincronização**.

Cada IP fixo do bloco será criado no NetBox assim:

```
VRF: Nicfibra
└─ Prefix: 181.191.116.0/22
    ├─ 181.191.116.10/32 → "FULANO DA SILVA (login123)"
    ├─ 181.191.116.25/32 → "EMPRESA XYZ LTDA (login456)"
    └─ ...
```

---

## 🧩 Usando com vários blocos / clientes

O plugin permite **quantas configurações você quiser**. Para adicionar um novo bloco ou cliente, **não é preciso editar código** — basta criar uma nova configuração na tela.

Exemplo de várias configurações cadastradas:

| Nome        | Bloco               | VRF       |
|-------------|---------------------|-----------|
| Bloco Matriz| `181.191.116.0/22`  | `Nicfibra`|
| Cliente B   | `200.150.10.0/24`   | `ClienteB`|
| Filial Sul  | `45.230.88.0/23`    | `SulNet`  |

Cada configuração tem seu **próprio botão Sincronizar** e gera seus próprios logs. Basta clicar em **Adicionar** e preencher o novo bloco e a nova VRF. 🎯

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
    ├── __init__.py         # config do plugin
    ├── ixc_api.py          # cliente da API IXCSoft
    ├── models.py           # IXCConfig + SyncLog
    ├── sync.py             # lógica de sincronização
    ├── forms.py
    ├── tables.py
    ├── views.py            # views + ação Sincronizar
    ├── urls.py
    ├── navigation.py       # menu lateral
    ├── migrations/
    │   ├── __init__.py
    │   └── 0001_initial.py
    └── templates/
        └── netbox_ixc_sync/
            ├── ixcconfig.html
            └── synclog.html
```

---

## 🔧 Solução de problemas

| Problema | Causa provável | Solução |
|----------|----------------|---------|
| **Erro 401 (Unauthorized)** | Formato do token/autenticação diferente | Verifique o token e o formato do header em `ixc_api.py` |
| **"Credenciais não configuradas"** | Variáveis de ambiente não definidas | Confira `IXC_HOST` e `IXC_TOKEN` e reinicie o NetBox |
| **Nenhum IP criado** | Campo do IP diferente no seu IXC | Confirme se o campo é `radusuarios.ip`; ajuste em `sync.py` |
| **Nome do cliente errado** | Campo diferente no seu IXC | O plugin usa `cliente.razao`; ajuste em `sync.py` se necessário |
| **SSL / certificado inválido** | Certificado auto-assinado | Deixe `IXC_VERIFY_SSL=false` |

Para ver logs detalhados de erro:

```bash
sudo journalctl -u netbox -f
```

---

## 🗺️ Roadmap

- [x] Sincronização manual por botão
- [x] Log de auditoria
- [x] Credenciais via variáveis de ambiente
- [x] Suporte a múltiplos blocos/clientes
- [ ] Sincronização automática agendada (cron / RQ scheduler)
- [ ] Suporte a IPv6
- [ ] Vínculo opcional do cliente como Tenant
- [ ] Filtro por múltiplos blocos em uma única configuração

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

MIT © [adrianfiio](https://github.com/adrianfiio)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra uma *issue* ou envie um *pull request*.

1. Faça um fork do projeto
2. Crie sua branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit (`git commit -m 'feat: nova funcionalidade'`)
4. Push (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request
