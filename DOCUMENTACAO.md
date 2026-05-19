# ENDE Platform — Documentação do Projecto

## Índice

- [Visão Geral](#visão-geral)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projecto](#estrutura-do-projecto)
- [Fase 1 — Preparação do Ambiente](#fase-1--preparação-do-ambiente)
- [Fase 2 — Modelagem de Dados e ORM](#fase-2--modelagem-de-dados-e-orm)
- [Fase 3 — Backend e Lógica de Negócio](#fase-3--backend-e-lógica-de-negócio)
- [Fase 4 — Frontend com Bootstrap 5](#fase-4--frontend-com-bootstrap-5)
- [Fase 5 — Segurança, Testes e Validação](#fase-5--segurança-testes-e-validação)
- [Fase 6 — Implantação e Documentação](#fase-6--implantação-e-documentação)
- [Como Executar](#como-executar)
- [Acessando a Aplicação](#acessando-a-aplicação)
- [Estrutura de URLs](#estrutura-de-urls)
- [Modelo de Dados](#modelo-de-dados)
- [API REST](#api-rest)

---

## Visão Geral

A **ENDE Platform** é um sistema web para gestão de clientes de energia eléctrica, desenvolvido em Django. A plataforma atende dois tipos de clientes:

- **Pré-pago**: clientes que recarregam saldo e consomem conforme o crédito disponível.
- **Pós-pago**: clientes que recebem faturas mensais e efectuam pagamentos.

O sistema inclui funcionalidades de consulta de saldo, recarga, pagamento de faturas, histórico de transacções, abertura de tickets de suporte e notificações in-app.

---

## Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|---|---|---|
| Python | 3.12+ | Linguagem de programação |
| Django | 6.0.5 | Framework web |
| Django REST Framework | 3.x | API REST |
| SQLite | 3.x | Banco de dados (desenvolvimento) |
| Bootstrap 5.3 | 5.3.3 | Framework frontend |
| Chart.js | 4.4.7 | Gráficos |
| Bootstrap Icons | 1.11.3 | Iconografia |

---

## Estrutura do Projecto

```
D:\Projects\AngoPower\
├── .env                          # Variáveis de ambiente
├── manage.py                     # Script de gestão do Django
├── DOCUMENTACAO.md               # Este documento
├── db.sqlite3                    # Banco de dados SQLite
├── inctruções.json               # Plano do projecto (fases/tarefas)
├── ende_platform/                # Configuração principal do Django
│   ├── settings.py               # Configurações do projecto
│   ├── urls.py                   # Rotas principais
│   ├── wsgi.py                   # WSGI entry point
│   ├── context_processors.py     # Context processors (notificações)
│   └── asgi.py                   # ASGI entry point
├── users/                        # App de utilizadores
│   ├── models.py                 # CustomUser (RBAC)
│   ├── views.py                  # Register view
│   ├── forms.py                  # CustomUserCreationForm
│   └── urls.py                   # Rotas de utilizadores
├── customers/                    # App de clientes
│   ├── models.py                 # Customer (pré/pós-pago)
│   ├── views.py                  # Dashboard, saldo, recarga, histórico
│   └── urls.py                   # Rotas de clientes
├── billing_app/                  # App de facturação
│   ├── models.py                 # Invoice
│   ├── views.py                  # Faturas, pagamento, consumo
│   └── urls.py                   # Rotas de facturação
├── payments/                     # App de pagamentos
│   ├── models.py                 # Transaction
│   ├── services.py               # Lógica de processamento de pagamentos
│   ├── api_views.py              # API REST endpoints
│   ├── api_urls.py               # Rotas da API
│   └── serializers.py            # Serializers DRF
├── support/                      # App de suporte
│   ├── models.py                 # Category, Ticket, Message
│   ├── views.py                  # Tickets (CRUD + mensagens)
│   └── urls.py                   # Rotas de suporte
├── notifications/                # App de notificações
│   ├── models.py                 # Notification
│   ├── views.py                  # Listar, marcar lida, marcar todas
│   └── urls.py                   # Rotas de notificações
└── templates/                    # Templates HTML
    ├── base.html                 # Template base (Bootstrap 5)
    ├── registration/             # Templates de autenticação
    │   ├── login.html
    │   ├── register.html
    │   ├── password_reset_form.html
    │   ├── password_reset_done.html
    │   ├── password_reset_confirm.html
    │   ├── password_reset_complete.html
    │   ├── password_change_form.html
    │   └── password_change_done.html
    ├── customers/                # Templates de clientes
    │   ├── dashboard.html
    │   ├── balance.html
    │   ├── recharge.html
    │   ├── transaction_history.html
    │   └── no_profile.html
    ├── billing/                  # Templates de facturação
    │   ├── invoice_list.html
    │   ├── invoice_detail.html
    │   ├── pay_invoice.html
    │   └── consumption_history.html
    ├── support/                  # Templates de suporte
    │   ├── ticket_list.html
    │   ├── ticket_detail.html
    │   └── ticket_create.html
    └── notifications/            # Templates de notificações
        └── list.html
```

---

## Fase 1 — Preparação do Ambiente

### 1.1 Ambiente Virtual e Dependências

- Criado ambiente virtual Python (`venv/`)
- Instaladas as dependências: Django 6.0.5, djangorestframework, python-dotenv
- Configurado `.env` para separar configurações sensíveis do código

### 1.2 Inicialização do Projecto

- Projecto Django iniciado: `django-admin startproject ende_platform .`
- Apps criados: `users`, `customers`, `payments`, `support`, `billing_app`, `notifications`

### 1.3 Configuração do Banco de Dados

- Banco configurado via variáveis de ambiente (`.env`)
- Engine definida como SQLite para desenvolvimento (`DB_ENGINE`)
- Nome da base de dados definido em `DB_NAME`

---

## Fase 2 — Modelagem de Dados e ORM

### 2.1 Modelo de Utilizadores (`users/models.py`)

- `CustomUser` estende `AbstractUser`
- Campo adicional: `user_type` com choices `client`, `operator`, `admin`
- `AUTH_USER_MODEL = 'users.CustomUser'` configurado em `settings.py`

### 2.2 Modelo de Clientes (`customers/models.py`)

- `Customer` vinculado 1:1 com `CustomUser`
- Campos:
  - `customer_type`: `prepaid` ou `postpaid`
  - `meter_number`: único, identificador do medidor
  - `current_balance`: saldo actual (Decimal)
  - `debt`: dívida pendente (Decimal)
  - `phone`, `address`: dados de contacto

### 2.3 Modelo de Facturação (`billing_app/models.py`)

- `Invoice` vinculada a `Customer`
- Campos:
  - `invoice_number`: único, gerado automaticamente
  - `amount`: valor total da factura
  - `paid_amount`: valor já pago
  - `status`: draft, issued, paid, overdue, partially_paid
  - `issue_date`, `due_date`: datas de emissão e vencimento
  - `description`: descrição opcional

### 2.4 Modelo de Transacções (`payments/models.py`)

- `Transaction` vinculada a `Customer` e opcionalmente a `Invoice`
- Campos:
  - `transaction_id`: UUID único
  - `transaction_type`: payment, credit, refund, adjustment
  - `amount`: valor da transacção
  - `status`: pending, completed, failed
  - `description`: descrição opcional
  - `idempotency_key`: chave de idempotência (opcional)

### 2.5 Modelo de Suporte (`support/models.py`)

- `Category`: categorias de tickets
- `Ticket`: vinculado a `Customer`, com subject, description, priority (low/medium/high/urgent), status (open/in_progress/resolved/closed), assigned_to
- `Message`: mensagens dentro de um ticket, vinculadas a `Ticket` e `User`

### 2.6 Modelo de Notificações (`notifications/models.py`)

- `Notification`: vinculada a `User`
- Campos: type (recharge/invoice/ticket/payment/system), title, message, is_read, link

### 2.7 Migrações

- Todas as migrações criadas e aplicadas (17 migrações)
- Superuser criado: `admin` / `admin123`

---

## Fase 3 — Backend e Lógica de Negócio

### 3.1 Serviço de Pagamentos (`payments/services.py`)

Função principal `process_payment()`:
- Transacção atómica com `select_for_update()` para evitar race conditions
- Verificação de idempotência via `idempotency_key`
- Actualização de saldo do cliente e/ou estado da factura
- Criação automática de notificação para o utilizador

Funções auxiliares:
- `recharge_balance(customer_id, amount)`: recarga de saldo pré-pago
- `pay_invoice(invoice_id, amount)`: pagamento de factura pós-pago

### 3.2 Views de Clientes Pré-pago (`customers/views.py`)

| Rota | Função | Descrição |
|---|---|---|
| `/customers/` | `dashboard` | Visão geral com saldo, dívida, transacções recentes |
| `/customers/balance/` | `check_balance` | Consulta detalhada de saldo |
| `/customers/recharge/` | `request_recharge` | Formulário de recarga com processamento |
| `/customers/transactions/` | `transaction_history` | Histórico completo de transacções |

### 3.3 Views de Clientes Pós-pago (`billing_app/views.py`)

| Rota | Função | Descrição |
|---|---|---|
| `/billing/` | `invoice_list` | Lista de facturas com status e valores |
| `/billing/<pk>/` | `invoice_detail` | Detalhe da factura + transacções relacionadas |
| `/billing/<pk>/pay/` | `pay_invoice_view` | Pagamento de factura (parcial ou total) |
| `/billing/consumption/` | `consumption_history` | Histórico de consumo |

### 3.4 Views de Suporte (`support/views.py`)

| Rota | Função | Descrição |
|---|---|---|
| `/support/` | `ticket_list` | Lista de tickets do cliente |
| `/support/<pk>/` | `ticket_detail` | Detalhe do ticket + mensagens |
| `/support/create/` | `ticket_create` | Criação de novo ticket |

### 3.5 Views de Notificações (`notifications/views.py`)

| Rota | Função | Descrição |
|---|---|---|
| `/notifications/` | `notification_list` | Lista de notificações |
| `/notifications/<pk>/read/` | `mark_read` | Marcar notificação como lida |
| `/notifications/read-all/` | `mark_all_read` | Marcar todas como lidas |

### 3.6 API REST (`payments/api_views.py`)

Endpoints disponíveis:

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/customers/` | Listar todos os clientes |
| GET | `/api/customers/<id>/` | Detalhe de um cliente |
| GET | `/api/invoices/` | Listar facturas |
| GET | `/api/transactions/` | Listar transacções |
| POST | `/api/recharge/` | Recarregar saldo |
| POST | `/api/pay-invoice/` | Pagar factura |

- Permissões: `IsAuthenticated` + `IsCustomerOwner` (acesso restrito ao próprio cliente)
- Autenticação via sessão (SessionAuthentication)

---

## Fase 4 — Frontend com Bootstrap 5

### 4.1 Template Base

- `base.html` reescrito com Bootstrap 5.3 via CDN
- Navbar responsiva: collapse em mobile, dropdown do utilizador em desktop
- Footer fixo com direitos reservados
- Mensagens Django convertidas em alerts Bootstrap no canto superior direito
- Auto-dismiss de mensagens após 5 segundos
- Validação client-side via classe `was-validated`
- Ícones Bootstrap Icons em toda a interface

### 4.2 Autenticação

- **Login**: formulário com input groups, link para recuperar senha e cadastro
- **Cadastro**: formulário com todos os campos do `CustomUserCreationForm`, feedback de erros
- **Recuperação de senha**: fluxo completo com 4 templates (solicitação, confirmação de envio, redefinição, conclusão)
- **Alteração de senha**: formulário com senha actual + nova senha + confirmação

### 4.3 Dashboard

- 4 stat cards com ícones: saldo, dívida, medidor, tipo de conta
- Efeito hover nos cards (elevação suave)
- Grid de acções rápidas com botões estilizados
- Tabela de transacções recentes com badges de status coloridos
- Mensagem "vazia" com ícone quando não há dados

### 4.4 Formulários

- **Recarga**: input group com prefixo `$`, validação de valor positivo
- **Pagamento**: exibe total/pago/restante em cards, input com min/max dinâmico
- **Ticket**: selects estilizados com `form-select`, textarea com placeholder
- **Mensagens**: chat UI com avatar circular, nome do autor, timestamp

### 4.5 Visualização de Dados

- **Chart.js**: gráfico de barras do consumo mensal
- **Cards de resumo**: total de transacções, consumo total, média mensal
- **Tabelas**: responsivas, linhas com hover, badges por tipo/status
- **Notificações**: list-group com ícones por tipo, badge "NOVA" para não lidas, auto-scroll

---

## Fase 5 — Segurança, Testes e Validação

### 5.1 Segurança (P5-T1)

**Rate Limiting**
- Middleware `ende_platform.middleware.RateLimitMiddleware`
- Limita POST requests a 10 por minuto nos endpoints sensíveis (`/login/`, `/customers/recharge/`, `/billing/`, `/api/recharge/`, `/api/pay-invoice/`)
- Baseado em IP (suporta `X-Forwarded-For` atrás de proxies)

**Protecção de Sessão**
- `SESSION_COOKIE_HTTPONLY = True` — cookies de sessão inacessíveis via JavaScript
- `SESSION_COOKIE_SAMESITE = 'Lax'` — protecção contra CSRF entre sites
- `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` — sessão expira ao fechar o navegador
- `CSRF_COOKIE_HTTPONLY = True`
- `CSRF_COOKIE_SAMESITE = 'Lax'`

**Headers HTTP**
- `SECURE_CONTENT_TYPE_NOSNIFF = True` — evita MIME sniffing
- `SECURE_BROWSER_XSS_FILTER = True` — activa filtro XSS do navegador

**Protecções Django**
- `CsrfViewMiddleware` — protecção CSRF em todos os formulários
- `XFrameOptionsMiddleware` — evita clickjacking
- `SecurityMiddleware` — várias protecções de segurança
- Templates com auto-escaping (nenhum `|safe` nos templates)

### 5.2 Testes Unitários e de Integração (P5-T2)

**76 testes**, todos passando:

| App | Testes | Cobertura |
|---|---|---|
| users | 9 | Criação de utilizadores, registo, validação |
| customers | 12 | Modelo, dashboard, saldo, recarga, transacções |
| billing_app | 11 | Modelo, listar faturas, detalhe, pagamento, consumo |
| payments | 17 | Modelo, serviços (process_payment, pay_invoice, recharge_balance), API |
| support | 14 | Modelo, tickets, mensagens, permissões |
| notifications | 11 | Modelo, listar, marcar lida, marcar todas |

Para executar:

```bash
python manage.py test --verbosity=2
```

### 5.3 Testes de Usabilidade (P5-T3)

Cenários simulados nos testes de integração:

1. **Cliente pré-pago**: consulta saldo → recarrega → vê histórico de transacções
2. **Cliente pós-pago**: lista faturas → vê detalhe → paga fatura → vê consumo
3. **Suporte**: abre ticket → adiciona mensagem
4. **Segurança**: utilizador não autenticado é redirecionado; acesso a recursos alheios retorna 404
5. **Perfil**: utilizador sem perfil de cliente vê página "no_profile"

### 5.4 Performance (P5-T4)

**Otimizações de queries:**
- `select_related('category')` na listagem de tickets (evita N+1 na categoria)
- `prefetch_related('transactions')` no detalhe da fatura
- `prefetch_related('messages__author')` no detalhe do ticket

**Índices de base de dados adicionados:**
- `Transaction`: `status`, `created_at`, índice composto (`transaction_type`, `status`)
- `Invoice`: `status`, `issue_date`
- `Ticket`: `priority`, `status`
- `Notification`: `is_read`, `created_at`

---

## Fase 6 — Implantação e Documentação

### 6.1 Ambiente de Produção (P6-T1)

**Ficheiros criados:**
- `.env.example` — template de configuração para produção
- `checklist_deploy.md` — guia passo-a-passo com Nginx, Gunicorn, PostgreSQL
- `deploy.ps1` — script de deploy automatizado para Windows
- `requirements.txt` — dependências fixadas

**Configuração de produção recomendada:**

```env
DEBUG=False
SECRET_KEY=<chave-gerada-aleatoriamente>
ALLOWED_HOSTS=.seuservidor.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ende_db
DB_USER=ende_user
DB_PASSWORD=<senha-forte>
DB_HOST=localhost
DB_PORT=5432
```

### 6.2 Documentação Técnica (P6-T2)

- `DOCUMENTACAO.md` — documentação completa do projecto (este ficheiro)
- `README.md` — visão geral rápida para o repositório
- `checklist_deploy.md` — guia de implantação

### 6.3 Manual do Utilizador (P6-T3)

- `MANUAL_USUARIO.md` — guia ilustrado para clientes e operadores

### 6.4 Apresentação PAP (P6-T4)

- `APRESENTACAO.md` — slides em markdown para a Prova de Aptidão Profissional

### 6.5 Exportação e Backup (P6-T5)

- `backup_db.ps1` — script de backup do banco de dados
- Arquivo ZIP do projecto via `git archive`

---

## Como Executar

### Pré-requisitos

- Python 3.12 ou superior
- Git (opcional)

### Passos

1. **Criar e activar o ambiente virtual**

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Instalar as dependências**

```bash
pip install django djangorestframework python-dotenv
```

3. **Configurar o ficheiro `.env`**

O ficheiro `.env` na raiz do projecto deve conter:

```env
SECRET_KEY=django-insecure-fd9#=%fal&k9_v4=vd&mxc=t!%gj5qup@kiwpc&4abo90-q(6%
DEBUG=True
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

4. **Executar as migrações**

```bash
python manage.py migrate
```

5. **Criar o superuser (admin)**

```bash
python manage.py createsuperuser
```

6. **Iniciar o servidor de desenvolvimento**

```bash
python manage.py runserver 0.0.0.0:8000
```

7. **Aceder à aplicação**

Abra o navegador em `http://localhost:8000`

---

## Acessando a Aplicação

### Credenciais Padrão

| Utilizador | Senha | Tipo |
|---|---|---|
| admin | admin123 | Administrador (staff) |

Para criar clientes de teste, aceda ao admin em `http://localhost:8000/admin/` e crie:
1. Um `CustomUser` com `user_type = client`
2. Um `Customer` vinculado a esse utilizador

### URLs Principais

| URL | Descrição |
|---|---|
| `/` | Redirecciona para Dashboard |
| `/admin/` | Painel de administração Django |
| `/login/` | Página de login |
| `/register/` | Página de cadastro |
| `/password-reset/` | Recuperação de senha |
| `/customers/` | Dashboard do cliente |
| `/customers/balance/` | Consulta de saldo |
| `/customers/recharge/` | Recarga de saldo |
| `/customers/transactions/` | Histórico de transacções |
| `/billing/` | Lista de facturas |
| `/billing/<pk>/` | Detalhe da factura |
| `/billing/<pk>/pay/` | Pagar factura |
| `/billing/consumption/` | Histórico de consumo |
| `/support/` | Lista de tickets |
| `/support/create/` | Novo ticket |
| `/notifications/` | Notificações |
| `/api/customers/` | API: lista de clientes |
| `/api/invoices/` | API: lista de facturas |
| `/api/transactions/` | API: lista de transacções |
| `/api/recharge/` | API: recarga |
| `/api/pay-invoice/` | API: pagamento de factura |

---

## Modelo de Dados

### Relacionamentos

```
CustomUser (AbstractUser)
    │
    └── 1:1 ── Customer
                    │
                    ├── 1:N ── Invoice
                    │             │
                    │             └── 1:N ── Transaction
                    │
                    ├── 1:N ── Transaction (direct transactions)
                    │
                    └── 1:N ── Ticket
                                    │
                                    └── 1:N ── Message

CustomUser
    │
    └── 1:N ── Notification
```

### Campos por Modelo

**CustomUser**
| Campo | Tipo | Descrição |
|---|---|---|
| username | CharField | Nome de utilizador (herdado) |
| email | EmailField | E-mail (herdado) |
| password | CharField | Senha (herdado) |
| user_type | CharField | client / operator / admin |
| date_joined | DateTimeField | Data de registo (herdado) |

**Customer**
| Campo | Tipo | Descrição |
|---|---|---|
| user | OneToOneField(CustomUser) | Utilizador associado |
| customer_type | CharField | prepaid / postpaid |
| meter_number | CharField(unique) | Número do medidor |
| current_balance | DecimalField | Saldo actual |
| debt | DecimalField | Dívida pendente |
| phone | CharField | Telefone |
| address | TextField | Endereço |

**Invoice**
| Campo | Tipo | Descrição |
|---|---|---|
| customer | ForeignKey(Customer) | Cliente associado |
| invoice_number | CharField(unique) | Número da factura |
| amount | DecimalField | Valor total |
| paid_amount | DecimalField | Valor pago |
| status | CharField | draft/issued/paid/overdue/partially_paid |
| issue_date | DateField | Data de emissão |
| due_date | DateField | Data de vencimento |
| description | TextField | Descrição |

**Transaction**
| Campo | Tipo | Descrição |
|---|---|---|
| customer | ForeignKey(Customer) | Cliente associado |
| invoice | ForeignKey(Invoice, nullable) | Factura associada |
| transaction_id | UUIDField | ID único da transacção |
| transaction_type | CharField | payment/credit/refund/adjustment |
| amount | DecimalField | Valor |
| status | CharField | pending/completed/failed |
| description | TextField | Descrição |
| idempotency_key | CharField(nullable) | Chave de idempotência |

**Ticket**
| Campo | Tipo | Descrição |
|---|---|---|
| customer | ForeignKey(Customer) | Cliente associado |
| category | ForeignKey(Category, nullable) | Categoria |
| subject | CharField | Assunto |
| description | TextField | Descrição |
| priority | CharField | low/medium/high/urgent |
| status | CharField | open/in_progress/resolved/closed |
| assigned_to | ForeignKey(User, nullable) | Operador responsável |

**Message**
| Campo | Tipo | Descrição |
|---|---|---|
| ticket | ForeignKey(Ticket) | Ticket associado |
| author | ForeignKey(User) | Autor da mensagem |
| content | TextField | Conteúdo |
| created_at | DateTimeField | Data de criação |

**Notification**
| Campo | Tipo | Descrição |
|---|---|---|
| user | ForeignKey(User) | Utilizador destino |
| type | CharField | recharge/invoice/ticket/payment/system |
| title | CharField | Título |
| message | TextField | Mensagem |
| is_read | BooleanField | Lida ou não |
| link | CharField(nullable) | Link opcional |
| created_at | DateTimeField | Data de criação |

---

## API REST

### Autenticação

A API utiliza SessionAuthentication. As requisições devem incluir o cookie de sessão ou o cabeçalho `Authorization: Session <sessionid>`.

### Endpoints

**`GET /api/customers/`**
- Retorna lista de clientes
- Filtrado pelo utilizador autenticado

**`GET /api/customers/<id>/`**
- Retorna detalhe do cliente
- Apenas o próprio cliente ou staff

**`GET /api/invoices/`**
- Lista facturas do cliente autenticado

**`GET /api/transactions/`**
- Lista transacções do cliente autenticado

**`POST /api/recharge/`**
- Body: `{"amount": 100.00}`
- Processa recarga de saldo pré-pago

**`POST /api/pay-invoice/`**
- Body: `{"invoice_id": 1, "amount": 50.00}`
- Processa pagamento de factura

### Permissões

- `IsAuthenticated`: todas as requisições exigem autenticação
- `IsCustomerOwner`: clientes só acedem aos próprios dados
- Operadores e admins têm acesso global via `IsStaffOrOwner`
