# ENDE Platform — Prova de Aptidão Profissional

**Curso Técnico de Informática de Gestão — IMCL**

---

## Slide 1: Capa

```
╔══════════════════════════════════════════╗
║                                          ║
║       ENDE Platform                      ║
║  Gestão de Atendimento e Pagamentos      ║
║                                          ║
║  Prova de Aptidão Profissional           ║
║  Curso Técnico de Informática de Gestão  ║
║  IMCL                                    ║
║                                          ║
║  Autor: [Nome do Aluno]                  ║
║  Orientador: [Nome do Orientador]        ║
║  Ano Lectivo: 2025/2026                  ║
║                                          ║
╚══════════════════════════════════════════╝
```

---

## Slide 2: Problema

**Contexto**

A ENDE-EP (Empresa Nacional de Distribuição de Electricidade) enfrenta desafios na gestão de clientes:

- **Clientes pré-pago**: dificuldade em consultar saldo e recarregar
- **Clientes pós-pago**: morosidade na consulta e pagamento de faturas
- **Suporte ao cliente**: ausência de canal digital para abertura de tickets
- **Falta de transparência**: histórico de consumo e transacções não acessível

**Problema central**: Inexistência de uma plataforma web integrada que permita aos clientes gerir os seus serviços de energia de forma autónoma.

---

## Slide 3: Solução

**ENDE Platform** — sistema web que oferece:

| Funcionalidade | Pré-pago | Pós-pago |
|---|---|---|
| Consulta de saldo | ✅ | — |
| Recarga de crédito | ✅ | — |
| Consulta de faturas | — | ✅ |
| Pagamento de faturas | — | ✅ |
| Histórico de transacções | ✅ | ✅ |
| Histórico de consumo | ✅ | ✅ |
| Tickets de suporte | ✅ | ✅ |
| Notificações in-app | ✅ | ✅ |

**Público-alvo**: Clientes, Operadores de Atendimento, Administradores

---

## Slide 4: Tecnologias

```
┌─────────────────────────────────────────┐
│         Stack Tecnológica               │
├─────────────┬───────────────────────────┤
│ Python 3.12 │ Linguagem principal       │
│ Django 6.0  │ Framework web             │
│ DRF         │ API REST                  │
│ SQLite/PSQL │ Base de dados             │
│ Bootstrap 5 │ Interface responsiva      │
│ Chart.js    │ Gráficos                  │
└─────────────┴───────────────────────────┘
```

**Arquitetura**: Monolítica modular (Django MTV)

- **Model**: ORM com SQLite/PostgreSQL
- **Template**: Bootstrap 5 com Chart.js
- **View**: Lógica de negócio em Python

---

## Slide 5: Arquitetura do Sistema

```
┌─────────── Utilizador ───────────┐
          │           │
    ┌─────▼─────┐ ┌──▼────────┐
    │  Browser  │ │ App Mobile│
    │ (HTML/CSS)│ │ (Futuro)  │
    └─────┬─────┘ └─────┬─────┘
          │              │
    ┌─────▼──────────────▼─────┐
    │       Django Server       │
    │  (MTV - Models/Templates/ │
    │         Views)            │
    ├───────────────────────────┤
    │  ┌─────────────────────┐  │
    │  │    API REST (DRF)   │  │
    │  └─────────────────────┘  │
    ├───────────────────────────┤
    │  Apps:                    │
    │  users ─ customers ─      │
    │  billing_app ─ payments ─ │
    │  support ─ notifications  │
    └─────────────┬─────────────┘
                  │
         ┌───────▼───────┐
         │   SQLite/PSQL  │
         │   (Database)   │
         └───────────────┘
```

---

## Slide 6: Modelo de Dados

```
┌───────────┐     ┌──────────────┐
│ CustomUser│1:1  │   Customer   │
│ (Abstract │─────┤ (prepaid/    │
│  User)    │     │  postpaid)   │
└───────────┘     └──────┬───────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
       ┌────▼───┐  ┌────▼───┐  ┌────▼───┐
       │Invoice │  │Transac.│  │ Ticket │
       │(status)│  │(type)  │  │(status)│
       └────────┘  └────────┘  └───┬────┘
                                    │
                              ┌─────▼────┐
                              │ Message  │
                              └──────────┘

┌──────────────┐
│ Notification │
│ (in-app)     │
└──────────────┘
```

### Apps:
- **users**: RBAC (client/operator/admin)
- **customers**: perfil do cliente (pré/pós)
- **billing_app**: faturas com 5 estados
- **payments**: transacções ACID + API
- **support**: tickets + mensagens
- **notifications**: alertas in-app

---

## Slide 7: Funcionalidades — Demo

### Fluxo Pré-pago

```
Dashboard → Consulta Saldo → Recarga → Confirmação
                                       ↓
                            Notificação + Histórico
```

### Fluxo Pós-pago

```
Dashboard → Lista Faturas → Detalhe → Pagamento
                                       ↓
                            Notificação + Histórico
```

### Fluxo Suporte

```
Dashboard → Novo Ticket → Descrição → Acompanhamento
                                       ↓
                            Mensagens + Resolução
```

---

## Slide 8: Segurança

| Medida | Implementação |
|---|---|
| CSRF | Django CsrfViewMiddleware + `{% csrf_token %}` |
| XSS | Auto-escaping de templates |
| Rate Limiting | 10 POST/min por IP |
| Sessão | HTTPOnly, SameSite Lax |
| Headers | XSS Filter, Content-Type Nosniff |
| Autenticação | `@login_required` + `IsAuthenticated` |

---

## Slide 9: Testes

**76 testes automatizados — todos passando**

```
─────────────────────────────────────────
App           Testes  Status
─────────────────────────────────────────
users             9   ✅ 100%
customers       12   ✅ 100%
billing_app     11   ✅ 100%
payments        17   ✅ 100%
support         14   ✅ 100%
notifications   11   ✅ 100%
─────────────────────────────────────────
Total           76   ✅ 100%
─────────────────────────────────────────
```

Cobertura: models, views, serviços de pagamento, API REST, fluxos completos.

---

## Slide 10: Resultados

### Critérios de Sucesso

| Critério | Resultado |
|---|---|
| Cliente pré-pago recarrega em < 3 cliques | ✅ 2 cliques |
| Cliente pós-pago paga fatura em < 2 min | ✅ ~30 segundos |
| Operador abre ticket sem sistema externo | ✅ Integrado |
| 0 erros críticos | ✅ 76/76 testes |
| Tempo de resposta < 2s | ✅ Consultas otimizadas |
| Código organizado por apps | ✅ 6 apps modulares |

### Diferenciais

- **Dashboard** personalizado por tipo de cliente
- **Gráficos** com Chart.js para visualização de consumo
- **Notificações** em tempo real com badges
- **API REST** pronta para integração mobile
- **Rate limiting** integrado sem dependências externas

---

## Slide 11: Limitações e Trabalho Futuro

### Limitações Actuais

- Pagamentos simulados (sem gateway real)
- Sem integração com sistemas externos (SMS, e-mail)
- Autenticação por sessão apenas (sem JWT/OAuth)
- Sem deploy em produção real

### Melhorias Futuras

- [ ] Integração com gateway de pagamentos real
- [ ] Aplicação mobile (Android/iOS) consumindo API REST
- [ ] Notificações por e-mail e SMS
- [ ] Painel de operador com métricas e relatórios
- [ ] Autenticação JWT para API
- [ ] Deploy em cloud (AWS/Heroku)

---

## Slide 12: Conclusão

```
╔══════════════════════════════════════════╗
║                                          ║
║  ENDE Platform                           ║
║                                          ║
║  ✅ Problema identificado                ║
║  ✅ Solução implementada                 ║
║  ✅ 6 fases concluídas                   ║
║  ✅ 76 testes, 0 falhas                  ║
║  ✅ Documentação completa                ║
║  ✅ Pronto para apresentação             ║
║                                          ║
║  "Tecnologia ao serviço da energia"      ║
║                                          ║
╚══════════════════════════════════════════╝
```

**Obrigado!**

Perguntas?

---

## Slide 13: Perguntas e Respostas

### Q: O sistema pode ser usado com diferentes moedas?
R: Sim. O campo `DecimalField` permite qualquer moeda. Apenas é necessário alterar o símbolo nos templates.

### Q: Como é feita a gestão de operadores?
R: Operadores têm acesso ao admin Django (`/admin/`) onde podem gerir clientes, tickets e faturas.

### Q: O sistema suporta multi-idioma?
R: Actualmente em português. Django tem suporte nativo a i18n para tradução.

### Q: Qual a escalabilidade?
R: Arquitetura monolítica modular. Pode evoluir para microserviços dividindo as apps em serviços independentes.

### Q: Como garantir a segurança dos dados?
R: CSRF, XSS protection, rate limiting, sessões HTTPOnly, autenticação obrigatória em todas as rotas.

---

## Notas para Apresentação

- **Duração estimada**: 15-20 minutos
- **Demo ao vivo**: Recomendado demonstrar os 3 fluxos principais
- **Slides**: Este documento serve como script; transferir para PowerPoint/Google Slides
- **Código-fonte**: Ter o projecto aberto no IDE durante a apresentação
