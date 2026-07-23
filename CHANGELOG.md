# Changelog

Todas as mudanças notáveis do projeto serão documentadas aqui.

## [0.1.0] - 2025

### Adicionado
- Integração com a API do IXCSoft (endpoint `radusuarios` e `cliente`).
- Sincronização de clientes com IP fixo para o NetBox.
- Filtro por bloco/prefixo (ex: `181.191.116.0/22`).
- Criação de IPs `/32` dentro de uma VRF configurável (padrão: `Nicfibra`).
- Descrição do IP com a razão social do cliente + login.
- Botão "Sincronizar" na interface do NetBox.
- Log de auditoria de cada sincronização.
