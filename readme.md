# Sistema de Gestão de Projetos Arquitetônicos
**Crialt Arquitetura - Painel Administrativo**

## 📋 Sumário
1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Estrutura do Monorepo](#estrutura-do-monorepo)
4. [Funcionalidades e Telas](#funcionalidades-e-telas)
5. [Regras de Negócio](#regras-de-negócio)
6. [Especificações Técnicas](#especificações-técnicas)
7. [Setup e Desenvolvimento](#setup-e-desenvolvimento)
8. [Roadmap Futuro](#roadmap-futuro)
9. [Conclusão](#conclusão)

---

## 🎯 Visão Geral do Projeto

Sistema web para gestão completa de projetos arquitetônicos, desenvolvido especificamente para **Crialt Arquitetura**. O sistema permite gerenciar clientes, projetos e o fluxo completo de etapas do processo arquitetônico, desde o levantamento até a assessoria pós-projeto.

### Objetivos Principais
- **Gestão de Clientes**: Cadastro completo e histórico de projetos
- **Controle de Projetos**: Acompanhamento detalhado do ciclo de vida
- **Workflow de Etapas**: Controle rigoroso das fases do projeto arquitetônico
- **Timeline Visual**: Acompanhamento visual do progresso
- **Gestão de Arquivos**: Upload e organização de documentos por etapa
- **Relatórios Gerenciais**: Dashboards e relatórios de performance

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico
- **Backend**: FastAPI (Python) com type hints completos
- **Frontend**: Angular 17+ com SSR (Angular Universal)
- **Banco de Dados**: PostgreSQL
- **Storage**: Sistema de arquivos local organizado
- **Containerização**: Docker + Docker Compose

### Arquitetura de Alto Nível
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Angular SSR   │────│   FastAPI       │────│   PostgreSQL    │
│   Frontend      │    │   Backend       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                       ┌─────────────────┐
                       │  Local Storage  │
                       │  File System    │
                       └─────────────────┘
```

---

## 📁 Estrutura do Monorepo

```
crialt-system/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── backend/                              # FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── .env
│   │
│   ├── alembic/                          # Migrações do banco
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                       # Entry point FastAPI
│   │   │
│   │   ├── core/                         # Configurações centrais
│   │   │   ├── __init__.py
│   │   │   ├── config.py                 # Settings e configurações
│   │   │   ├── database.py               # Conexão com banco
│   │   │   ├── security.py               # JWT, hash, etc
│   │   │   └── exceptions.py             # Exception handlers
│   │   │
│   │   ├── models/                       # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   # Base class
│   │   │   ├── user.py
│   │   │   ├── client.py
│   │   │   ├── project.py
│   │   │   ├── stage_type.py             # Tipos de etapa (cadastrável)
│   │   │   ├── stage.py                  # Instâncias dinâmicas de etapa
│   │   │   ├── task.py
│   │   │   └── file.py
│   │   │
│   │   ├── schemas/                      # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── common.py                 # Schemas comuns
│   │   │   ├── user.py
│   │   │   ├── client.py
│   │   │   ├── project.py
│   │   │   ├── stage_type.py             # Schemas para tipos de etapa
│   │   │   ├── stage.py                  # Schemas para etapas dinâmicas
│   │   │   ├── task.py
│   │   │   └── file.py
│   │   │
│   │   ├── api/                          # Rotas e endpoints
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py           # Dependências compartilhadas
│   │   │   ├── router.py                 # Router principal
│   │   │   │
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── clients.py
│   │   │   ├── projects.py
│   │   │   ├── stage_types.py            # Endpoint para tipos de etapa
│   │   │   ├── stages.py                 # Endpoint para etapas dinâmicas
│   │   │   ├── tasks.py
│   │   │   └── files.py
│   │   │
│   │   ├── services/                     # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── client_service.py
│   │   │   ├── project_service.py
│   │   │   ├── stage_type_service.py     # Serviço para tipos de etapa
│   │   │   ├── stage_service.py          # Serviço para etapas dinâmicas
│   │   │   ├── task_service.py
│   │   │   └── file_service.py
│   │   │
│   │   ├── utils/                        # Utilitários
│   │   │   ├── __init__.py
│   │   │   ├── validators.py
│   │   │   ├── formatters.py
│   │   │   ├── cache.py
│   │   │   └── constants.py
│   │   │
│   │   └── storage/                      # Storage local
│   │       ├── uploads/
│   │       │   ├── documents/
│   │       │   ├── images/
│   │       │   └── temp/
│   │       └── backups/
│   │
│   └── tests/                            # Testes backend
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_clients.py
│       ├── test_projects.py
│       ├── test_stage_types.py           # Testes para tipos de etapa
│       ├── test_stages.py                # Testes para etapas dinâmicas
│       └── test_tasks.py
│
├── frontend/                             # Angular SSR
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   ├── angular.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.spec.json
│   └── server.ts                         # SSR server
│   │
│   ├── src/
│   │   ├── main.ts                       # Bootstrap client
│   │   ├── main.server.ts                # Bootstrap server
│   │   ├── index.html
│   │   ├── styles.scss                   # Global styles
│   │   │
│   │   ├── app/
│   │   │   ├── app.config.ts             # App configuration
│   │   │   ├── app.config.server.ts      # Server configuration
│   │   │   ├── app.routes.ts             # Routing
│   │   │   ├── app.component.ts
│   │   │   ├── app.component.html
│   │   │   ├── app.component.scss
│   │   │   │
│   │   │   ├── core/                     # Serviços centrais
│   │   │   │   ├── services/
│   │   │   │   │   ├── api.service.ts
│   │   │   │   │   ├── auth.service.ts
│   │   │   │   │   ├── client.service.ts
│   │   │   │   │   ├── project.service.ts
│   │   │   │   │   ├── stage.service.ts
│   │   │   │   │   └── file.service.ts
│   │   │   │   │
│   │   │   │   ├── guards/
│   │   │   │   │   ├── auth.guard.ts
│   │   │   │   │   └── role.guard.ts
│   │   │   │   │
│   │   │   │   ├── interceptors/
│   │   │   │   │   ├── auth.interceptor.ts
│   │   │   │   │   ├── error.interceptor.ts
│   │   │   │   │   └── loading.interceptor.ts
│   │   │   │   │
│   │   │   │   └── models/
│   │   │   │       ├── user.model.ts
│   │   │   │       ├── client.model.ts
│   │   │   │       ├── project.model.ts
│   │   │   │       ├── stage.model.ts
│   │   │   │       └── common.model.ts
│   │   │   │
│   │   │   ├── shared/                   # Componentes compartilhados
│   │   │   │   ├── components/
│   │   │   │   │   ├── header/
│   │   │   │   │   │   ├── header.component.ts
│   │   │   │   │   │   ├── header.component.html
│   │   │   │   │   │   └── header.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── sidebar/
│   │   │   │   │   │   ├── sidebar.component.ts
│   │   │   │   │   │   ├── sidebar.component.html
│   │   │   │   │   │   └── sidebar.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── loading-spinner/
│   │   │   │   │   │   ├── loading-spinner.component.ts
│   │   │   │   │   │   ├── loading-spinner.component.html
│   │   │   │   │   │   └── loading-spinner.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── confirmation-modal/
│   │   │   │   │   │   ├── confirmation-modal.component.ts
│   │   │   │   │   │   ├── confirmation-modal.component.html
│   │   │   │   │   │   └── confirmation-modal.component.scss
│   │   │   │   │   │
│   │   │   │   │   └── file-upload/
│   │   │   │   │       ├── file-upload.component.ts
│   │   │   │   │       ├── file-upload.component.html
│   │   │   │   │       └── file-upload.component.scss
│   │   │   │   │
│   │   │   │   ├── directives/
│   │   │   │   │   ├── auto-focus.directive.ts
│   │   │   │   │   └── number-only.directive.ts
│   │   │   │   │
│   │   │   │   ├── pipes/
│   │   │   │   │   ├── currency-br.pipe.ts
│   │   │   │   │   ├── cpf-cnpj.pipe.ts
│   │   │   │   │   └── date-br.pipe.ts
│   │   │   │   │
│   │   │   │   └── validators/
│   │   │   │       ├── cpf.validator.ts
│   │   │   │       ├── cnpj.validator.ts
│   │   │   │       └── phone.validator.ts
│   │   │   │
│   │   │   ├── features/                 # Funcionalidades principais
│   │   │   │   ├── auth/
│   │   │   │   │   ├── login/
│   │   │   │   │   │   ├── login.component.ts
│   │   │   │   │   │   ├── login.component.html
│   │   │   │   │   │   └── login.component.scss
│   │   │   │   │   │
│   │   │   │   │   └── register/
│   │   │   │   │       ├── register.component.ts
│   │   │   │   │       ├── register.component.html
│   │   │   │   │       └── register.component.scss
│   │   │   │   │
│   │   │   │   ├── dashboard/
│   │   │   │   │   ├── dashboard.component.ts
│   │   │   │   │   ├── dashboard.component.html
│   │   │   │   │   ├── dashboard.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── stats-cards/
│   │   │   │   │   │   │   ├── stats-cards.component.ts
│   │   │   │   │   │   │   ├── stats-cards.component.html
│   │   │   │   │   │   │   └── stats-cards.component.scss
│   │   │   │   │   │   │
│   │   │   │   │   │   ├── recent-projects/
│   │   │   │   │   │   │   ├── recent-projects.component.ts
│   │   │   │   │   │   │   ├── recent-projects.component.html
│   │   │   │   │   │   │   └── recent-projects.component.scss
│   │   │   │   │   │   │
│   │   │   │   │   │   └── timeline-overview/
│   │   │   │   │   │       ├── timeline-overview.component.ts
│   │   │   │   │   │       ├── timeline-overview.component.html
│   │   │   │   │   │       └── timeline-overview.component.scss
│   │   │   │   │   │
│   │   │   │   │   └── dashboard.routes.ts
│   │   │   │   │
│   │   │   │   ├── clients/
│   │   │   │   │   ├── client-list/
│   │   │   │   │   │   ├── client-list.component.ts
│   │   │   │   │   │   ├── client-list.component.html
│   │   │   │   │   │   └── client-list.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── client-form/
│   │   │   │   │   │   ├── client-form.component.ts
│   │   │   │   │   │   ├── client-form.component.html
│   │   │   │   │   │   └── client-form.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── client-detail/
│   │   │   │   │   │   ├── client-detail.component.ts
│   │   │   │   │   │   ├── client-detail.component.html
│   │   │   │   │   │   └── client-detail.component.scss
│   │   │   │   │   │
│   │   │   │   │   └── clients.routes.ts
│   │   │   │   │
│   │   │   │   ├── projects/
│   │   │   │   │   ├── project-list/
│   │   │   │   │   │   ├── project-list.component.ts
│   │   │   │   │   │   ├── project-list.component.html
│   │   │   │   │   │   └── project-list.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── project-form/
│   │   │   │   │   │   ├── project-form.component.ts
│   │   │   │   │   │   ├── project-form.component.html
│   │   │   │   │   │   └── project-form.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── project-detail/
│   │   │   │   │   │   ├── project-detail.component.ts
│   │   │   │   │   │   ├── project-detail.component.html
│   │   │   │   │   │   └── project-detail.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── project-timeline/
│   │   │   │   │   │   ├── project-timeline.component.ts
│   │   │   │   │   │   ├── project-timeline.component.html
│   │   │   │   │   │   └── project-timeline.component.scss
│   │   │   │   │   │
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── stage-card/
│   │   │   │   │   │   │   ├── stage-card.component.ts
│   │   │   │   │   │   │   ├── stage-card.component.html
│   │   │   │   │   │   │   └── stage-card.component.scss
│   │   │   │   │   │   │
│   │   │   │   │   │   └── progress-bar/
│   │   │   │   │   │       ├── progress-bar.component.ts
│   │   │   │   │   │       ├── progress-bar.component.html
│   │   │   │   │   │       └── progress-bar.component.scss
│   │   │   │   │   │
│   │   │   │   │   └── projects.routes.ts
│   │   │   │   │
│   │   │   │   └── stages/
│   │   │   │       ├── stage-form/
│   │   │   │       │   ├── stage-form.component.ts
│   │   │   │       │   ├── stage-form.component.html
│   │   │   │       │   └── stage-form.component.scss
│   │   │   │       │
│   │   │   │       ├── stage-detail/
│   │   │   │       │   ├── stage-detail.component.ts
│   │   │   │       │   ├── stage-detail.component.html
│   │   │   │       │   └── stage-detail.component.scss
│   │   │   │       │
│   │   │   │       └── stages.routes.ts
│   │   │   │
│   │   │   ├── layout/                   # Layout components
│   │   │   │   ├── main-layout/
│   │   │   │   │   ├── main-layout.component.ts
│   │   │   │   │   ├── main-layout.component.html
│   │   │   │   │   └── main-layout.component.scss
│   │   │   │   │
│   │   │   │   └── auth-layout/
│   │   │   │       ├── auth-layout.component.ts
│   │   │   │       ├── auth-layout.component.html
│   │   │   │       └── auth-layout.component.scss
│   │   │   │
│   │   │   └── environments/
│   │   │       ├── environment.ts        # Development
│   │   │       └── environment.prod.ts   # Production
│   │   │
│   │   └── assets/                       # Static assets
│   │       ├── images/
│   │       ├── icons/
│   │       └── fonts/
│   │
│   ├── dist/                             # Build output
│   └── docker/                               # Docker configs
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
│
├── scripts/                              # Utility scripts
│   ├── setup.sh
│   ├── build.sh
│   └── deploy.sh
│
└── docs/                                 # Documentação
    ├── api.md
    ├── setup.md
    └── deployment.md
```

---

## 🖥️ Funcionalidades e Telas

### 1. **Autenticação**
#### 1.1 Tela de Login (`/auth/login`)
- **Componente**: `LoginComponent`
- **Funcionalidades**:
  - Login com email/senha (usuário ou cliente)
  - Recuperação de senha
  - Lembrar credenciais
  - Redirecionamento pós-login
  - Validação de formulário
  - Loading states

#### 1.2 Tela de Registro (`/auth/register`)
- **Componente**: `RegisterComponent`
- **Funcionalidades**:
  - Cadastro de novo usuário
  - Validação de CPF
  - Confirmação de senha
  - Termos de uso
  - **Cadastro público desabilitado**: Apenas admins podem criar usuários

### 2. **Dashboard Principal**
#### 2.1 Tela Principal (`/dashboard`)
- **Componente**: `DashboardComponent`
- **Funcionalidades**:
  - **Cards de Estatísticas**:
    - Total de clientes ativos
    - Projetos em andamento
    - Projetos concluídos no mês
    - Receita do mês
    - Etapas próximas do vencimento
  - **Projetos Recentes**: Lista dos 5 projetos mais recentes
  - **Timeline Geral**: Visão macro de todas as etapas em andamento
  - **Gráficos**:
    - Projetos por status
    - Receita mensal (últimos 6 meses)
    - Tempo médio por etapa
  - **Notificações**: Prazos vencendo, etapas pendentes

### 3. **Gestão de Clientes**
#### 3.1 Lista de Clientes (`/clients`)
- **Componente**: `ClientListComponent`
- **Funcionalidades**:
  - **Tabela de clientes** com paginação
  - **Filtros**:
    - Nome/razão social
    - CPF/CNPJ
    - Status (ativo/inativo)
    - Data de cadastro
  - **Ordenação** por colunas
  - **Busca textual** global
  - **Ações rápidas**:
    - Editar cliente
    - Ver detalhes
    - Novo projeto
    - Inativar/ativar
  - **Export** para Excel/PDF

#### 3.2 Formulário de Cliente (`/clients/new`, `/clients/:id/edit`)
- **Componente**: `ClientFormComponent`
- **Funcionalidades**:
  - **Dados Básicos**:
    - Nome completo/razão social
    - CPF/CNPJ (com validação)
    - RG/IE
    - Data de nascimento/fundação
  - **Contato**:
    - Email (principal e secundário)
    - Telefone/celular
    - WhatsApp
  - **Endereço**:
    - CEP com busca automática
    - Endereço completo
    - Complemento
  - **Observações**: Campo livre para anotações
  - **Upload de documentos**: RG, CPF, etc.
  - **Validação completa** dos campos
  - **Auto-save** draft
  - **Senha de acesso**:
    - Gerada automaticamente no cadastro
    - Campo 'primeiro acesso' para obrigar troca de senha
    - Opção de redefinir senha pelo admin

#### 3.3 Detalhes do Cliente (`/clients/:id`)
- **Componente**: `ClientDetailComponent`
- **Funcionalidades**:
  - **Informações Completas** do cliente
  - **Histórico de Projetos**: Todos os projetos do cliente
  - **Linha do Tempo**: Interações e marcos importantes
  - **Documentos**: Arquivos relacionados ao cliente
  - **Notas e Observações**: Timeline de anotações
  - **Edição rápida** de informações básicas
  - **Opção de troca de senha**: Disponível para o cliente na tela de detalhes

### 4. **Gestão de Projetos**
#### 4.1 Lista de Projetos (`/projects`)
- **Componente**: `ProjectListComponent`
- **Funcionalidades**:
  - **Cards de Projeto** com informações resumidas
  - **Filtros Avançados**:
    - Status (em andamento, pausado, concluído)
    - Cliente
    - Período de criação
    - Valor
    - Etapa atual
  - **Visualização**: Grid ou lista
  - **Ordenação** múltipla
  - **Busca textual**
  - **Ações em lote**: Export, mudança de status
  - **Progress bars** visuais por projeto

#### 4.2 Formulário de Projeto (`/projects/new`, `/projects/:id/edit`)
- **Componente**: `ProjectFormComponent`
- **Funcionalidades**:
  - **Informações Básicas**:
    - Nome do projeto
    - Descrição detalhada
    - Cliente(s) vinculado(s) - seleção múltipla
    - Valor total do projeto
  - **Cronograma**:
    - Data de início
    - Prazo estimado
    - Data limite
  - **Localização**:
    - Endereço da obra
    - CEP
    - Referências de localização
  - **Escopo do Projeto**:
    - Ambientes incluídos (baseado no documento)
    - Área total (m²)
    - Observações técnicas
  - **Configuração de Etapas**:
    - Seleção das etapas que farão parte do projeto
    - Personalização de prazos por etapa
    - Valores individuais por etapa
  - **Anexos**: Upload de briefing, plantas existentes, etc.

#### 4.3 Detalhes do Projeto (`/projects/:id`)
- **Componente**: `ProjectDetailComponent`
- **Funcionalidades**:
  - **Cabeçalho com Informações Principais**:
    - Nome, cliente, valor, status
    - Progress bar geral
    - Ações rápidas (editar, pausar, finalizar)
  - **Abas de Navegação**:
    - **Visão Geral**: Resumo e métricas
    - **Timeline**: Linha do tempo das etapas
    - **Arquivos**: Documentos organizados por etapa
    - **Financeiro**: Valores, pagamentos, orçamentos
    - **Histórico**: Log de todas as alterações
  - **Widget de Etapa Atual**: Destaque para etapa em andamento
  - **Próximas Ações**: Lista de tarefas pendentes

#### 4.4 Timeline do Projeto (`/projects/:id/timeline`)
- **Componente**: `ProjectTimelineComponent`
- **Funcionalidades**:
  - **Linha do Tempo Visual** estilo Gantt
  - **Etapas Interativas**: Click para ver detalhes
  - **Status Visual**: Cores para cada status
  - **Marcos Importantes**: Datas de entrega, aprovações
  - **Zoom e Filtros**: Visualização por período
  - **Dependências**: Relações entre etapas
  - **Edição Inline**: Arrastar para reagendar
  - **Export**: PDF, imagem

### 5. **Gestão de Etapas**
#### 5.1 Formulário de Etapa (`/stages/new`, `/stages/:id/edit`)
- **Componente**: `StageFormComponent`
- **Funcionalidades**:
  - **Informações Básicas**:
    - Nome da etapa
    - Tipo de etapa (Levantamento, Briefing, etc.)
    - Descrição
    - Projeto vinculado
  - **Cronograma**:
    - Data de início planejada
    - Prazo estimado
    - Data limite
  - **Financeiro**:
    - Valor da etapa
    - Status de pagamento
  - **Campos Específicos por Tipo de Etapa**:
    - **Levantamento**: Local, data da visita, responsável
    - **Briefing**: Questionário, preferências do cliente
    - **Estudo Preliminar**: Número de alternativas, revisões
    - **Projeto Executivo**: Tipo de plantas, especialidades
    - **Assessoria Pós-Projeto**: Cronograma de visitas
  - **Upload de Arquivos**: Documentos relacionados à etapa
  - **Checklist de Atividades**: Tarefas internas da etapa

#### 5.2 Detalhes da Etapa (`/stages/:id`)
- **Componente**: `StageDetailComponent`
- **Funcionalidades**:
  - **Header da Etapa**: Nome, status, progresso
  - **Informações do Projeto**: Link e contexto
  - **Timeline da Etapa**: Marcos internos
  - **Arquivos e Documentos**: Organizados por categoria
  - **Notas e Observações**: Sistema de comentários
  - **Histórico de Alterações**: Log detalhado
  - **Ações Disponíveis**:
    - Iniciar etapa
    - Pausar/retomar
    - Marcar como concluída
    - Solicitar revisão

### 6. **Componentes Compartilhados**

#### 6.1 Header Principal
- **Componente**: `HeaderComponent`
- **Funcionalidades**:
  - Logo da empresa
  - Menu de navegação principal
  - Notificações
  - Perfil do usuário
  - Breadcrumb
  - Busca global

#### 6.2 Sidebar de Navegação
- **Componente**: `SidebarComponent`
- **Funcionalidades**:
  - Menu hierárquico
  - Indicadores de notificação
  - Links rápidos
  - Modo collapse/expand
  - Favoritos

#### 6.3 Upload de Arquivos
- **Componente**: `FileUploadComponent`
- **Funcionalidades**:
  - Drag & drop
  - Multiple files
  - Preview de imagens
  - Validação de tipo e tamanho
  - Progress bar de upload
  - Lista de arquivos com ações (remover, download)
  - Organização por categorias

#### 6.4 Modal de Confirmação
- **Componente**: `ConfirmationModalComponent`
- **Funcionalidades**:
  - Confirmações de exclusão
  - Alertas de alteração de status
  - Customização de mensagens
  - Botões de ação personalizáveis

#### 6.5 Loading Spinner
- **Componente**: `LoadingSpinnerComponent`
- **Funcionalidades**:
  - Indicador de carregamento
  - Overlay para bloqueio de tela
  - Diferentes tamanhos e estilos
  - Integração com interceptors HTTP

#### 6.6 Cards de Estatísticas
- **Componente**: `StatsCardComponent`
- **Funcionalidades**:
  - Display de métricas principais
  - Ícones e cores customizáveis
  - Animações de contadores
  - Links para drill-down

#### 6.7 Barra de Progresso
- **Componente**: `ProgressBarComponent`
- **Funcionalidades**:
  - Progresso visual de projetos/etapas
  - Múltiplos estilos (linear, circular)
  - Cores baseadas em status
  - Tooltips informativos

---

## ⚙️ Regras de Negócio

### 1. **Gestão de Etapas**
- **Uma etapa "em andamento" por projeto**: Sistema deve validar e impedir múltiplas etapas simultâneas
- **Sequência lógica**: Etapas devem seguir a ordem definida (configurável)
- **Transições válidas**:
  ```
  Pendente → Em Andamento → Concluída
  Pendente → Cancelada
  Em Andamento → Pausada → Em Andamento
  Em Andamento → Cancelada
  ```
- **Dependências**: Etapa só pode iniciar se a anterior estiver concluída (opcional)

### 2. **Workflow de Projetos**
- **Criação automática de etapas**: Ao criar projeto, gerar etapas padrão
- **Cálculo automático de progresso**: Baseado nas etapas concluídas
- **Notificações de prazo**: Alertas 3 dias antes do vencimento
- **Validação de datas**: Data fim deve ser posterior à data início

### 3. **Gestão de Arquivos**
- **Organização automática**: Arquivos organizados por projeto/etapa/categoria
- **Versionamento**: Manter histórico de versões
- **Validação de tipos**: Apenas tipos permitidos por categoria
- **Limite de tamanho**: Configurável por tipo de arquivo
- **Backup automático**: Cópia de segurança diária

### 4. **Permissões e Segurança**
- **Níveis de acesso**:
  - **Admin**: Acesso total
  - **Arquiteto**: CRUD projetos próprios
  - **Assistente**: Visualização e updates limitados
- **Auditoria**: Log de todas as operações críticas
- **Sessão segura**: JWT com refresh token

### 5. **Validações Específicas**
- **CPF/CNPJ**: Validação algoritmo oficial
- **Email**: Formato e unicidade
- **Telefone**: Formato brasileiro
- **CEP**: Integração com API ViaCEP
- **Datas**: Consistência entre datas relacionadas

---

## 🔧 Especificações Técnicas

### Backend (FastAPI)

#### Models e Schemas
- **SQLAlchemy Models**: Estrutura completa de dados com relacionamentos
- **Pydantic Schemas**: Validação e serialização de dados
- **Type Safety**: Type hints completos em todo o código
- **Validações Automáticas**: CPF/CNPJ, email, telefone, CEP

#### Arquitetura de Serviços
- **Service Layer**: Lógica de negócio separada dos endpoints
- **Repository Pattern**: Abstração de acesso aos dados
- **Dependency Injection**: Injeção de dependências com FastAPI
- **Cache Inteligente**: Cache automático com invalidação baseada em eventos

#### Segurança e Autenticação
- **JWT Tokens**: Autenticação stateless com refresh tokens
- **Role-based Access**: Controle de acesso baseado em funções
- **Password Hashing**: Bcrypt para hash de senhas
- **Session Management**: Gerenciamento seguro de sessões

#### API Design
- **RESTful APIs**: Endpoints seguindo padrões REST
- **OpenAPI/Swagger**: Documentação automática da API
- **Error Handling**: Tratamento consistente de erros
- **Response Formatting**: Padronização de respostas

#### Banco de Dados
- **PostgreSQL**: Banco principal com suporte a JSON
- **Alembic**: Migrações versionadas do banco
- **Connection Pooling**: Pool de conexões para performance
- **Indexes**: Índices otimizados para consultas frequentes

### Frontend (Angular SSR)

#### Arquitetura Angular
- **Server-Side Rendering**: Renderização no servidor para SEO
- **Standalone Components**: Componentes independentes (Angular 17+)
- **Reactive Forms**: Formulários reativos com validação
- **RxJS**: Programação reativa para gerenciamento de estado

#### UI/UX Design
- **Component Library**: Biblioteca de componentes reutilizáveis
- **Responsive Design**: Interface adaptável para diferentes telas
- **Loading States**: Estados de carregamento consistentes
- **Error Boundaries**: Tratamento de erros na interface

#### Performance
- **Lazy Loading**: Carregamento sob demanda de módulos
- **Tree Shaking**: Otimização de bundle
- **Caching Strategy**: Estratégia de cache no cliente
- **PWA Ready**: Preparado para Progressive Web App

### DevOps e Deploy

#### Containerização
- **Docker**: Containerização completa da aplicação
- **Docker Compose**: Orquestração de serviços locais
- **Multi-stage Builds**: Otimização de imagens Docker
- **Health Checks**: Verificações de saúde dos containers

#### CI/CD Pipeline
- **Automated Testing**: Testes automatizados em pipeline
- **Code Quality**: Análise de qualidade de código
- **Security Scanning**: Verificação de vulnerabilidades
- **Deployment Automation**: Deploy automatizado para produção

#### Monitoramento
- **Application Logs**: Logs estruturados da aplicação
- **Performance Metrics**: Métricas de performance
- **Error Tracking**: Rastreamento de erros em produção
- **Health Monitoring**: Monitoramento de saúde dos serviços

---

## 🚀 Setup e Desenvolvimento

### Pré-requisitos
- **Node.js** 18+
- **Python** 3.11+
- **PostgreSQL** 14+
- **Docker** & Docker Compose (opcional)

### Setup Local

#### 1. Clone e Configuração Inicial
```bash
git clone <repo-url> crialt-system
cd crialt-system
cp .env.example .env
# Editar .env com suas configurações
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Database setup
alembic upgrade head
python -m app.db.init_db  # Seed inicial

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend
npm install

# Development server
npm run dev

# Build for production
npm run build
npm run serve:ssr
```

#### 4. Docker Setup (Alternativa)
```bash
# Na raiz do projeto
docker-compose up -d
```

### Scripts Disponíveis

#### Backend
```bash
# Desenvolvimento
uvicorn app.main:app --reload

# Testes
pytest

# Migrações
alembic revision --autogenerate -m "description"
alembic upgrade head

# Linting
black app/
flake8 app/
mypy app/
```

#### Frontend
```bash
# Desenvolvimento
npm run dev

# Build
npm run build

# SSR
npm run serve:ssr

# Testes
npm run test
npm run e2e

# Linting
npm run lint
npm run lint:fix
```

### Estrutura de Desenvolvimento

#### Workflow Git
```
main
├── develop
│   ├── feature/client-management
│   ├── feature/project-timeline
│   └── feature/stage-workflow
└── hotfix/critical-bug
```

#### Padrões de Commit
```
feat: add client registration form
fix: resolve stage transition validation
docs: update API documentation
refactor: optimize database queries
test: add unit tests for project service
```

### Deploy e Produção

#### Variáveis de Ambiente
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost/crialt_prod
SECRET_KEY=your-super-secret-key
ENVIRONMENT=production

# Frontend (environment.prod.ts)
export const environment = {
  production: true,
  apiUrl: 'https://api.crialt.com',
  enableSSR: true
};
```

#### Docker Production
```bash
# Build images
docker build -f docker/backend.Dockerfile -t crialt-backend .
docker build -f docker/frontend.Dockerfile -t crialt-frontend .

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📈 Roadmap Futuro

### Fase 1 (MVP) - 3 meses
- [x] Autenticação e autorização
- [x] CRUD completo de clientes
- [x] CRUD completo de projetos
- [x] Sistema básico de etapas
- [ ] Upload e gestão de arquivos
- [x] Dashboard básico

### Fase 2 (Expansão) - 6 meses
- [ ] Timeline interativa avançada
- [ ] Notificações por email/WhatsApp
- [ ] Relatórios e exportações
- [ ] Sistema de templates de projeto
- [ ] Integração com assinatura digital
- [ ] App mobile (Progressive Web App)

### Fase 3 (Avançado) - 12 meses
- [ ] Integração com ferramentas CAD
- [ ] Sistema de orçamentos integrado
- [ ] Portal do cliente
- [ ] API pública para integrações
- [ ] BI e analytics avançados
- [ ] Multi-tenancy para outras arquitetônicas

---

## 🎯 Conclusão

Este sistema foi projetado especificamente para atender às necessidades da **Crialt Arquitetura**, baseando-se no fluxo real de trabalho documentado. A arquitetura monorepo com FastAPI e Angular SSR garante performance, escalabilidade e uma excelente experiência do usuário.

A estrutura modular permite crescimento orgânico, começando com funcionalidades essenciais e expandindo conforme a necessidade. O foco em type safety, SSR e boas práticas de desenvolvimento assegura um código maintível e robusto.

**Próximos passos**: Setup do ambiente de desenvolvimento e início da implementação seguindo as especificações detalhadas neste documento.

---

## 🔄 Paginação, Filtros e Ordenação nos Endpoints de Listagem

Todos os endpoints de listagem da API (clientes, projetos, etapas, arquivos, tarefas) implementam os seguintes recursos e formato de resposta:

- **Paginação**: Parâmetros `limit` (quantidade por página, padrão 20, máximo 100) e `offset` (página inicial, padrão 0).
- **Filtros**: Parâmetros de query para busca por campos relevantes (ex: nome, status, datas, cliente, etc). Cada endpoint aceita filtros específicos conforme o modelo.
- **Ordenação**: Parâmetros `order_by` (campo para ordenar, ex: `created_at`, `name`, etc) e `order_dir` (`asc` ou `desc`).

### Formato de resposta paginada
```json
{
  "total": 120,           // total de registros encontrados
  "count": 20,            // quantidade exibida nesta página
  "offset": 0,            // índice inicial
  "limit": 20,            // quantidade máxima por página
  "items": [ ... ]        // lista dos registros
}
```

### Exemplo de uso (clientes):
```http
GET /clients?limit=10&offset=0&order_by=name&order_dir=asc&name=João&is_active=true
```

### Endpoints cobertos:
- `/clients` (clientes)
- `/projects` (projetos)
- `/projects/my` (projetos do usuário)
- `/projects/client/{client_id}` (projetos por cliente)
- `/stages` (etapas)
- `/files` (arquivos)
- `/tasks` (tarefas)

Esses recursos garantem performance, flexibilidade e melhor experiência para telas de listagem, exportação e relatórios.

## 🔄 Cache Inteligente nos Endpoints de Listagem e Dashboard

Todos os endpoints de listagem e o dashboard utilizam cache inteligente no backend para garantir performance e dados atualizados. O cache é sensível aos parâmetros de paginação, filtros e ordenação, e é invalidado automaticamente nas ações de criação, edição e exclusão dos principais recursos (clientes, projetos, etapas, arquivos, tarefas).

- **Cache por parâmetros**: Cada combinação de filtros, ordenação e paginação gera uma chave única de cache.
- **Validação automática**: O cache é consultado antes de executar queries pesadas.
- **Invalidado em alterações**: Ao criar, editar ou excluir clientes, projetos, etapas, arquivos ou tarefas, o cache dos endpoints relacionados e do dashboard é limpo automaticamente.
- **Dashboard sempre atualizado**: O cache do dashboard é invalidado junto com qualquer alteração relevante nos dados principais.
- **Configuração flexível**: O tempo de expiração do cache pode ser ajustado conforme necessidade.

### Exemplo de funcionamento
- Ao criar um novo cliente, o cache das listagens de clientes e do dashboard é invalidado.
- Ao editar um projeto, o cache das listagens de projetos e do dashboard é invalidado.
- O mesmo ocorre para etapas, arquivos e tarefas.

Essa abordagem garante alta performance nas consultas e consistência dos dados exibidos para todos os usuários.

---

## 📁 Sistema de Upload Chunked

### Visão Geral
O sistema implementa upload chunked robusto para arquivos grandes com retry automático, verificação de integridade e gerenciamento inteligente de falhas.

### Características Principais
- ✅ **Retry automático** com backoff exponencial
- ✅ **Verificação de integridade** de chunks (MD5) e arquivo final (SHA-256)
- ✅ **Controle de transações** para evitar race conditions
- ✅ **Logging detalhado** para debugging
- ✅ **Timeouts configuráveis** (5 minutos por chunk)
- ✅ **Limpeza automática** de uploads expirados (24h)
- ✅ **Endpoint de retry** para chunks faltando

### Configurações
```python
# Em config.py
UPLOAD_DIR = "app/storage/uploads"
MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1GB
MAX_CHUNK_SIZE = 50 * 1024 * 1024  # 50MB por chunk
CHUNK_UPLOAD_TIMEOUT = 300  # 5 minutos
CHUNKED_UPLOAD_EXPIRY_HOURS = 24  # Expiração em 24h
```

### Endpoints da API

#### 1. Iniciar Upload
```
POST /api/files/chunked/initiate
```
**Body:**
```json
{
  "filename": "video.mp4",
  "total_chunks": 36,
  "chunk_size": 1048576,
  "total_size": 37748736,
  "file_checksum": "a1b2c3d4e5f6...",
  "mime_type": "video/mp4",
  "category": "video",
  "project_id": "uuid-here",
  "description": "Descrição opcional"
}
```

#### 2. Enviar Chunk
```
POST /api/files/chunked/{upload_id}/chunk/{chunk_number}
Content-Type: multipart/form-data
```

#### 3. Verificar Status
```
GET /api/files/chunked/{upload_id}/status
```
**Response:**
```json
{
  "upload_id": "abc123_1703276400",
  "filename": "video.mp4",
  "total_chunks": 36,
  "uploaded_chunks": [1, 2, 3, 6, 7, 8, 9],
  "missing_chunks": [4, 5, 10, 11, 12, 13],
  "progress": 19.44,
  "is_completed": false,
  "expires_at": "2024-01-23T10:00:00Z"
}
```

#### 4. Retry de Chunks Faltando
```
GET /api/files/chunked/{upload_id}/retry
```

#### 5. Finalizar Upload
```
POST /api/files/chunked/{upload_id}/complete
```

#### 6. Cancelar Upload
```
DELETE /api/files/chunked/{upload_id}
```

#### 7. Limpeza de Uploads Expirados (Admin)
```
POST /api/files/chunked/cleanup
```

### Implementação Frontend Recomendada

```typescript
class ChunkedUploadService {
  private maxRetries = 3;
  private retryDelay = 1000;

  async uploadFileWithRetry(file: File, metadata: UploadMetadata): Promise<string> {
    // 1. Iniciar upload
    const uploadResponse = await this.initiateUpload({
      filename: file.name,
      total_size: file.size,
      total_chunks: Math.ceil(file.size / this.chunkSize),
      chunk_size: this.chunkSize,
      file_checksum: await this.calculateSHA256(file),
      ...metadata
    });

    const uploadId = uploadResponse.upload_id;
    const chunks = this.splitFileIntoChunks(file);

    // 2. Upload chunks com retry individual
    for (let i = 0; i < chunks.length; i++) {
      const chunkNumber = i + 1;
      await this.uploadChunkWithRetry(uploadId, chunkNumber, chunks[i]);
    }

    // 3. Finalizar com retry para chunks faltando
    return await this.completeUploadWithRetry(uploadId);
  }

  private async completeUploadWithRetry(uploadId: string): Promise<string> {
    try {
      const result = await this.completeUpload(uploadId);
      return result.final_file_id;
    } catch (error) {
      if (error.response?.status === 400 && 
          error.response?.data?.detail?.includes('Chunks faltando')) {
        
        // Obter lista de chunks faltando
        const status = await this.getUploadStatus(uploadId);
        const missingChunks = status.missing_chunks;
        
        if (missingChunks && missingChunks.length > 0) {
          console.log(`Retrying ${missingChunks.length} missing chunks:`, missingChunks);
          
          // Reenviar apenas chunks faltando
          for (const chunkNumber of missingChunks) {
            const chunk = this.getChunkFromFile(chunkNumber);
            await this.uploadChunkWithRetry(uploadId, chunkNumber, chunk);
          }
          
          // Tentar finalizar novamente
          return await this.completeUpload(uploadId).then(r => r.final_file_id);
        }
      }
      throw error;
    }
  }
}
```

### Monitoramento e Troubleshooting

#### Logs Importantes
```
INFO - Iniciando upload chunked: video.mp4, 36 chunks
DEBUG - Chunk 1 enviado com sucesso (tentativa 1)
WARNING - Tentativa 1 falhou para chunk 5: Timeout
DEBUG - Chunk 5 enviado com sucesso (tentativa 2)
WARNING - Upload abc123 com chunks faltando: [4, 5, 10]
INFO - Upload abc123 completado com sucesso
```

#### Problemas Resolvidos
1. **"Chunks faltando" após upload completo**
   - ✅ Verificação tripla (BD + disco + integridade)
   - ✅ Retry automático implementado

2. **Race conditions em uploads paralelos**
   - ✅ Lock de transação com `nowait=True`
   - ✅ Arquivos temporários únicos por tentativa

3. **Uploads ficando órfãos**
   - ✅ Expiração automática em 24h
   - ✅ Limpeza agendada disponível

4. **Chunks corrompidos**
   - ✅ Verificação MD5 por chunk
   - ✅ Checksum SHA-256 do arquivo final

### Performance e Configurações Recomendadas
- **Chunk size**: 5-10MB para conexões normais, até 50MB para rápidas
- **Paralelo**: Máximo 3-5 chunks simultâneos
- **Timeout**: 5 minutos por chunk
- **Retry**: Máximo 3 tentativas com backoff exponencial

---

## 🔧 Setup e Desenvolvimento
