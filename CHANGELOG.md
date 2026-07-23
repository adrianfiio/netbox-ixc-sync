# Changelog

Todas as mudanças notáveis do projeto serão documentadas aqui.

## [0.2.1]

### Alterado
- Removidos os valores padrão fixos (`Nicfibra` e `IXC Principal`).
- Campos `name`, `prefix` e `vrf_name` agora vêm em branco, com exemplos apenas no texto de ajuda.
- Deixa claro que o bloco e a VRF são configuráveis por perfil, permitindo múltiplos blocos/clientes.

## [0.2.0]

### Alterado
- Credenciais (host/token/SSL) movidas do banco de dados para variáveis de ambiente (`PLUGINS_CONFIG`), por segurança.
- Tela do plugin agora guarda apenas o bloco e a VRF.

## [0.1.0]

### Adicionado
- Integração com a API do IXCSoft (endpoints `radusuarios` e `cliente`).
- Sincronização de clientes com IP fixo para o NetBox.
- Filtro por bloco/prefixo.
- Criação de IPs `/32` dentro de uma VRF configurável.
- Descrição do IP com a razão social do cliente + login.
- Botão "Sincronizar" na interface do NetBox.
- Log de auditoria de cada sincronização.
