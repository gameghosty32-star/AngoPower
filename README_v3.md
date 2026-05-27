# ENDE Platform v3

Sistema web integrado para gestão de clientes de energia eléctrica da **ENDE-EP, Angola**.

---

## Credenciais Padrão

| Utilizador | Senha | Tipo | Acesso |
|---|---|---|---|
| `admin` | `admin123` | Administrador | Dashboard Admin + Django Admin + área cliente |
| `operador` | `operador123` | Operador | Painel do Agente + área cliente |
| `cliente` | `cliente123` | Cliente (pré-pago) | Dashboard pré-pago |

> Altere todas as senhas em produção.

---

## Início Rápido

```bash
git clone <url> ende_platform && cd ende_platform
python -m venv venv
.\venv\Scripts\Activate.ps1
.\venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.\venv\Scripts\python manage.py migrate
.\venv\Scripts\python manage.py loaddata support/fixtures/categories.json
.\venv\Scripts\python manage.py loaddata payment_gateways/fixtures/gateways.json
.\venv\Scripts\python manage.py shell -c "
from users.models import CustomUser
CustomUser.objects.create_superuser('admin', 'admin@ende.ao', 'admin123', user_type='admin')
CustomUser.objects.create_user('operador', 'operador@ende.ao', 'operador123', user_type='operator')
CustomUser.objects.create_user('cliente', 'cliente@ende.ao', 'cliente123', user_type='client')
"
.\venv\Scripts\python manage.py runserver 0.0.0.0:8000
```

Aceder em **http://localhost:8000**

---

## Funcionalidades por App

### `dashboard/` — Gestão Administrativa v3

**Dashboard Admin** (`/dashboard/admin/`)
- Métricas: total clientes, pré-pagos, pós-pagos, receita total, tickets abertos, contratos pendentes
- Acesso rápido a todas as ferramentas de gestão

**Gestão de Clientes** (`/dashboard/customers/`)
- Lista completa de clientes com busca por username, email, contador, telefone
- Edição de dados do cliente: tipo, contador, saldo, dívida, telefone, província, município, endereço
- Exclusão de cliente (remove utilizador + perfil)

**Gestão de Facturas** (`/dashboard/invoices/`)
- Lista de todas as facturas com busca e filtro por status
- Visão consolidada de valores, pagamentos e vencimentos

**Painel do Agente** (`/dashboard/agent/`)
- Tickets com busca, filtros (status, prioridade, categoria), ordenação
- Contagem de tickets por status (abertos, andamento, resolvidos, fechados)
- Detalhe do ticket com resposta, alteração de status e prioridade

**Definições** (`/dashboard/settings/`)
- 4 temas visuais: Vermelho ENDE (padrão), Preto (dark), Branco (clean), Roxo Neon (tech)

### `payment_gateways/` — Pagamentos v3

- Gateways angolanos: Multicaixa Express, Paypay, Unitel Money, Afrimoney
- Simulação 100% bem-sucedida em desenvolvimento
- Download de recibo PDF após pagamento bem-sucedido
- Tratamento de erros robusto com mensagens amigáveis
- Redireccionamento inteligente (saldo para recargas, factura para pagamentos)

### `prepaid/` — Pré-pago

- Dashboard com saldo, consumo diário (Chart.js), transacções recentes
- Recarga via gateways com fluxo completo
- Saldo actualizado automaticamente após confirmação
- Recibo PDF para cada recarga
- Consulta de saldo e histórico de transacções

### `postpaid/` — Pós-pago

- Dashboard com dívida total e facturas pendentes
- Botão **Pagar** directo no dashboard e na lista de facturas
- Pagamento de facturas via gateways angolanos
- PDF da dívida actual (relatório completo com todas as facturas pendentes)
- Activação de contrato (vistoria ou sugestão de sistema)
- Histórico de consumo

### `billing_app/` — Facturação

- PDF nativo com ReportLab (avisos de vencimento, recibos de pagamento, recibos de recarga, relatório de dívida)
- Envio de email com PDF anexo
- Notificações in-app integradas
- Comandos de gestão: `generate_due_notices`, `generate_overdue_notices`

### `support/` — Suporte

- 6 categorias com SLA (Avaria Técnica: 4h, Recarga Não Creditada: 2h, etc.)
- Protocolo automático `END-yyyyMMdd-XXXX`
- Notificações automáticas na criação do ticket
- Painel do agente com busca, filtros, ordenação
- SLA calculado e verificado com deadlines

### `notifications/` — Notificações

- Tipos: recarga, factura, ticket, pagamento, sistema
- Badge de contagem não lida no menu
- Marcar como lida / marcar todas

---

## Temas Visuais

4 temas disponíveis em `/dashboard/settings/`:

| Tema | Descrição | Cor Primária |
|---|---|---|
| Vermelho ENDE | Padrão institucional | `#E30613` |
| Preto | Dark mode | `#0d6efd` |
| Branco | Clean minimalista | `#212529` |
| Roxo Neon | Tech com glow | `#a855f7` |

A escolha é guardada em `localStorage` e persiste entre sessões.

---

## Estrutura do Projecto

```
ende_platform/
├── users/              # Modelo CustomUser (admin, operator, client)
├── customers/          # Modelo Customer + templatetags
├── prepaid/            # Lógica pré-pago
├── postpaid/           # Lógica pós-pago (contratos, facturas)
├── billing_app/        # Facturação + PDF (ReportLab)
├── payments/           # Pagamentos + API REST
├── payment_gateways/   # Gateways angolanos
├── support/            # Suporte com SLA
├── notifications/      # Notificações in-app
├── dashboard/          # Gestão administrativa v3
│   ├── admin dashboard
│   ├── customer CRUD
│   ├── invoice list
│   ├── agent dashboard
│   └── settings (themes)
├── utils/              # Angola data (províncias, Kz, telefone)
├── templates/          # Bootstrap 5 mobile-first
└── static/
    ├── css/
    │   ├── ende_theme.css      # Design system com CSS variables
    │   └── themes/
    │       ├── red.css          # Tema vermelho ENDE
    │       ├── black.css        # Tema preto dark
    │       ├── white.css        # Tema branco clean
    │       └── purple.css       # Tema roxo neon
    ├── js/
    ├── img/gateways/   # Logos dos gateways
    └── manifest.json   # PWA
```

---

## Comandos Úteis

```bash
# Carregar dados iniciais
python manage.py loaddata support/fixtures/categories.json
python manage.py loaddata payment_gateways/fixtures/gateways.json

# Notificações de vencimento
python manage.py generate_due_notices
python manage.py generate_overdue_notices

# Testes (68 testes)
python manage.py test

# Produção
python manage.py collectstatic --noinput
.\deploy.ps1 -Start
```

---

## Alterações da v3

### 1. Dashboard Administrativo Completo
- Gestão CRUD de clientes e contadores (listar, editar, excluir)
- Lista de facturas com busca e filtro
- Painel de métricas objectivo (sem info desnecessária de cliente)
- Navegação rápida entre ferramentas de gestão

### 2. Painel do Agente Melhorado
- Detalhe do ticket com resposta inline
- Alteração de status e prioridade sem sair da página
- Contagem de tickets por status
- Destaque visual para tickets urgentes

### 3. Recargas e Pagamentos Corrigidos
- Gateway simulado com 100% de sucesso em desenvolvimento
- Tratamento de erros com mensagens amigáveis
- Download de recibo PDF após pagamento
- Redireccionamento para saldo (recarga) ou factura (pagamento)

### 4. Pagamento no Pós-pago
- Botão **Pagar** adicionado no dashboard (por factura pendente)
- Botão **Pagar Facturas Pendentes** nas acções rápidas
- Fluxo completo: dashboard → gateway → confirmação → recibo PDF

### 5. Sistema de Temas (4 temas)
- Vermelho ENDE (padrão institucional)
- Preto (dark mode completo)
- Branco (clean minimalista)
- Roxo Violeta Tech Neon (com glow e efeitos neon)
- Guardado em localStorage, persiste entre sessões
- Disponível em `/dashboard/settings/`

### 6. Tecnologias
| Tecnologia | Versão |
|---|---|
| Python | 3.12+ |
| Django | 6.0.5 |
| Django REST Framework | 3.x |
| Bootstrap | 5.3.3 |
| Chart.js | 4.4.7 |
| ReportLab | 4.x |
| SQLite / PostgreSQL | — |
