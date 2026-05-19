# ENDE Platform

Sistema web integrado para gestão de clientes de energia eléctrica da **ENDE-EP, Angola**. Plataforma para clientes **pré-pago** e **pós-pago** com funcionalidades de recarga, faturação, pagamentos, suporte e notificações.

---

## Funcionalidades

- **Clientes Pré-pago**: consulta de saldo, recarga, histórico de transacções
- **Clientes Pós-pago**: consulta de faturas, pagamento, histórico de consumo
- **Suporte**: abertura e acompanhamento de tickets com mensagens
- **Notificações**: alertas in-app para recargas, pagamentos e actualizações de tickets
- **API REST**: endpoints JSON para integração futura

## Tecnologias

| Tecnologia | Versão |
|---|---|
| Python | 3.12+ |
| Django | 6.0.5 |
| Django REST Framework | 3.x |
| Bootstrap | 5.3.3 |
| Chart.js | 4.4.7 |
| SQLite / PostgreSQL | Conforme ambiente |

## Início Rápido

```bash
# 1. Clonar
git clone <url> ende_platform
cd ende_platform

# 2. Ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Dependências
pip install -r requirements.txt

# 4. Configurar .env
copy .env.example .env

# 5. Migrar e iniciar
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Aceder em **http://localhost:8000**

## Credenciais Padrão

| Utilizador | Senha | Tipo |
|---|---|---|
| admin | admin123 | Administrador |

## Documentação Completa

- [`DOCUMENTACAO.md`](DOCUMENTACAO.md) — documentação técnica detalhada
- [`MANUAL_USUARIO.md`](MANUAL_USUARIO.md) — guia para utilizadores finais
- [`checklist_deploy.md`](checklist_deploy.md) — passos para produção

## Estrutura do Projecto

```
ende_platform/          # Configuração principal
├── users/              # Autenticação e RBAC
├── customers/          # Gestão de clientes
├── billing_app/        # Faturação
├── payments/           # Pagamentos e API REST
├── support/            # Suporte (tickets)
├── notifications/      # Notificações in-app
└── templates/          # Templates Bootstrap 5
```

## API REST

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/customers/` | Listar clientes |
| GET | `/api/customers/<id>/` | Detalhe do cliente |
| GET | `/api/invoices/` | Listar faturas |
| GET | `/api/transactions/` | Listar transacções |
| POST | `/api/recharge/` | Recarregar saldo |
| POST | `/api/pay-invoice/` | Pagar fatura |

## Licença

Projecto académico — PAP do curso Técnico de Informática de Gestão, IMCL.
