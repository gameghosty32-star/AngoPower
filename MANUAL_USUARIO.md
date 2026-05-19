# Manual do Utilizador — ENDE Platform

## Índice

1. [Introdução](#1-introdução)
2. [Acesso ao Sistema](#2-acesso-ao-sistema)
3. [Dashboard](#3-dashboard)
4. [Clientes Pré-pago](#4-clientes-pré-pago)
5. [Clientes Pós-pago](#5-clientes-pós-pago)
6. [Suporte e Tickets](#6-suporte-e-tickets)
7. [Notificações](#7-notificações)
8. [Perguntas Frequentes](#8-perguntas-frequentes)

---

## 1. Introdução

A **ENDE Platform** é um sistema web para gestão de serviços de energia eléctrica. Permite que clientes **pré-pago** recarreguem saldo, consultem o consumo, e que clientes **pós-pago** visualizem e paguem faturas. O sistema também oferece suporte via tickets e notificações in-app.

### Perfis de Utilizador

| Perfil | Descrição |
|---|---|
| **Cliente** | Utilizador final que consome energia (pré-pago ou pós-pago) |
| **Operador** | Funcionário da ENDE que atende tickets de suporte |
| **Administrador** | Gestor do sistema com acesso total |

---

## 2. Acesso ao Sistema

### 2.1. Criar Conta

1. Aceda a `http://localhost:8000/register/`
2. Preencha os campos: nome de utilizador, e-mail e senha
3. Clique em **Cadastrar**
4. A sua conta será criada e será redireccionado ao Dashboard

> **Nota**: Após o registo, um operador ENDE precisa associar um perfil de cliente (com número de medidor) à sua conta. Contacte o suporte se não conseguir aceder ao Dashboard.

### 2.2. Iniciar Sessão

1. Aceda a `http://localhost:8000/login/`
2. Introduza o nome de utilizador e senha
3. Clique em **Entrar**

### 2.3. Recuperar Senha

1. Na página de login, clique em **Esqueceu a senha?**
2. Introduza o e-mail da sua conta
3. Receberá um link para redefinir a senha

### 2.4. Encerrar Sessão

- Clique no seu nome de utilizador (canto superior direito)
- Selecione **Logout** no menu suspenso

---

## 3. Dashboard

Após o login, o Dashboard apresenta uma visão geral da sua conta:

- **Saldo Actual**: valor disponível na conta
- **Dívida Pendente**: valor em dívida (se aplicável)
- **Nº do Medidor**: identificador do seu medidor
- **Tipo de Conta**: Pré-pago ou Pós-pago

### Acções Rápidas

A partir do Dashboard pode aceder directamente a:
- **Consultar Saldo** — ver detalhes do saldo
- **Recarregar** — adicionar crédito (pré-pago)
- **Histórico de Transacções** — ver movimentos da conta
- **Minhas Faturas** — listar faturas (pós-pago)
- **Consumo** — visualizar consumo com gráfico
- **Suporte** — abrir tickets de atendimento

---

## 4. Clientes Pré-pago

### 4.1. Consultar Saldo

1. No Dashboard, clique em **Consultar Saldo**
2. Serão exibidos: saldo disponível, dívida, número do medidor e tipo de conta
3. Clique em **Recarregar Agora** para adicionar crédito

### 4.2. Recarregar Saldo

1. No Dashboard, clique em **Recarregar**
2. Introduza o valor da recarga (ex: 50.00)
3. Clique em **Confirmar Recarga**
4. Uma notificação de confirmação será exibida
5. O saldo será actualizado automaticamente

### 4.3. Histórico de Transacções

1. No Dashboard, clique em **Histórico de Transacções**
2. Visualize todas as transacções: ID, tipo, valor, status e data
3. Os status podem ser: **Concluído** (verde), **Pendente** (amarelo), **Falhou** (vermelho)

---

## 5. Clientes Pós-pago

### 5.1. Listar Faturas

1. No Dashboard, clique em **Minhas Faturas**
2. Visualize todas as faturas com: número, valor, valor pago, status, emissão e vencimento
3. Status possíveis: **Emitida** (azul), **Paga** (verde), **Vencida** (vermelho), **Parcial** (amarelo)

### 5.2. Detalhe da Fatura

1. Na lista de faturas, clique em **👁️ Ver** ao lado da fatura desejada
2. Visualize: valor total, valor pago, saldo restante, datas e descrição
3. As transacções relacionadas à fatura são exibidas na mesma página

### 5.3. Pagar Fatura

1. Na lista ou detalhe da fatura, clique em **💳 Pagar**
2. Confirme o valor total, já pago e restante
3. Introduza o valor do pagamento (pode ser parcial)
4. Clique em **Confirmar Pagamento**
5. A fatura será actualizada (paga ou parcialmente paga)

### 5.4. Histórico de Consumo

1. No Dashboard, clique em **Consumo**
2. Visualize um gráfico de barras do consumo mensal
3. Cards de resumo: total de transacções, consumo total, média mensal
4. Tabela detalhada com todos os registos de consumo

---

## 6. Suporte e Tickets

### 6.1. Criar Ticket

1. No Dashboard, clique em **Suporte** ou aceda a **Novo Ticket**
2. Preencha:
   - **Assunto**: breve descrição do problema
   - **Categoria**: tipo de problema (ex: Técnico, Facturação)
   - **Prioridade**: Baixa, Média, Alta ou Urgente
   - **Descrição**: detalhe completo do problema
3. Clique em **Enviar Ticket**
4. Será redireccionado ao detalhe do ticket criado

### 6.2. Acompanhar Ticket

1. Na lista de tickets, clique em **👁️ Ver** no ticket desejado
2. Visualize: assunto, status, prioridade, categoria e descrição
3. As mensagens trocadas com o suporte são exibidas em formato de chat

### 6.3. Adicionar Mensagem

1. No detalhe do ticket, desça até à secção **Mensagens**
2. Escreva a sua mensagem na caixa de texto
3. Clique em **Enviar**
4. A mensagem será adicionada ao histórico

### Status dos Tickets

| Status | Significado |
|---|---|
| **Aberto** (vermelho) | Ticket registado, aguardando atendimento |
| **Em Andamento** (amarelo) | Operador está a analisar o problema |
| **Resolvido** (azul) | Problema foi resolvido |
| **Fechado** (cinza) | Ticket encerrado |

---

## 7. Notificações

### 7.1. Visualizar Notificações

1. Clique em **Notificações** na barra de navegação
2. O número ao lado indica quantas notificações não lidas existem
3. Cada notificação mostra: tipo, título, mensagem e data

### 7.2. Marcar como Lida

- **Individual**: clique no ícone ✅ ao lado da notificação
- **Todas**: clique em **Marcar todas como lidas**

### Tipos de Notificação

| Tipo | Ícone | Quando ocorre |
|---|---|---|
| Recarga | 💚 | Após recarga de saldo confirmada |
| Pagamento | 💙 | Após pagamento de fatura |
| Ticket | 💛 | Actualização de ticket de suporte |
| Factura | 🩵 | Alerta de fatura próxima do vencimento |
| Sistema | 🩶 | Avisos gerais do sistema |

---

## 8. Perguntas Frequentes

### Como sei se sou pré-pago ou pós-pago?
O seu tipo de conta é exibido no Dashboard e na página de saldo. Contacte a ENDE se precisar alterar.

### Porque não consigo ver o Dashboard após criar conta?
É necessário que um operador associe um perfil de cliente (com número de medidor) à sua conta de utilizador. Contacte o suporte.

### Posso pagar apenas parte de uma fatura?
Sim. O sistema permite pagamentos parciais. A fatura ficará com status **Parcial** até ser totalmente liquidada.

### Quanto tempo demora a recarga a aparecer no saldo?
Imediatamente. As recargas são processadas em tempo real e o saldo é actualizado de imediato.

### Como alterar a minha senha?
1. Aceda a `/password-change/` (Alterar Senha)
2. Introduza a senha actual e a nova senha
3. Clique em **Alterar senha**

### Esqueci a minha senha, o que fazer?
Na página de login, clique em **Esqueceu a senha?** e siga as instruções para redefinir.
