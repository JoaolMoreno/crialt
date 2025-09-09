# Sistema de Gestão de Projetos Arquitetônicos
**Crialt Arquitetura - Painel Administrativo**

## 📋 Sumário
1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Estrutura do Monorepo](#estrutura-do-monorepo)
4. [Funcionalidades e Telas](#funcionalidades-e-telas)
5. [Modelos de Dados](#modelos-de-dados)
6. [Regras de Negócio](#regras-de-negócio)
7. [Especificações Técnicas](#especificações-técnicas)
8. [Setup e Desenvolvimento](#setup-e-desenvolvimento)

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
│   │   │   ├── stage.py
│   │   │   └── file.py
│   │   │
│   │   ├── schemas/                      # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── common.py                 # Schemas comuns
│   │   │   ├── user.py
│   │   │   ├── client.py
│   │   │   ├── project.py
│   │   │   ├── stage.py
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
│   │   │   ├── stages.py
│   │   │   └── files.py
│   │   │
│   │   ├── services/                     # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── client_service.py
│   │   │   ├── project_service.py
│   │   │   ├── stage_service.py
│   │   │   └── file_service.py
│   │   │
│   │   ├── utils/                        # Utilitários
│   │   │   ├── __init__.py
│   │   │   ├── validators.py
│   │   │   ├── formatters.py
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
│       └── test_stages.py
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

## 📊 Modelos de Dados

### 1. **Usuario (User)**
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  password_hash: string;
  role: UserRole; // 'admin' | 'architect' | 'assistant'
  avatar?: string;
  is_active: boolean;
  created_at: DateTime;
  updated_at: DateTime;
  last_login?: DateTime;
}
```

### 2. **Cliente (Client)**
```typescript
interface Client {
  id: string;
  // Dados Pessoais/Empresariais
  name: string;
  document: string; // CPF ou CNPJ
  document_type: 'cpf' | 'cnpj';
  rg_ie?: string;
  birth_date?: Date;
  
  // Contato
  email: string;
  secondary_email?: string;
  phone: string;
  mobile?: string;
  whatsapp?: string;

  // Senha de acesso do cliente
  password_hash: string;
  first_access: boolean;
  
  // Endereço
  address: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
  };
  
  // Meta
  notes?: string;
  is_active: boolean;
  created_at: DateTime;
  updated_at: DateTime;
  
  // Relacionamentos
  projects: Project[];
  documents: File[];
}
```

### 3. **Projeto (Project)**
```typescript
interface Project {
  id: string;
  name: string;
  description?: string;
  
  // Valores
  total_value: number;
  currency: string; // 'BRL'
  
  // Cronograma
  start_date: Date;
  estimated_end_date: Date;
  actual_end_date?: Date;
  
  // Status
  status: ProjectStatus; // 'draft' | 'active' | 'paused' | 'completed' | 'cancelled'
  
  // Localização da Obra
  work_address: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zip_code: string;
    reference?: string;
  };
  
  // Escopo
  scope: {
    total_area?: number; // m²
    rooms_included: string[]; // Lista de ambientes
    technical_notes?: string;
  };
  
  // Meta
  notes?: string;
  created_at: DateTime;
  updated_at: DateTime;
  
  // Relacionamentos
  clients: Client[]; // Many-to-many
  stages: Stage[];
  files: File[];
  created_by: User;
}
```

### 4. **Etapa (Stage)**
```typescript
interface Stage {
  id: string;
  name: string;
  type: StageType;
  description?: string;
  order: number; // Ordem na sequência
  
  // Status e Cronograma
  status: StageStatus; // 'pending' | 'in_progress' | 'completed' | 'cancelled' | 'on_hold'
  planned_start_date: Date;
  actual_start_date?: Date;
  planned_end_date: Date;
  actual_end_date?: Date;
  
  // Financeiro
  value: number;
  payment_status: PaymentStatus; // 'pending' | 'partial' | 'paid'
  
  // Campos Específicos por Tipo
  specific_data: StageSpecificData;
  
  // Progress
  progress_percentage: number; // 0-100
  
  // Meta
  notes?: string;
  created_at: DateTime;
  updated_at: DateTime;
  
  // Relacionamentos
  project: Project;
  files: File[];
  tasks: Task[];
  created_by: User;
  assigned_to?: User;
}

// Tipos de Etapa baseados no documento da Crialt
enum StageType {
  LEVANTAMENTO = 'levantamento',
  BRIEFING = 'briefing',
  ESTUDO_PRELIMINAR = 'estudo_preliminar',
  PROJETO_EXECUTIVO = 'projeto_executivo',
  ASSESSORIA_POS_PROJETO = 'assessoria_pos_projeto'
}

// Dados específicos por tipo de etapa
type StageSpecificData = 
  | LevantamentoData 
  | BriefingData 
  | EstudoPreliminarData 
  | ProjetoExecutivoData 
  | AssessoriaData;

interface LevantamentoData {
  visit_date?: Date;
  responsible?: string;
  measurements_taken: boolean;
  photos_taken: boolean;
  site_conditions?: string;
}

interface BriefingData {
  questionnaire_completed: boolean;
  client_preferences?: string;
  style_references?: string[];
  budget_defined: boolean;
  special_requirements?: string;
}

interface EstudoPreliminarData {
  alternatives_count: number;
  layout_approved: boolean;
  renders_generated: boolean;
  client_feedback?: string;
  revisions_count: number;
}

interface ProjetoExecutivoData {
  technical_drawings: string[]; // Tipos de plantas
  specifications_ready: boolean;
  materials_defined: boolean;
  complementary_projects: string[]; // elétrico, hidráulico, etc.
}

interface AssessoriaData {
  visit_schedule: {
    date: Date;
    type: string;
    completed: boolean;
  }[];
  suppliers_meetings: number;
  decoration_phase: boolean;
}
```

### 5. **Arquivo (File)**
```typescript
interface File {
  id: string;
  original_name: string;
  stored_name: string;
  path: string;
  size: number; // bytes
  mime_type: string;
  
  // Categorização
  category: FileCategory; // 'document' | 'image' | 'plan' | 'render' | 'contract'
  tags: string[];
  
  // Relacionamentos
  project_id?: string;
  client_id?: string;
  stage_id?: string;
  
  // Meta
  description?: string;
  uploaded_by: User;
  created_at: DateTime;
  updated_at: DateTime;
}
```

### 6. **Tarefa (Task)**
```typescript
interface Task {
  id: string;
  title: string;
  description?: string;
  
  // Status
  status: TaskStatus; // 'todo' | 'in_progress' | 'completed' | 'cancelled'
  priority: TaskPriority; // 'low' | 'medium' | 'high' | 'urgent'
  
  // Cronograma
  due_date?: Date;
  completed_at?: DateTime;
  
  // Relacionamentos
  stage_id: string;
  assigned_to?: User;
  created_by: User;
  
  // Meta
  created_at: DateTime;
  updated_at: DateTime;
}
```

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

### Checklist de Implementação Backend

**Já implementado:**
- Estrutura de pastas e arquivos do backend (conforme monorepo)
- Dockerfile, requirements.txt, pyproject.toml, alembic.ini, .env
- Alembic configurado e pronto para migrações
- Models SQLAlchemy: user, client, project, stage, file, task
- Schemas Pydantic: user, client, project, stage, file, task
- Serviços: auth_service, project_service, file_service
- Utils: validators.py, constants.py
- Rotas principais: auth, users, clients, projects, stages, files
- Validações: CPF/CNPJ, email, telefone, CEP (ViaCEP), datas
- Permissões e segurança: JWT, roles, troca/redefinição de senha
- Criação automática de etapas ao criar projeto
- Cálculo automático de progresso do projeto
- Organização automática de arquivos por categoria
- Versionamento básico de arquivos
- Limite de tamanho e tipos permitidos de arquivo
- Estrutura de storage local
- Dependências e setup do ambiente
- Testes: estrutura inicial criada

**Falta implementar (MVP):**
- Notificações de prazo (alertas 3 dias antes do vencimento)
- Backup automático de arquivos
- Auditoria (logs de operações críticas)
- Serviços e rotas para stage_service, client_service, task_service (separados)
- Testes unitários e de integração completos
- Exportação de dados (Excel/PDF)
- Relatórios gerenciais e dashboards
- Integração com email para envio de senha/redefinição

### Frontend (Angular SSR)

#### Dependências Principais
```json
{
  "dependencies": {
    "@angular/core": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/router": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-server": "^17.0.0",
    "@angular/ssr": "^17.0.0",
    "@angular/material": "^17.0.0",
    "@angular/cdk": "^17.0.0",
    "rxjs": "^7.8.0",
    "chart.js": "^4.4.0",
    "ng2-charts": "^5.0.0",
    "ngx-mask": "^16.4.0",
    "ngx-loading": "^16.0.0"
  }
}
```

#### Configuração SSR
```typescript
// app.config.server.ts
import { ApplicationConfig, mergeApplicationConfig } from '@angular/core';
import { provideServerRendering } from '@angular/platform-server';
import { appConfig } from './app.config';

const serverConfig: ApplicationConfig = {
  providers: [
    provideServerRendering(),
    // Server-specific providers
  ]
};

export const config = mergeApplicationConfig(appConfig, serverConfig);
```

#### Service com Type Safety - Exemplo
```typescript
// core/services/project.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { Project, ProjectCreate, ProjectUpdate } from '../models/project.model';
import { ApiResponse, PaginatedResponse } from '../models/common.model';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = '/api/v1/projects';
  
  // State management
  private projectsSubject = new BehaviorSubject<Project[]>([]);
  public projects$ = this.projectsSubject.asObservable();
  
  getProjects(
    page: number = 1, 
    limit: number = 10,
    filters?: Record<string, any>
  ): Observable<PaginatedResponse<Project>> {
    const params = { page: page.toString(), limit: limit.toString(), ...filters };
    return this.http.get<PaginatedResponse<Project>>(this.apiUrl, { params });
  }
  
  getProjectById(id: string): Observable<ApiResponse<Project>> {
    return this.http.get<ApiResponse<Project>>(`${this.apiUrl}/${id}`);
  }
  
  createProject(project: ProjectCreate): Observable<ApiResponse<Project>> {
    return this.http.post<ApiResponse<Project>>(this.apiUrl, project);
  }
  
  updateProject(id: string, project: ProjectUpdate): Observable<ApiResponse<Project>> {
    return this.http.put<ApiResponse<Project>>(`${this.apiUrl}/${id}`, project);
  }
  
  deleteProject(id: string): Observable<ApiResponse<void>> {
    return this.http.delete<ApiResponse<void>>(`${this.apiUrl}/${id}`);
  }
}
```

#### Componente com Separação de Arquivos
```typescript
// features/projects/project-list/project-list.component.ts
import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Subject, takeUntil } from 'rxjs';

import { ProjectService } from '../../../core/services/project.service';
import { Project } from '../../../core/models/project.model';

@Component({
  selector: 'app-project-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './project-list.component.html',
  styleUrl: './project-list.component.scss'
})
export class ProjectListComponent implements OnInit, OnDestroy {
  private readonly projectService = inject(ProjectService);
  private readonly destroy$ = new Subject<void>();
  
  projects: Project[] = [];
  displayedColumns: string[] = ['name', 'client', 'status', 'progress', 'actions'];
  loading = false;
  
  ngOnInit(): void {
    this.loadProjects();
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  
  private loadProjects(): void {
    this.loading = true;
    this.projectService.getProjects()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.projects = response.data;
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading projects:', error);
          this.loading = false;
        }
      });
  }
  
  onEditProject(project: Project): void {
    // Navigation logic
  }
  
  onDeleteProject(project: Project): void {
    // Delete confirmation logic
  }
}
```

#### SSR Otimizações
- **Resolvers**: Pré-carregar dados no servidor
- **Meta tags**: SEO dinâmico por página
- **Cache HTTP**: Estratégias de cache para performance
- **Lazy loading**: Módulos carregados sob demanda
- **State transfer**: Transferir estado servidor→cliente

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
- [ ] Autenticação e autorização
- [ ] CRUD completo de clientes
- [ ] CRUD completo de projetos
- [ ] Sistema básico de etapas
- [ ] Upload e gestão de arquivos
- [ ] Dashboard básico

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

## 🔧 Endpoints de Senha

### Alteração de Senha (Usuário ou Cliente)

- **Endpoint:** `PATCH /auth/change-password`
- **Descrição:** Permite ao usuário logado (admin, arquiteto, assistente ou cliente) alterar sua própria senha.
- **Payload:**
  ```json
  {
    "current_password": "string",
    "new_password": "string"
  }
  ```
- **Regras:**
  - Usuário deve estar autenticado
  - Para clientes, se `first_access` estiver true, obrigar troca de senha no primeiro login
  - Validação de senha forte
  - Atualiza campo `first_access` para false após troca

### Redefinição de Senha pelo Admin

- **Endpoint:** `POST /clients/{id}/reset-password`
- **Descrição:** Permite ao admin redefinir a senha de um cliente (gera nova senha e envia por email ou exibe na tela)
- **Payload:**
  ```json
  {
    "new_password": "string" // opcional, se não enviado, sistema gera automaticamente
  }
  ```
- **Regras:**
  - Apenas admin pode acessar
  - Atualiza campo `first_access` para true

