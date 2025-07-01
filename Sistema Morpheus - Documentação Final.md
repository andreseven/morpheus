# Sistema Morpheus - Documentação Final

## Visão Geral
O **Sistema Morpheus** é uma plataforma completa de gestão de denúncias corporativas com hierarquia de acesso, desenvolvida com tecnologias modernas e escaláveis.

## Tecnologias Utilizadas

### Frontend
- **React 18** com Vite
- **Tailwind CSS** para estilização
- **React Router** para navegação
- **Context API** para gerenciamento de estado
- **Fetch API** para comunicação com backend

### Backend
- **Flask** (Python) como framework web
- **SQLAlchemy** como ORM
- **SQLite** como banco de dados
- **Flask-CORS** para comunicação cross-origin
- **Werkzeug** para hash de senhas

### Infraestrutura
- **Vite Dev Server** para desenvolvimento frontend
- **Flask Development Server** para backend
- **Proxy configurado** para comunicação frontend/backend

## Funcionalidades Implementadas

### 1. Sistema de Autenticação
- ✅ Login seguro com hash de senhas
- ✅ Sessões persistentes
- ✅ Logout funcional
- ✅ Proteção de rotas

### 2. Hierarquia de Usuários
- ✅ **Super Admin**: Acesso total ao sistema
- ✅ **Admin do Cliente**: Gestão da própria empresa
- ✅ **Auditoria**: Visualização e análise de denúncias
- ✅ **Gerente**: Gestão operacional
- ✅ **Usuário Comum**: Criação de denúncias

### 3. Gestão de Denúncias
- ✅ Listagem completa com filtros
- ✅ Categorização modular:
  - Segurança da Informação
  - Fraudes e Integridade Corporativa
  - Conduta, Compliance e Recursos Humanos
- ✅ Status de acompanhamento:
  - Recebida
  - Em Análise
  - Concluída
  - Arquivada
- ✅ Níveis de prioridade:
  - Baixa, Média, Alta, Crítica
- ✅ Protocolos únicos gerados automaticamente
- ✅ Denúncias anônimas e identificadas

### 4. Configurações do Sistema
- ✅ **Configurações da Empresa**:
  - Personalização de nome
  - Upload de logo
  - Cores personalizadas (primária, secundária, texto)
- ✅ **Gestão de Categorias**:
  - Criação/edição de categorias
  - Ativação/desativação
  - Contagem de subcategorias
  - Sistema modular por empresa

### 5. Relatórios e Análises
- ✅ **Dashboard de Estatísticas**:
  - Total de denúncias
  - Distribuição por status
  - Distribuição por categoria
  - Distribuição por prioridade
- ✅ **Relatórios Detalhados**:
  - Filtros avançados (data, categoria, status, prioridade)
  - Cálculo de dias médios de resolução
  - Exportação em JSON e CSV
- ✅ **Métricas por Empresa** (Super Admin)

### 6. Interface do Usuário
- ✅ Design moderno e responsivo
- ✅ Navegação intuitiva com React Router
- ✅ Sistema de tabs organizadas
- ✅ Feedback visual para ações
- ✅ Cards informativos com ícones
- ✅ Formulários validados
- ✅ Compatibilidade mobile

## Estrutura do Projeto

```
morpheus/
├── frontend/                 # Aplicação React
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Denuncias.jsx
│   │   │   ├── Configuracoes.jsx
│   │   │   └── Relatorios.jsx
│   │   ├── contexts/        # Context API
│   │   │   └── AuthContext.jsx
│   │   └── App.jsx          # Componente principal
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/                 # API Flask
│   ├── src/
│   │   ├── models/         # Modelos de dados
│   │   │   ├── usuario.py
│   │   │   ├── empresa.py
│   │   │   ├── denuncia.py
│   │   │   └── configuracao.py
│   │   ├── routes/         # Rotas da API
│   │   │   ├── auth.py
│   │   │   ├── usuarios.py
│   │   │   ├── empresas.py
│   │   │   ├── denuncias.py
│   │   │   ├── configuracoes.py
│   │   │   └── relatorios.py
│   │   ├── database/       # Banco de dados
│   │   │   └── app.db
│   │   ├── database.py     # Configuração do DB
│   │   └── main.py         # Aplicação principal
│   └── requirements.txt
│
└── SISTEMA_MORPHEUS_COMPLETO.md
```

## Banco de Dados

### Tabelas Principais
1. **usuarios** - Gestão de usuários e perfis
2. **empresas** - Dados das empresas clientes
3. **denuncias** - Registro de denúncias
4. **historico_denuncias** - Auditoria de ações
5. **categorias_denuncia** - Categorias modulares
6. **subcategorias_denuncia** - Subcategorias
7. **configuracao_empresa** - Configurações personalizadas

### Relacionamentos
- Usuários pertencem a empresas
- Denúncias são vinculadas a empresas e usuários
- Histórico rastreia todas as ações
- Configurações são específicas por empresa

## APIs Implementadas

### Autenticação
- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/logout` - Logout de usuário
- `GET /api/auth/me` - Dados do usuário logado

### Denúncias
- `GET /api/denuncias` - Listar denúncias
- `POST /api/denuncias` - Criar denúncia
- `GET /api/denuncias/{id}` - Detalhes da denúncia
- `PUT /api/denuncias/{id}` - Atualizar denúncia
- `GET /api/denuncias/estatisticas` - Estatísticas

### Configurações
- `GET /api/configuracoes/empresa` - Configurações da empresa
- `PUT /api/configuracoes/empresa` - Atualizar configurações
- `GET /api/configuracoes/categorias` - Listar categorias
- `POST /api/configuracoes/categorias` - Criar categoria

### Relatórios
- `GET /api/relatorios/dashboard` - Dashboard de estatísticas
- `GET /api/relatorios/detalhado` - Relatório com filtros
- `GET /api/relatorios/empresas` - Métricas por empresa

## Dados de Teste

### Usuário Administrador
- **Email**: admin@morpheus.com
- **Senha**: admin123
- **Perfil**: Super Admin

### Empresa
- **Nome**: Morpheus Corp
- **CNPJ**: 12.345.678/0001-90

### Denúncias de Exemplo
1. Vazamento de dados confidenciais (Alta prioridade)
2. Suspeita de fraude em licitação (Crítica)
3. Assédio moral no departamento (Alta)
4. Uso inadequado de recursos (Concluída)
5. Acesso não autorizado a sistemas (Alta)

## Como Executar

### Backend
```bash
cd backend
source venv/bin/activate
python src/main.py
```

### Frontend
```bash
cd frontend
pnpm run dev --host
```

### Acesso
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:5000

## Funcionalidades Avançadas

### Segurança
- Hash de senhas com Werkzeug
- Validação de sessões
- Proteção contra SQL injection (SQLAlchemy)
- CORS configurado adequadamente

### Escalabilidade
- Arquitetura modular
- Separação frontend/backend
- API RESTful
- Banco de dados relacional

### Usabilidade
- Interface responsiva
- Navegação intuitiva
- Feedback visual
- Filtros avançados
- Exportação de dados

## Status do Projeto

✅ **COMPLETO E FUNCIONAL**

Todas as funcionalidades principais foram implementadas e testadas:
- Sistema de autenticação ✅
- Gestão de denúncias ✅
- Configurações personalizáveis ✅
- Relatórios e análises ✅
- Interface moderna ✅
- APIs completas ✅

O sistema está pronto para uso em produção após configuração adequada de infraestrutura e segurança.

---

**Desenvolvido por**: Manus AI
**Data**: Julho 2025
**Versão**: 1.0.0

