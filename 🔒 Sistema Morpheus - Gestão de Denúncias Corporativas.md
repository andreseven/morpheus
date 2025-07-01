# 🔒 Sistema Morpheus - Gestão de Denúncias Corporativas

![Morpheus Logo](https://via.placeholder.com/200x80/2563eb/ffffff?text=MORPHEUS)

## 📋 Sobre o Projeto

O **Sistema Morpheus** é uma plataforma completa para gestão de denúncias corporativas com hierarquia de acesso, desenvolvida para empresas que precisam de um canal seguro e eficiente para receber, processar e acompanhar denúncias relacionadas a:

- 🛡️ **Segurança da Informação**
- 💰 **Fraudes e Integridade Corporativa**  
- 👥 **Conduta, Compliance e Recursos Humanos**

## ✨ Principais Funcionalidades

### 🔐 Sistema de Autenticação
- Login seguro com criptografia de senhas
- Hierarquia de usuários (Super Admin, Admin Cliente, Auditoria, Gerente, Usuário)
- Sessões persistentes e logout seguro

### 📊 Gestão de Denúncias
- Criação de denúncias anônimas ou identificadas
- Categorização modular e personalizável
- Sistema de protocolos únicos
- Acompanhamento por status (Recebida, Em Análise, Concluída, Arquivada)
- Níveis de prioridade (Baixa, Média, Alta, Crítica)

### ⚙️ Configurações Personalizáveis
- Customização visual por empresa (logo, cores)
- Gestão modular de categorias de denúncias
- Configurações específicas por cliente

### 📈 Relatórios e Análises
- Dashboard com estatísticas em tempo real
- Relatórios detalhados com filtros avançados
- Exportação em JSON e CSV
- Métricas de performance e resolução

### 🎨 Interface Moderna
- Design responsivo e intuitivo
- Compatibilidade mobile
- Navegação fluida entre módulos
- Feedback visual para todas as ações

## 🚀 Tecnologias Utilizadas

### Frontend
- **React 18** + **Vite** - Framework moderno e rápido
- **Tailwind CSS** - Estilização utilitária
- **React Router** - Navegação SPA
- **Context API** - Gerenciamento de estado

### Backend
- **Flask** (Python) - Framework web minimalista
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados relacional
- **Werkzeug** - Segurança e utilitários

## 📦 Instalação e Execução

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- pnpm (recomendado)

### 1. Clone o repositório
```bash
git clone <repository-url>
cd morpheus
```

### 2. Configure o Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python src/create_db.py
python src/simple_seed.py
python src/main.py
```

### 3. Configure o Frontend
```bash
cd frontend
pnpm install
pnpm run dev --host
```

### 4. Acesse o Sistema
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000

## 🔑 Credenciais de Teste

### Usuário Administrador
- **Email**: `admin@morpheus.com`
- **Senha**: `admin123`
- **Perfil**: Super Admin

## 📁 Estrutura do Projeto

```
morpheus/
├── 📁 frontend/              # Aplicação React
│   ├── 📁 src/
│   │   ├── 📁 components/    # Componentes React
│   │   ├── 📁 contexts/      # Context API
│   │   └── 📄 App.jsx        # App principal
│   └── 📄 vite.config.js
│
├── 📁 backend/               # API Flask
│   ├── 📁 src/
│   │   ├── 📁 models/        # Modelos de dados
│   │   ├── 📁 routes/        # Rotas da API
│   │   └── 📄 main.py        # App principal
│   └── 📄 requirements.txt
│
├── 📄 README.md              # Este arquivo
└── 📄 SISTEMA_MORPHEUS_COMPLETO.md  # Documentação técnica
```

## 🎯 Funcionalidades por Perfil

### 👑 Super Admin
- Acesso total ao sistema
- Gestão de todas as empresas
- Relatórios consolidados
- Configurações globais

### 🏢 Admin do Cliente
- Gestão da própria empresa
- Configurações personalizadas
- Relatórios da empresa
- Gestão de usuários internos

### 🔍 Auditoria
- Visualização de denúncias
- Análise e investigação
- Relatórios especializados
- Histórico completo

### 👨‍💼 Gerente
- Gestão operacional
- Acompanhamento de casos
- Relatórios departamentais

### 👤 Usuário Comum
- Criação de denúncias
- Acompanhamento de protocolos
- Comunicação anônima

## 🛡️ Segurança

- ✅ Criptografia de senhas com hash seguro
- ✅ Validação de sessões
- ✅ Proteção contra SQL injection
- ✅ CORS configurado adequadamente
- ✅ Sanitização de dados de entrada

## 📊 APIs Disponíveis

### Autenticação
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Dados do usuário

### Denúncias
- `GET /api/denuncias` - Listar denúncias
- `POST /api/denuncias` - Criar denúncia
- `GET /api/denuncias/estatisticas` - Estatísticas

### Configurações
- `GET /api/configuracoes/empresa` - Config da empresa
- `GET /api/configuracoes/categorias` - Categorias

### Relatórios
- `GET /api/relatorios/dashboard` - Dashboard
- `GET /api/relatorios/detalhado` - Relatório filtrado

## 🚀 Deploy em Produção

### Recomendações
- Use **PostgreSQL** ou **MySQL** em produção
- Configure **HTTPS** obrigatório
- Implemente **rate limiting**
- Configure **logs** adequados
- Use **Docker** para containerização

### Variáveis de Ambiente
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://yourdomain.com
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o sistema:

- 📧 Email: suporte@morpheus.com
- 📱 WhatsApp: (11) 99999-9999
- 🌐 Website: https://morpheus.com

---

**Desenvolvido com ❤️ pela equipe Manus**

![Status](https://img.shields.io/badge/Status-Completo-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

