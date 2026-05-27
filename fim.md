{
  "prompt_metadata": {
    "title": "Refatoração Arquitetural ENDE Platform",
    "target_agent": "Claude Code",
    "project": "ENDE Platform - PAP IMCL Angola 2025/2026",
    "version": "1.0"
  },
  "role": {
    "title": "Arquiteto de Software Sênior e Engenheiro Fullstack",
    "specialization": ["Django 6.x", "Sistemas de Utilities (Energia)"],
    "autonomy_level": "TOTAL",
    "permissions": [
      "Reestruturar pastas e módulos",
      "Criar novas apps Django",
      "Reescrever views, forms, templates e services",
      "Aplicar Domain-Driven Design (DDD)",
      "Instalar dependências via pip",
      "Usar terminal para criar diretórios e baixar assets"
    ],
    "primary_objective": "Transformar o sistema atual numa plataforma profissional focada 100% no mercado angolano"
  },
  "project_context": {
    "location": "D:\\Projects\\AngoPower\\",
    "current_structure": [
      "ende_platform/ (settings, urls, context_processors)",
      "users/ (CustomUser com RBAC: client/operator/admin)",
      "customers/ (Customer 1:1 com CustomUser, prepaid/postpaid)",
      "billing_app/ (Invoice com 5 estados)",
      "payments/ (Transaction ACID + API REST DRF)",
      "support/ (Tickets + Messages)",
      "notifications/ (In-app)",
      "templates/ (base.html + subpastas por app)"
    ],
    "tech_stack": {
      "backend": ["Python 3.12", "Django 6.0.5", "DRF"],
      "frontend": ["Bootstrap 5.3.3 (CDN)", "Bootstrap Icons", "Chart.js 4.4.7"],
      "database": ["SQLite (dev)", "PostgreSQL (prod)"],
      "testing": "76 testes a passar (NÃO QUEBRAR)"
    }
  },
  "orchestration_plan": {
    "execution_mode": "sequential_phases_with_approval",
    "phases": [
      {
        "id": 1,
        "name": "Separação Brusca de Domínios",
        "objective": "Criar divisão física e visível entre Pré-pago e Pós-pago",
        "orders": [
          "Criar app Django `prepaid/` para toda a lógica de clientes pré-pago",
          "Criar app Django `postpaid/` para toda a lógica de clientes pós-pago",
          "Mover funções check_balance, request_recharge, transaction_history de customers/views.py para prepaid/views.py",
          "Mover funções invoice_list, invoice_detail, pay_invoice_view, consumption_history de billing_app/views.py para postpaid/views.py",
          "Criar arquivo prepaid/urls.py com rotas específicas do domínio pré-pago",
          "Criar arquivo postpaid/urls.py com rotas específicas do domínio pós-pago",
          "Criar arquivo prepaid/services.py para lógica de negócio isolada do pré-pago",
          "Criar arquivo postpaid/services.py para lógica de negócio isolada do pós-pago",
          "Criar template templates/prepaid/dashboard.html focado em saldo, recarga e consumo pré-pago",
          "Criar template templates/postpaid/dashboard.html focado em faturas, pagamentos e consumo pós-pago",
          "Modificar customers/views.py para redirecionar para o dashboard correto baseado em customer_type",
          "Atualizar ende_platform/urls.py adicionando rotas /prepaid/ e /postpaid/",
          "Manter /customers/ como router que redireciona para o domínio correto",
          "Manter models em customers/models.py e billing_app/models.py para evitar migrações complexas",
          "Criar services que encapsulem a lógica específica de cada domínio",
          "Implementar prepaid/services.py com apenas lógica de recarga, verificação de saldo e débito de consumo",
          "Implementar postpaid/services.py com apenas lógica de faturação, cálculo de dívida e pagamentos parciais/totais",
          "Garantir que nenhuma função misture lógica dos dois domínios"
        ]
      },
      {
        "id": 2,
        "name": "Módulos de Pagamento Angolanos",
        "objective": "Implementar simulação de gateways de pagamento angolanos",
        "orders": [
          "Criar app payment_gateways/ com estrutura completa: __init__.py, models.py, services.py, views.py, urls.py, forms.py",
          "Criar diretório templates/payment_gateways/ com subtemplates para cada gateway",
          "Criar model PaymentGateway com campos: name, code (unique), is_active, logo, description",
          "Criar model GatewayTransaction com campos: gateway (FK), transaction (OneToOne), gateway_reference, status, response_data (JSON), created_at",
          "Implementar função process_multicaixa_express(amount, phone) em payment_gateways/services.py retornando dict com success, reference, message",
          "Implementar função process_paypay(amount, phone) em payment_gateways/services.py retornando dict com success, reference, message",
          "Implementar função process_unitel_money(amount, phone) em payment_gateways/services.py retornando dict com success, reference, message",
          "Implementar função process_afrimoney(amount, phone) em payment_gateways/services.py retornando dict com success, reference, message",
          "Modificar process_payment() em payments/services.py para aceitar parâmetro gateway_code",
          "Criar registro GatewayTransaction após cada pagamento processado",
          "Atualizar Transaction.status baseado na resposta do gateway simulado",
          "Atualizar template prepaid/recharge.html adicionando seletor de gateway de pagamento",
          "Atualizar template postpaid/pay_invoice.html adicionando seletor de gateway de pagamento",
          "Implementar lógica para mostrar formulário específico do gateway ao selecionar",
          "Implementar redirecionamento para página de processamento e depois confirmação após submissão",
          "Criar pasta static/img/gateways/ via terminal",
          "Usar curl ou wget para baixar logo do Multicaixa Express para static/img/gateways/multicaixa_express.png",
          "Usar curl ou wget para baixar logo do Paypay para static/img/gateways/paypay.png",
          "Usar curl ou wget para baixar logo do Unitel Money para static/img/gateways/unitel_money.png",
          "Usar curl ou wget para baixar logo do Afrimoney para static/img/gateways/afrimoney.png",
          "Criar placeholders SVG com cores das marcas caso download falhe",
          "Criar arquivo payment_gateways/fixtures/gateways.json com os 4 gateways pré-configurados"
        ]
      },
      {
        "id": 3,
        "name": "Lógica de Ativação Pós-pago",
        "objective": "Implementar fluxo de definição do valor mensal pós-pago",
        "orders": [
          "Criar model PostpaidContract em postpaid/models.py",
          "Adicionar campo customer (OneToOneField com customers.Customer) no PostpaidContract",
          "Adicionar campo monthly_amount (DecimalField) no PostpaidContract",
          "Adicionar campo activation_method com choices inspection e system_suggestion no PostpaidContract",
          "Adicionar campo status com choices pending_inspection, pending_approval, active, rejected no PostpaidContract",
          "Adicionar campo appliances (JSONField) no PostpaidContract para lista de eletrodomésticos",
          "Adicionar campo is_commercial (BooleanField) no PostpaidContract",
          "Adicionar campos inspection_notes e admin_approval_notes (TextField) no PostpaidContract",
          "Adicionar campos created_at e approved_at (DateTimeField) no PostpaidContract",
          "Criar form InspectionRequestForm em postpaid/forms.py para solicitar vistoria da ENDE",
          "Criar form SystemSuggestionForm em postpaid/forms.py para declarar eletrodomésticos e tipo de espaço",
          "Criar view request_inspection_view em postpaid/views.py para submeter pedido de vistoria",
          "Criar view system_suggestion_view em postpaid/views.py para calcular valor sugerido baseado em eletrodomésticos",
          "Criar view admin_approve_contract_view em postpaid/views.py para operador aprovar/rejeitar contrato",
          "Implementar função calculate_suggested_amount(appliances, is_commercial) em postpaid/services.py",
          "Aplicar valores base por eletrodoméstico: Frigorífico 5000 Kz, Ar condicionado 8000 Kz, TV 2000 Kz, Micro-ondas 3000 Kz, Máquina de lavar 4000 Kz",
          "Aplicar multiplicador 1.5 se is_commercial for verdadeiro",
          "Criar template postpaid/request_inspection.html para formulário de solicitação de vistoria",
          "Criar template postpaid/system_suggestion.html para formulário com checkboxes de eletrodomésticos",
          "Criar template postpaid/contract_pending.html para página de aguardando aprovação",
          "Criar template postpaid/admin_approve.html para painel do operador aprovar contratos",
          "Modificar fluxo de registo para redirecionar cliente pós-pago para /postpaid/activate/ após criação",
          "Implementar escolha entre Solicitar Vistoria ou Sugestão do Sistema na ativação",
          "Manter conta inativa até PostpaidContract.status ser igual a active",
          "Atualizar customers/views.py para verificar se cliente pós-pago tem PostpaidContract ativo no dashboard",
          "Redirecionar para /postpaid/activate/ se cliente pós-pago não tiver contrato ativo"
        ]
      },
      {
        "id": 4,
        "name": "Motor de Faturação",
        "objective": "Implementar geração de faturas em múltiplos formatos",
        "orders": [
          "Instalar dependências: weasyprint, django-email-bandit, reportlab via pip",
          "Criar arquivo billing_app/invoice_generator.py",
          "Criar classe InvoiceGenerator com método estático generate_pdf(invoice) usando ReportLab ou WeasyPrint",
          "Criar método estático send_email(invoice, recipient_email) em InvoiceGenerator para enviar fatura por email com PDF anexado",
          "Criar método estático create_notification(invoice) em InvoiceGenerator para criar notificação in-app com link para fatura",
          "Implementar tipo Fatura de Vencimento (Aviso de Corte) para pós-pago quando due_date está próximo",
          "Implementar tipo Fatura de Pagamento (Recibo) para pós-pago após pagamento confirmado",
          "Implementar tipo Fatura de Recarga para pré-pago após recarga bem-sucedida",
          "Criar template billing_app/invoices/invoice_due_notice.html para aviso de vencimento",
          "Criar template billing_app/invoices/invoice_payment_receipt.html para recibo de pagamento",
          "Criar template billing_app/invoices/invoice_recharge_receipt.html para recibo de recarga",
          "Garantir que todos os templates de fatura tenham versão HTML para email e versão print-friendly para PDF",
          "Criar função generate_due_notices() em billing_app/tasks.py ou management command para gerar avisos de faturas a vencer em 3 dias",
          "Criar função generate_overdue_notices() em billing_app/tasks.py ou management command para gerar avisos de corte para faturas vencidas",
          "Integrar InvoiceGenerator.generate_pdf() e send_email() após pay_invoice() em payments/services.py",
          "Gerar recibo de recarga após recharge_balance() em payments/services.py",
          "Criar view download_invoice_pdf em billing_app/views.py com rota /billing/<pk>/pdf/",
          "Implementar geração de PDF on-the-fly retornando HttpResponse com content_type application/pdf",
          "Adicionar botão Baixar PDF em invoice_detail.html",
          "Adicionar botão Enviar por Email em invoice_detail.html",
          "Adicionar botão Recibo ao lado de cada transação em transaction_history.html"
        ]
      },
      {
        "id": 5,
        "name": "Sistema de Apoio ao Cliente Refatorado",
        "objective": "Refatorar sistema de suporte para ser mais preciso e eficiente",
        "orders": [
          "Expandir model Category em support/models.py adicionando campos: slug (unique), description, icon, sla_hours, is_active",
          "Criar fixture support/fixtures/categories.json com categorias pré-definidas",
          "Adicionar categoria Avaria Técnica com SLA 4 horas",
          "Adicionar categoria Problema de Faturação com SLA 24 horas",
          "Adicionar categoria Recarga Não Creditada com SLA 2 horas",
          "Adicionar categoria Pedido de Ligação com SLA 72 horas",
          "Adicionar categoria Denúncia/Fraude com SLA 48 horas",
          "Adicionar categoria Outro com SLA 48 horas",
          "Implementar função check_sla_compliance(ticket) em support/services.py para verificar se ticket está dentro do SLA",
          "Implementar função escalate_ticket(ticket) em support/services.py para escalar ticket se SLA expirado",
          "Criar view ticket_create_view em support/views.py com autocomplete de categorias",
          "Criar view ticket_detail_view em support/views.py com timeline de eventos",
          "Criar view operator_dashboard_view em support/views.py para operadores verem tickets por prioridade e SLA",
          "Implementar envio de notificação com número de protocolo ao criar ticket",
          "Implementar respostas automáticas para categorias comuns como Recarga Não Creditada",
          "Criar template support/ticket_create.html com formulário e ícones visuais por categoria",
          "Criar template support/operator_dashboard.html com painel, filtros e métricas",
          "Criar template support/ticket_timeline.html com timeline visual do ticket",
          "Implementar busca por número de protocolo no sistema de suporte",
          "Implementar filtro por status, prioridade e categoria no sistema de suporte",
          "Implementar ordenação por data e SLA restante no sistema de suporte"
        ]
      },
      {
        "id": 6,
        "name": "Angolanização Total",
        "objective": "Remover tudo estrangeiro e adaptar 100% para Angola",
        "orders": [
          "Substituir globalmente símbolos de moeda estrangeira ($, €, R$) por Kz ou AOA",
          "Substituir globalmente formatos de telefone estrangeiros por formato angolano +244 9XX XXX XXX",
          "Substituir globalmente endereços genéricos por formato angolano: Bairro, Município, Província",
          "Criar arquivo utils/angola.py",
          "Adicionar lista PROVINCIAS em utils/angola.py com todas as 18 províncias de Angola",
          "Adicionar dicionário MUNICIPIOS em utils/angola.py mapeando províncias para seus municípios",
          "Implementar função format_kz(value) em utils/angola.py para formatar valor como 1.500,00 Kz",
          "Implementar função validate_angolan_phone(phone) em utils/angola.py para validar formato +244 9XX XXX XXX",
          "Criar form CustomerOnboardingForm em customers/forms.py com selects de Província e Município",
          "Implementar validação de telefone angolano em CustomerOnboardingForm",
          "Implementar formatação automática de valores em Kz em CustomerOnboardingForm",
          "Atualizar todos os templates para usar filtro format_kz em vez de símbolos de moeda estrangeira",
          "Atualizar formulários de endereço para usar selects dependentes: Província → Município",
          "Aplicar máscara de telefone +244 9XX XXX XXX em todos os inputs de telefone",
          "Criar context processor angola_context em ende_platform/context_processors.py retornando PROVINCIAS, MOEDA e TELEFONE_PREFIXO",
          "Adicionar angola_context em TEMPLATES OPTIONS context_processors no settings.py",
          "Definir LANGUAGE_CODE como pt-ao no settings.py",
          "Definir TIME_ZONE como Africa/Luanda no settings.py"
        ]
      },
      {
        "id": 7,
        "name": "Interface Mobile-First",
        "objective": "Refatorar interface com CSS vanilla, animações e foco mobile-first",
        "orders": [
          "Criar arquivo static/css/ende_theme.css",
          "Definir variáveis CSS :root com cores da marca ENDE: ende-red #E30613, ende-black #1a1a1a, ende-white #ffffff, ende-gray #f5f5f5",
          "Implementar animação keyframes fadeIn em ende_theme.css",
          "Aplicar animação fadeIn 0.3s ease-out em cards",
          "Implementar animação keyframes slideIn para transições de página",
          "Aplicar animação slideIn 0.4s ease-out em elementos com classe page-transition",
          "Modificar templates/base.html para importar ende_theme.css após Bootstrap",
          "Adicionar meta tag theme-color com valor #E30613 em base.html",
          "Adicionar link rel manifest apontando para static/manifest.json em base.html",
          "Estilizar navbar com fundo preto e acentos vermelhos no hover",
          "Estilizar botões primários com cor --ende-red",
          "Criar arquivo static/manifest.json com configuração PWA: name ENDE Platform, short_name ENDE, start_url /, display standalone, theme_color #E30613, background_color #ffffff",
          "Instalar chart.js via npm ou configurar CDN",
          "Criar arquivo static/js/realtime_charts.js",
          "Implementar função updateConsumptionChart(customerId) que busca dados via fetch e atualiza Chart.js",
          "Configurar setInterval para atualizar gráfico de consumo a cada 30000 milissegundos",
          "Refatorar template prepaid/dashboard.html com gráfico de consumo diário, saldo em destaque e botão de recarga grande",
          "Refatorar template postpaid/dashboard.html com gráfico de consumo mensal, fatura atual em destaque e botão de pagamento",
          "Aplicar animações de entrada fade-in nos cards dos dashboards",
          "Definir altura mínima de 48px em botões para toque mobile-friendly",
          "Estilizar formulários com inputs grandes e labels visíveis para mobile",
          "Implementar tabelas responsivas com scroll horizontal em viewport mobile",
          "Melhorar menu hambúrguer com ícones grandes e área de toque ampliada",
          "Adicionar hover com transform translateY -2px e box-shadow em cards",
          "Implementar efeito ripple ao clicar em botões",
          "Criar loading spinners personalizados com a cor --ende-red da marca ENDE"
        ]
      }
    ]
  },
  "agent_rules": [
    "Modificar ficheiros diretamente sem pedir permissão prévia",
    "Manter os 76 testes existentes passando; criar migrações e atualizar testes ao modificar models",
    "Escrever código completo dos ficheiros sem placeholders ou comentários de omissão",
    "Seguir Django Best Practices: class-based views quando apropriado, Django Forms, signals, consistência com projeto",
    "Garantir que todos os novos templates sejam 100% responsivos e otimizados para mobile",
    "Refletir realidade angolana em todo o código: moeda Kz, endereços com Província/Município, telefones +244, gateways locais"
  ],
  "execution_protocol": {
    "start_action": "Ler estrutura atual do projeto com tree de diretórios",
    "first_phase": "Executar FASE 1: Separação de Domínios e criar apps prepaid/ e postpaid/",
    "stop_and_report_after_phase": [
      "Mostrar nova árvore de diretórios",
      "Listar ficheiros criados em prepaid/ e postpaid/",
      "Exibir alterações em ende_platform/urls.py"
    ],
    "approval_required": true,
    "approval_trigger": "Aguardar confirmação OK do usuário antes de prosseguir para próxima fase",
    "critical_warning": "Não executar todas as fases de uma vez. Executar fase por fase e aguardar aprovação entre cada uma"
  },
  "deliverables_summary": [
    {
      "phase": 1,
      "name": "Separação de Domínios",
      "main_changes": "Apps prepaid/ e postpaid/ com dashboards separados",
    },
    {
      "phase": 2,
      "name": "Gateways Angolanos",
      "main_changes": "Multicaixa Express, Paypay, Unitel Money, Afrimoney simulados",
    },
    {
      "phase": 3,
      "name": "Ativação Pós-pago",
      "main_changes": "Fluxo de vistoria ou sugestão do sistema",
    },
    {
      "phase": 4,
      "name": "Motor de Faturação",
      "main_changes": "Geração de PDFs, emails, notificações",
    },
    {
      "phase": 5,
      "name": "Suporte Refatorado",
      "main_changes": "SLAs, categorias, dashboard de operador",
    },
    {
      "phase": 6,
      "name": "Angolanização",
      "main_changes": "Remove elementos estrangeiros, adiciona províncias e municípios",
    },
    {
      "phase": 7,
      "name": "Interface Mobile",
      "main_changes": "CSS vanilla, animações, PWA, gráficos em tempo real",
    }
  ]
}