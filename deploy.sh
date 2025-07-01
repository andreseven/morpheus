#!/bin/bash

# --- Variáveis de Configuração ---
PROJECT_DIR="/opt/morpheus"
DOMAIN="yourdomain.com" # Substitua pelo seu domínio
EMAIL="your-email@example.com" # Substitua pelo seu email para Certbot
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
sudo tee .env > /dev/null <<EOF
FLASK_ENV=production
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost/$DB_NAME
SECRET_KEY=$(openssl rand -base64 32)
CORS_ORIGINS=https://$DOMAIN
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
log_info "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/morpheus > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        root $PROJECT_DIR/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src \'self\' http: https: data: blob: \'unsafe-inline\'" always;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        add_header Access-Control-Allow-Origin "https://$DOMAIN" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    }
    
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

# --- 7. Configurar SSL com Certbot (Opcional) ---
log_info "Configurando SSL com Certbot..."
sudo apt install -y certbot python3-certbot-nginx || log_error "Falha ao instalar Certbot."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $EMAIL || log_error "Falha ao obter certificado SSL."

log_success "Deploy do Sistema Morpheus concluído com sucesso!"
log_info "Acesse seu sistema em: https://$DOMAIN"


