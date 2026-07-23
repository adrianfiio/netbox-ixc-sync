# NetBox IXC Sync

Plugin para o **NetBox v4.6+** que integra com o **IXCSoft** e sincroniza automaticamente clientes com **IP fixo** para o IPAM do NetBox.

Ao clicar em **Sincronizar**, o plugin:
1. Lê os logins (`radusuarios`) ativos do IXCSoft que tenham **IP fixo** preenchido.
2. Filtra apenas os IPs que pertencem ao **bloco** configurado (ex: `181.191.116.0/22`).
3. Cria/atualiza cada IP como **/32** no NetBox, dentro da **VRF** configurada (padrão: `Nicfibra`).
4. Preenche a **descrição** do IP com a **razão social** do cliente + login.
5. Registra um **log de auditoria** de cada execução.

---

## ✨ Funcionalidades

- 🔌 Cliente Python nativo para a API do IXCSoft.
- 🔎 Filtro por bloco/prefixo.
- 🌐 Criação de IPs `/32` dentro de uma VRF.
- 🏷️ Descrição do IP com a razão social do cliente.
- 🖱️ Botão **Sincronizar** na interface do NetBox.
- 📜 Log de auditoria de todas as sincronizações.

---

## 📋 Requisitos

- NetBox **>= 4.6.0**
- Python **>= 3.10**
- Token de API do IXCSoft (formato `id:hash`)

---

## 🚀 Instalação

```bash
# 1. Ative o virtualenv do NetBox
source /opt/netbox/venv/bin/activate

# 2. Clone e instale
git clone https://github.com/SEU_USUARIO/netbox-ixc-sync.git
cd netbox-ixc-sync
pip install -e .
```

Edite `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = ['netbox_ixc_sync']
```

Aplique as migrations e reinicie:

```bash
cd /opt/netbox/netbox
python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

> Para instalação persistir em upgrades do NetBox, adicione `netbox-ixc-sync` ao arquivo `local_requirements.txt`.

---

## ⚙️ Uso

1. No menu lateral: **IXCSoft Sync → Configurações IXC → Adicionar**.
2. Preencha:
   - **Host:** `https://SEU_DOMINIO/webservice/v1`
   - **Token:** `7:521683b205bb5bfc28f16e06efc717112b457ba6008b3f875fa7964177c0a191`
   - **Bloco (Prefix):** `181.191.116.0/22`
   - **VRF:** `Nicfibra`
   - **Verificar SSL:** desmarcado (para certificado auto-assinado)
3. Salve e clique em **Sincronizar agora**.
4. Veja o resultado em **Logs de Sincronização**.

---

## 🗂️ Estrutura

```
netbox_ixc_sync/
├── ixc_api.py      # cliente da API IXCSoft
├── models.py       # IXCConfig + SyncLog
├── sync.py         # lógica de sincronização
├── views.py        # views + ação Sincronizar
├── tables.py       # tabelas da interface
├── forms.py
├── urls.py
├── navigation.py
└── templates/
```

---

## 🔧 Ajustes possíveis

- **Erro 401 (autenticação):** alguns IXC usam formato diferente de token. Ajuste em `ixc_api.py`.
- **Campo do IP:** o plugin lê `radusuarios.ip`. Se seu IXC usar outro campo, ajuste em `sync.py`.
- **Nome do cliente:** o plugin usa o campo `razao`. Ajuste em `sync.py` se necessário.

---

## 📄 Licença

MIT © Nicfibra
