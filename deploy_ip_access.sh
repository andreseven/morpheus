#!/bin/bash

# --- Variáveis de Configuração ---
PROJECT_DIR="/opt/morpheus"
# Para acesso via IP, não precisamos de DOMAIN ou EMAIL para Certbot
# DB_USER, DB_PASS, DB_NAME permanecem os mesmos
DB_USER="morpheus"
DB_PASS="secure_password" # Altere para uma senha forte
DB_NAME="morpheus_db"

# --- Funções Auxiliares ---
log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo "[SUCCESS] $1"
}

log_error() {
    echo "[ERROR] $1"
    exit 1
}

# --- 1. Atualizar Sistema e Instalar Pré-requisitos ---
log_info "Atualizando o sistema e instalando pré-requisitos..."
sudo apt update || log_error "Falha ao atualizar apt."
sudo apt upgrade -y || log_error "Falha ao fazer upgrade do sistema."
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx postgresql postgresql-contrib git || log_error "Falha ao instalar pacotes."

# Instalar pnpm
log_info "Instalando pnpm..."
sudo npm install -g pnpm || log_error "Falha ao instalar pnpm."

# --- 2. Configurar PostgreSQL ---
log_info "Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD 	erase $DB_PASS

# --- 3. Clonar Repositório (Assumindo que o código está em um repositório Git) ---
# log_info "Clonando o repositório do Morpheus..."
# sudo git clone <URL_DO_SEU_REPOSITORIO> $PROJECT_DIR || log_error "Falha ao clonar o repositório."
# sudo chown -R www-data:www-data $PROJECT_DIR || log_error "Falha ao alterar permissões do projeto."

# Se o código já estiver no diretório atual, mova-o para $PROJECT_DIR
log_info "Movendo o código existente para o diretório do projeto..."
sudo mkdir -p $PROJECT_DIR || log_error "Falha ao criar diretório do projeto."
sudo mv /home/ubuntu/morpheus/* $PROJECT_DIR/ || log_error "Falha ao mover arquivos do projeto."
sudo chown -R www-data:www-data $PROJECT_DIR || log_error "Falha ao alterar permissões do projeto."

# --- 4. Deploy do Backend ---
log_info "Iniciando deploy do Backend..."
cd $PROJECT_DIR/backend || log_error "Diretório do backend não encontrado."

log_info "Criando ambiente virtual e instalando dependências Python..."
python3.11 -m venv venv || log_error "Falha ao criar ambiente virtual."
source venv/bin/activate || log_error "Falha ao ativar ambiente virtual."
pip install -r requirements.txt || log_error "Falha ao instalar dependências Python."
pip install gunicorn psycopg2-binary || log_error "Falha ao instalar Gunicorn e Psycopg2."

log_info "Configurando variáveis de ambiente do Backend (.env)..."
# Para acesso via IP, CORS_ORIGINS pode ser '*' ou o IP específico do servidor
sudo tee .env > /dev/null <<EOF
FLASK_ENV=production
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost/$DB_NAME
SECRET_KEY=$(openssl rand -base64 32)
CORS_ORIGINS=*
EOF

log_info "Criando e populando o banco de dados..."
python src/create_db.py || log_error "Falha ao criar o banco de dados."
python src/simple_seed.py || log_error "Falha ao popular o banco de dados."

log_info "Configurando serviço Systemd para o Backend..."
sudo tee /etc/systemd/system/morpheus-backend.service > /dev/null <<EOF
[Unit]
Description=Morpheus Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR/backend
Environment=PATH=$PROJECT_DIR/backend/venv/bin
EnvironmentFile=$PROJECT_DIR/backend/.env
ExecStart=$PROJECT_DIR/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload || log_error "Falha ao recarregar daemon do Systemd."
sudo systemctl enable morpheus-backend || log_error "Falha ao habilitar serviço do backend."
sudo systemctl start morpheus-backend || log_error "Falha ao iniciar serviço do backend."

# --- 5. Deploy do Frontend ---
log_info "Iniciando deploy do Frontend..."
cd $PROJECT_DIR/frontend || log_error "Diretório do frontend não encontrado."

log_info "Instalando dependências Node.js e realizando build..."
pnpm install || log_error "Falha ao instalar dependências Node.js."
pnpm run build || log_error "Falha ao realizar build do frontend."

# --- 6. Configurar Nginx ---
log_info "Configurando Nginx para acesso via IP..."
sudo tee /etc/nginx/sites-available/morpheus > /dev/null <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    
    # Frontend
    location / {
        root $PROJECT_DIR/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        # Content-Security-Policy pode precisar de ajustes dependendo dos recursos externos
        add_header Content-Security-Policy "default-src \'self\' http: https: data: blob: \'unsafe-inline\' \'unsafe-eval\';" always;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS headers para acesso via IP
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    }
    
    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        root $PROJECT_DIR/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/morpheus /etc/nginx/sites-enabled/ || log_error "Falha ao criar link simbólico do Nginx."
sudo nginx -t || log_error "Erro na configuração do Nginx."
sudo systemctl reload nginx || log_error "Falha ao recarregar Nginx."

# --- 7. Certbot (Desabilitado para acesso via IP) ---
log_info "Configuração SSL com Certbot desabilitada para acesso via IP."
log_success "Deploy do Sistema Morpheus concluído com sucesso para acesso via IP!"
log_info "Acesse seu sistema pelo IP do servidor (ex: http://SEU_IP_DO_SERVIDOR)"


