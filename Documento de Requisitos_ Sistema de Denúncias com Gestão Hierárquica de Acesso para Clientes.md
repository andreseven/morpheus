# Documento de Requisitos: Sistema de Denúncias com Gestão Hierárquica de Acesso para Clientes

## 1. Introdução

Este documento detalha os requisitos funcionais e não funcionais para o desenvolvimento de um Sistema de Denúncias com Gestão Hierárquica de Acesso para Clientes. O objetivo é criar uma plataforma web robusta e segura para o registro, acompanhamento e tratamento de denúncias relacionadas a fraudes, segurança da informação e conduta, garantindo conformidade e integridade corporativa para empresas privadas.

## 2. Tecnologias Utilizadas

Este projeto será desenvolvido utilizando um conjunto de tecnologias modernas e escaláveis, abrangendo tanto o frontend quanto o backend, além de serviços de autenticação e hospedagem.

*   **Frontend:**
    *   **React:** Biblioteca JavaScript para construção de interfaces de usuário dinâmicas e reativas.
    *   **TailwindCSS:** Framework CSS utilitário para estilização rápida e responsiva, permitindo a criação de designs personalizados sem a necessidade de escrever CSS do zero.

*   **Backend:**
    *   **Firebase:** Plataforma de desenvolvimento de aplicativos do Google, que inclui:
        *   **Firestore:** Banco de dados NoSQL baseado em nuvem, flexível e escalável, ideal para armazenar os dados do sistema de denúncias.
        *   **Firebase Functions:** Funções serverless que permitem executar código backend em resposta a eventos do Firebase e requisições HTTP, sem a necessidade de gerenciar servidores.
    *   **Serviço de Envio de E-mail (via Firebase Functions):** Para notificações por e-mail.

*   **Autenticação:**
    *   **Firebase Auth:** Serviço de autenticação completo que suporta diversos métodos de login (e-mail/senha, SSO, etc.), facilitando a gestão de usuários e a segurança do acesso.

*   **Hospedagem e Deploy:**
    *   **Netlify:** Plataforma de hospedagem e automação de deploy para o frontend (React), oferecendo integração contínua com repositórios Git e deploy automático.
    *   **Firebase Hosting:** Utilizado para hospedar as funções do Firebase e, se necessário, outros ativos estáticos do backend.

## 3. Escopo do Projeto

### 3.1. Objetivo

Criar um sistema web robusto e seguro para o registro, acompanhamento e tratamento de denúncias, com um controle de acesso hierárquico bem definido. O sistema visa atender às necessidades de empresas privadas na gestão de temas sensíveis como fraudes, segurança da informação e conduta, garantindo conformidade e integridade corporativa.

### 3.2. Classificação Temática das Denúncias

O sistema permitirá a classificação de denúncias em categorias principais, com seus respectivos subitens. Esta estrutura é modular, permitindo que os itens sejam adicionados, removidos ou editados conforme a necessidade específica de cada empresa, garantindo flexibilidade e adaptabilidade.

*   **Segurança da Informação:**
    *   Acesso à informação, Dados Pessoais - LGPD, Governança Digital (contexto corporativo), Normas e Fiscalização, Redes Sociais (segurança/reputação digital), Transparência (ativa), Auditoria, Controle social (compliance interno), Ouvidoria Interna.
*   **Fraudes e Integridade Corporativa:**
    *   Fraude em auxílio emergencial - coronavírus (se houver tentativa de golpe interno), Corrupção (corporativa, suborno, favorecimento), Denúncia Crime (canal interno de ética e conduta), Denúncia de irregularidades de colaboradores, Descontos associativos indevidos, Lavagem de dinheiro, Sistema Financeiro (fraudes bancárias, compliance financeiro), Licitações, Benefício (fraudes na concessão interna), Cadastro (falsidade ideológica/dados manipulados), Certidões e Declarações (falsificação de documentos), Propriedade Industrial (uso indevido, pirataria, vazamento de segredos), Seguro (fraudes relacionadas a sinistros), Operações (fraudes operacionais internas).
*   **Conduta, Compliance e Recursos Humanos:**
    *   Assédio moral, Assédio sexual, Discriminação, Conduta Ética, Conduta Docente (se aplicável), Racismo, Guia Lilás (boas práticas contra assédio e discriminação), Recursos Humanos, Frequência de Servidores (controle de ponto, produtividade), Relações de Trabalho (compliance trabalhista, relações sindicais).

### 3.3. Hierarquia de Acesso e Perfis de Usuário

O sistema implementará um controle de acesso baseado em perfis hierárquicos, garantindo que cada usuário tenha acesso apenas às informações e funcionalidades pertinentes à sua função:

*   **Super Admin:** Acesso total ao sistema. Pode visualizar e administrar todas as empresas, usuários e denúncias, além de gerenciar configurações globais.
*   **Admin do Cliente:** Administrador da empresa cliente. Pode gerenciar usuários (criar, editar, desativar) e perfis de acesso (Gerente, Auditoria, Cliente) dentro de sua própria empresa. Tem acesso total às denúncias da sua empresa, similar ao perfil de Auditoria.
*   **Auditoria/Compliance:** Acesso total às denúncias dentro de sua empresa. Pode visualizar, encerrar e reclassificar denúncias, além de gerar relatórios específicos da empresa.
*   **Gerente/Responsável:** Visualiza denúncias de clientes sob sua gestão. Pode inserir comentários e solicitar mais informações sobre as denúncias.
*   **Cliente:** Pode registrar novas denúncias (anônimas ou identificadas) e acompanhar o status de suas próprias denúncias.

### 3.4. Funcionalidades Principais

*   **Registro de Denúncias:**
    *   Formulário para registro de novas denúncias, com opção de anonimato ou identificação.
    *   Campos para título, descrição, categoria e anexos (se aplicável).
*   **Acompanhamento de Status:**
    *   Visualização do status da denúncia (recebida, em análise, concluída).
    *   Histórico de interações e comentários.
*   **Gestão de Denúncias (Admin do Cliente, Gerente, Auditoria):**
    *   Visualização filtrada de denúncias por status, categoria, empresa, etc.
    *   Ferramentas para inserir comentários, solicitar informações adicionais, reclassificar e encerrar denúncias.
*   **Gestão de Usuários e Empresas (Super Admin):**
    *   CRUD (Criar, Ler, Atualizar, Deletar) de empresas e usuários.
    *   Associação de usuários a empresas e perfis de acesso.
    *   Customização por Empresa: Capacidade de cada empresa personalizar elementos visuais como logos, cores e outros aspectos da interface para seus usuários.
*   **Gestão de Usuários (Admin do Cliente):**
    *   CRUD de usuários (criar, editar, desativar) e atribuição de perfis (Gerente, Auditoria, Cliente) dentro de sua própria empresa.
*   **Relatórios:**
    *   Geração de relatórios e dashboards para análise de dados das denúncias (por categoria, status, empresa, etc.).
*   **Segurança:**
    *   Autenticação robusta via Firebase Auth.
    *   Criptografia de dados sensíveis.
    *   Regras de segurança no Firestore para controle de acesso granular.
    *   Auditoria de acesso (logs internos de usuário, ação e timestamp).

### 3.5. Modelagem de Dados (Firestore)

O banco de dados Firestore será estruturado com as seguintes coleções principais:

*   **`empresas`:** Armazena informações sobre as empresas (id, nome, cnpj, status, logo_url, cores_personalizadas).
*   **`usuarios`:** Armazena dados dos usuários (id, email, nome, perfil: `super_admin` | `admin_cliente` | `auditoria` | `gerente` | `cliente`, empresa_id).
*   **`denuncias`:** Armazena os detalhes de cada denúncia (id, titulo, descricao, data_criacao, status, anonima, empresa_id, usuario_id, historico de interações).
*   **`configuracoes_globais`:** Armazenará configurações gerais do sistema, como categorias e subitens de denúncias padrão, modelos de e-mail globais, etc.
*   **`configuracoes_empresa`:** Armazenará configurações específicas de cada empresa, como customização visual, destinatários de notificação específicos, etc.

### 3.6. Próximos Passos Detalhados

1.  **Criação de Wireframes:**
    *   Desenho dos layouts básicos para as telas de Login, Dashboards (para cada perfil), Registro de Denúncia, Visualização de Denúncia e Gestão de Usuários/Empresas.
    *   Inclusão de áreas para customização visual nas telas pertinentes.
    *   Criação de telas específicas para o perfil "Admin do Cliente" para gestão de usuários da empresa.
    *   Desenho das telas para o "Menu de Configuração" para Super Admin e Admin do Cliente, detalhando cada item e suas sub-opções.
2.  **Implementação do Layout:**
    *   Desenvolvimento do frontend com React, utilizando `create-react-app` ou Vite para iniciar o projeto.
    *   Configuração do TailwindCSS para estilização responsiva.
    *   Criação de componentes reutilizáveis (botões, formulários, tabelas, cards).
    *   Implementação da navegação e rotas (React Router).
    *   Suporte para aplicação de temas e logos personalizados por empresa, garantindo a renderização dinâmica com base nas configurações da empresa.
3.  **Integração de Autenticação:**
    *   Configuração do Firebase Auth para login e registro de usuários.
    *   Implementação de `custom claims` no Firebase Auth para gerenciar os perfis de acesso (`super_admin`, `admin_cliente`, `auditoria`, `gerente`, `cliente`).
    *   Testes de autenticação e diferenciação de interface por perfil.
4.  **Aplicação de Regras de Acesso no Firestore:**
    *   Modelagem do banco de dados Firestore conforme o escopo (coleções `empresas`, `usuarios`, `denuncias`, `configuracoes_globais`, `configuracoes_empresa`).
    *   Criação e implementação de regras de segurança no Firestore para restringir leitura e escrita de dados conforme o perfil do usuário e a `empresa_id`.
    *   Garantia de segurança para denúncias anônimas e identificadas.
5.  **Validação do Fluxo de Super Admin:**
    *   Implementação das funcionalidades de CRUD para empresas e usuários na interface do Super Admin.
    *   Implementação da gestão das opções de customização visual para cada empresa.
    *   Testes de criação, edição, exclusão e associação correta das relações entre empresas e usuários.
    *   Garantia de que o Super Admin visualize e gerencie todas as entidades do sistema.
6.  **Validação do Fluxo de Admin do Cliente:**
    *   Implementação das funcionalidades de gestão de usuários (criação, edição, desativação, atribuição de perfis) para o perfil `admin_cliente` dentro de sua respectiva empresa.
    *   Testes para garantir que o `admin_cliente` só possa gerenciar usuários e configurações de sua própria empresa.
7.  **Testes de Ponta a Ponta (Usuários Simulados):**
    *   Criação de scripts de teste ou cenários de uso para usuários com diferentes perfis.
    *   Validação do fluxo completo: login, registro de denúncia, acompanhamento, comentários, encerramento, gestão de usuários e configurações.
    *   Verificação da segurança e restrição de acesso em todas as funcionalidades.
8.  **Documentação:**
    *   Elaboração da política de privacidade e termos de uso do sistema, em conformidade com a LGPD e as práticas da empresa.
    *   Criação de documentação técnica para o desenvolvimento e manutenção do sistema.
    *   Desenvolvimento de material de treinamento para os usuários finais (Super Admin, Admin do Cliente, Auditoria, Gerente, Cliente).

### 3.7. Mecanismos de Alerta e Visualização

Para garantir a eficiência no tratamento das denúncias, o sistema implementará os seguintes mecanismos:

*   **Notificações no Próprio Sistema (In-App Notifications):**
    *   Alertas visuais (ícones, contadores, banners) na interface do usuário para Admin do Cliente, Auditoria e Gerente sobre novas denúncias ou atualizações (novos comentários, mudanças de status).
*   **Notificações por E-mail:**
    *   Envio automático de e-mails para os perfis designados (Admin do Cliente, Auditoria, Gerente) ao registrar uma nova denúncia ou em caso de atualizações importantes. Os e-mails conterão um resumo e um link direto para a denúncia no sistema.
*   **Dashboards e Listas de Denúncias:**
    *   Painéis centralizados para cada perfil, exibindo listas de denúncias com indicadores visuais de status.
    *   Funcionalidades robustas de filtro e pesquisa para facilitar a localização e priorização das denúncias.
*   **Tela de Detalhes da Denúncia:**
    *   Visualização completa de cada denúncia, incluindo informações detalhadas, histórico de interações, campo para novos comentários/atualizações e opções de gestão (alterar status, reclassificar, solicitar informações).

### 3.8. Menu de Configuração do Sistema

O menu de configuração será acessível pelos perfis **Super Admin** e **Admin do Cliente**, com funcionalidades específicas para cada um, garantindo a gestão granular do sistema.

**3.8.1. Para o Perfil Super Admin:**

*   **Gestão de Empresas:** Listar/Criar/Editar Empresas, Configurações de Customização por Empresa, Associação de Admin do Cliente.
*   **Gestão de Usuários Globais:** Listar/Criar/Editar Usuários (Todos os Perfis), Atribuição de Perfis.
*   **Configurações de Classificação de Denúncias:** Gerenciar Categorias Principais, Gerenciar Subitens por Categoria, Ordem de Exibição.
*   **Configurações de Notificação:** Modelos de E-mail, Destinatários Padrão, Frequência de Alertas.
*   **Configurações de Segurança:** Políticas de Senha, Configurações de Autenticação, Logs de Auditoria.
*   **Configurações Gerais do Sistema:** Termos de Uso e Política de Privacidade, Manutenção do Sistema.

**3.8.2. Para o Perfil Admin do Cliente:**

*   **Gestão de Usuários da Empresa:** Listar/Criar/Editar Usuários da Empresa, Atribuição de Perfis (dentro da empresa).
*   **Configurações da Empresa:** Dados da Empresa, Customização Visual (upload de logo, definição de cores).
*   **Configurações de Notificação (da Empresa):** Destinatários de Alerta, Regras de Notificação.
*   **Configurações de Classificação de Denúncias (da Empresa):** Gerenciar Subitens por Categoria (ativação/desativação/adição de subitens específicos para a empresa).
*   **Logs de Atividade da Empresa:** Visualizar logs de acesso e ações dos usuários da própria empresa.

---

**Autor:** Manus AI
**Data:** 7 de janeiro de 2025

