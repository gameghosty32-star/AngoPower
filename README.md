# ENDE Platform

Sistema web integrado para gestão de clientes de energia eléctrica da **ENDE-EP, Angola**. Plataforma para clientes **pré-pago** e **pós-pago** com recarga via carteiras móveis angolanas, faturação, pagamentos, suporte com SLA, notificações e interface mobile-first.

---

## Credenciais Padrão

| Utilizador | Senha | Tipo | Acesso |
|---|---|---|---|
| `admin` | `admin123` | Administrador | `/admin/` + área de cliente |
| `operador` | `operador123` | Operador | Painel de tickets + área de cliente |
| `cliente` | `cliente123` | Cliente (pré-pago) | Dashboard pré-pago |

> **Importante**: Altere todas as senhas em produção.

---

## Funcionalidades

### Clientes Pré-pago
- Dashboard com saldo, medidor, consumo diário (Chart.js)
- Consulta de saldo detalhada
- Recarga via gateways angolanos (Multicaixa Express, Paypay, Unitel Money, Afrimoney)
- Histórico de transacções com filtros
- Recibo de recarga em PDF

### Clientes Pós-pago
- Dashboard com dívida total e faturas pendentes
- Listagem e detalhe de faturas com histórico de pagamentos
- Pagamento de faturas via gateways angolanos
- Ativação de contrato pós-pago (vistoria ou sugestão de sistema)
- Histórico de consumo
- Recibo de pagamento em PDF
- Notificações de vencimento (automáticas via comando)

### Gateway de Pagamentos
- 4 gateways angolanos: Multicaixa Express, Paypay, Unitel Money, Afrimoney
- Simulação de processamento (90% sucesso / 10% falha)
- Transacções registadas com rastreabilidade

### Suporte ao Cliente
- 6 categorias com SLA (Avaria Técnica: 4h, Recarga Não Creditada: 2h, etc.)
- Protocolo automático no formato `END-yyyyMMdd-XXXX`
- Notificações automáticas na criação do ticket
- Painel do operador com busca, filtro por status/categoria e ordenação
- SLA calculado e verificado com deadlines

### Notificações
- Notificações in-app em tempo real
- Tipos: recarga, fatura, ticket, pagamento, sistema
- Badge de contagem não lida no menu
- Marcar como lida / marcar todas como lidas

### Angola
- Todas as 18 províncias e +150 municípios
-- Formatação de moeda Kz com `|format_kz`
- Validação de telefone angolano (+244)
- Fuso horário `Africa/Luanda`, locale `pt-AO`
- Formulário de registo com selects dependentes província → município

### Interface
- Tema mobile-first com design system CSS variables (cores ENDE)
- Animações e ripple effect em botões
- PWA manifest para instalação em dispositivo móvel
- Bootstrap 5.3.3 + Bootstrap Icons
- Chart.js 4.4.7 com auto-refresh a cada 30s
- Gráfico de consumo diário no dashboard pré-pago

### API REST
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/customers/` | Listar clientes |
| GET | `/api/customers/<id>/` | Detalhe do cliente |
| GET | `/api/invoices/` | Listar faturas |
| GET | `/api/transactions/` | Listar transacções |
| POST | `/api/recharge/` | Recarregar saldo |
| POST | `/api/pay-invoice/` | Pagar fatura |

---

## Tecnologias

| Tecnologia | Versão |
|---|---|
| Python | 3.12+ |
| Django | 6.0.5 |
| Django REST Framework | 3.x |
| Bootstrap | 5.3.3 (CDN) |
| Chart.js | 4.4.7 |
| ReportLab | 4.x (PDF) |
| SQLite (dev) / PostgreSQL (prod) | — |

---

## Início Rápido

```bash
# 1. Clonar e aceder
git clone <url> ende_platform
cd ende_platform

# 2. Ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # Linux/Mac

# 3. Dependências
.\venv\Scripts\pip install -r requirements.txt

# 4. Configurar .env
copy .env.example .env

# 5. Migrar e carregar dados iniciais
.\venv\Scripts\python manage.py migrate
.\venv\Scripts\python manage.py loaddata support/fixtures/categories.json
.\venv\Scripts\python manage.py loaddata payment_gateways/fixtures/gateways.json

# 6. Criar utilizadores
.\venv\Scripts\python manage.py shell -c "
from users.models import CustomUser
CustomUser.objects.create_superuser('admin', 'admin@ende.ao', 'admin123', user_type='admin')
CustomUser.objects.create_user('operador', 'operador@ende.ao', 'operador123', user_type='operator')
CustomUser.objects.create_user('cliente', 'cliente@ende.ao', 'cliente123', user_type='client')
"

# 7. Iniciar servidor
.\venv\Scripts\python manage.py runserver 0.0.0.0:8000
```

Aceder em **http://localhost:8000**

---

## Comandos Úteis

```bash
# Gerar notificações de vencimento para faturas próximas do prazo
.\venv\Scripts\python manage.py generate_due_notices

# Gerar notificações para faturas vencidas
.\venv\Scripts\python manage.py generate_overdue_notices

# Executar testes
.\venv\Scripts\python manage.py test

# Recolher estáticos para produção
.\venv\Scripts\python manage.py collectstatic --noinput

# Deploy rápido (Windows)
.\deploy.ps1 -Start
```

---

## Arquitectura

```
ende_platform/              # Configuração principal
├── users/                  # Autenticação e RBAC (admin, operator, client)
├── customers/              # Modelo central Customer, templatetags, formulários
├── prepaid/                # Lógica pré-pago (dashboard, saldo, recarga)
├── postpaid/               # Lógica pós-pago (contratos, faturas, consumo)
├── billing_app/            # Motor de faturação + gerador PDF (ReportLab)
├── payments/               # Processamento de pagamentos + API REST
├── payment_gateways/       # Gateways angolanos (modelos, fixture, simulação)
├── support/                # Suporte com categorias, SLA, protocolo
├── notifications/          # Notificações in-app
├── utils/                  # Angola data (províncias, municípios, Kz, telefone)
├── templates/              # Templates Bootstrap 5 (mobile-first)
└── static/                 # CSS, JS, PWA manifest, imagens dos gateways
```

### Diagrama de Navegação

```
/login/  →  /customers/dashboard/  (router)
                ├── cliente pré-pago  →  /prepaid/dashboard/
                │                        ├── /prepaid/balance/
                │                        ├── /prepaid/recharge/
                │                        └── /prepaid/transactions/
                └── cliente pós-pago  →  /postpaid/dashboard/
                                           ├── /postpaid/invoices/
                                           ├── /postpaid/invoice/<pk>/
                                           ├── /postpaid/pay/<pk>/
                                           └── /postpaid/consumption/
```

---

## Evoluções (V2)

### Fase 1 — Separação de Domínios
- Criados `prepaid/` e `postpaid/` com views, serviços e templates dedicados
- `customers/views.py` transformado em router com base em `customer.customer_type`
- `billing_app/views.py` redireciona clientes para os novos módulos

### Fase 2 — Gateways Angolanos
- Modelos `PaymentGateway` e `GatewayTransaction`
- 4 gateways: Multicaixa Express, Paypay, Unitel Money, Afrimoney
- Simulação de processamento (90% sucesso)
- Integração nos fluxos de recarga e pagamento de facturas

### Fase 3 — Activação Pós-pago
- Modelo `PostpaidContract` (OneToOne com Customer)
- Formulários de pedido de vistoria e sugestão de sistema (calculadora de electrodomésticos)
- Fluxo: escolha → vistoria/sugestão → pendente → aprovação admin
- Registo de cliente com escolha pré-pago/pós-pago

### Fase 4 — Motor de Facturação
- PDFs com ReportLab: aviso de vencimento, recibo de pagamento, recibo de recarga
- Envio de email com PDF anexo
- Notificações in-app integradas
- Comandos: `generate_due_notices`, `generate_overdue_notices`
- View de download PDF em `/billing/<pk>/pdf/`

### Fase 5 — Suporte Refatorado
- Categoria com slug, ícone, SLA, activo/inactivo
- Protocolo automático `END-yyyyMMdd-XXXX`
- SLA calculado com deadline e verificação de compliance
- Auto-respostas por categoria
- Operator dashboard com busca, filtro, ordenação
- 6 categorias carregadas via fixture

### Fase 6 — Angolanização Total
- `utils/angola.py`: 18 províncias, +150 municípios, `format_kz()`, validação de telefone
- `LANGUAGE_CODE=pt-ao`, `TIMEZONE=Africa/Luanda`
- Template filter `|format_kz` e context processor `angola_context`
- `CustomerOnboardingForm` com selects dependentes e máscara de telefone
- Símbolo `$` substituído por `Kz` em todos os templates

### Fase 7 — Interface Mobile-First
- Design system com CSS variables (cores ENDE `#E30613`)
- Animações, ripple effect, breakpoints mobile-first (576px, 768px, 992px)
- PWA manifest para instalação em dispositivo móvel
- Chart.js com auto-refresh a cada 30s no dashboard pré-pago

---

## Estrutura do Banco de Dados

```
CustomUser (users)
    └── Customer (customers) [OneToOne]
            ├── PostpaidContract (postpaid) [OneToOne, opcional]
            ├── Invoice (billing_app) [FK]
            ├── Transaction (payments) [FK]
            ├── Ticket (support) [FK]
            ├── Notification (notifications) [FK]
            └── GatewayTransaction (payment_gateways) [FK]
```

---

## Licença

Projecto académico — PAP do curso Técnico de Informática de Gestão, IMCL.
