# 🚀 Instruções de Deploy - Sistema Morpheus

## 📋 Pré-requisitos para Produção

### Servidor
- **OS**: Ubuntu 20.04+ ou CentOS 8+
- **RAM**: Mínimo 2GB, recomendado 4GB+
- **CPU**: 2 cores mínimo
- **Storage**: 20GB+ SSD
- **Rede**: Conexão estável com IP público

### Software
- **Python**: 3.11+
- **Node.js**: 20+
- **Nginx**: Para proxy reverso
- **PostgreSQL**: 13+ (recomendado para produção)
- **SSL Certificate**: Let's Encrypt ou similar

## 🔧 Configuração do Servidor

### 1. Atualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx postgresql postgresql-contrib
```

### 2. Configurar PostgreSQL
```bash
sudo -u postgres createuser --interactive morpheus
sudo -u postgres createdb morpheus_db -O morpheus
sudo -u postgres psql -c "ALTER USER morpheus PASSWORD 'secure_password';"
```

### 3. Configurar Firewall
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 📦 Deploy do Backend

### 1. Preparar Aplicação
```bash
cd /opt
sudo git clone <repository-url> morpheus
sudo chown -R www-data:www-data morpheus
cd morpheus/backend

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 2. Configurar Variáveis de Ambiente
```bash
sudo nano /opt/morpheus/backend/.env
```

```env
FLASK_ENV=production
DATABASE_URL=postgresql://morpheus:secure_password@localhost/morpheus_db
SECRET_KEY=your-super-secret-key-here
CORS_ORIGINS=https://yourdomain.com
```

### 3. Configurar Banco de Dados
```bash
# Atualizar src/main.py para usar PostgreSQL
# Executar migrações
source venv/bin/activate
python src/create_db.py
python src/simple_seed.py
```

### 4. Criar Serviço Systemd
```bash
sudo nano /etc/systemd/system/morpheus-backend.service
```

```ini
[Unit]
Description=Morpheus Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/morpheus/backend
Environment=PATH=/opt/morpheus/backend/venv/bin
EnvironmentFile=/opt/morpheus/backend/.env
ExecStart=/opt/morpheus/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable morpheus-backend
sudo systemctl start morpheus-backend
```

## 🌐 Deploy do Frontend

### 1. Build da Aplicação
```bash
cd /opt/morpheus/frontend
npm install -g pnpm
pnpm install
pnpm run build
```

### 2. Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/morpheus
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Frontend
    location / {
        root /opt/morpheus/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "https://yourdomain.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    }
    
    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        root /opt/morpheus/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/morpheus /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 Configurar SSL

### 1. Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. Obter Certificado
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Configurar Renovação Automática
```bash
sudo crontab -e
# Adicionar linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoramento

### 1. Logs do Sistema
```bash
# Backend logs
sudo journalctl -u morpheus-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Monitoramento de Performance
```bash
# Instalar htop para monitoramento
sudo apt install htop

# Verificar status dos serviços
sudo systemctl status morpheus-backend
sudo systemctl status nginx
sudo systemctl status postgresql
```

## 🔄 Backup e Recuperação

### 1. Backup do Banco de Dados
```bash
# Criar script de backup
sudo nano /opt/morpheus/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/morpheus/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup do banco
pg_dump -U morpheus -h localhost morpheus_db > $BACKUP_DIR/morpheus_db_$DATE.sql

# Manter apenas últimos 7 backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup concluído: morpheus_db_$DATE.sql"
```

```bash
chmod +x /opt/morpheus/backup.sh

# Agendar backup diário
sudo crontab -e
# Adicionar linha:
0 2 * * * /opt/morpheus/backup.sh
```

### 2. Restauração
```bash
# Restaurar backup
psql -U morpheus -h localhost morpheus_db < /opt/morpheus/backups/morpheus_db_YYYYMMDD_HHMMSS.sql
```

## 🚨 Troubleshooting

### Problemas Comuns

#### Backend não inicia
```bash
# Verificar logs
sudo journalctl -u morpheus-backend -n 50

# Verificar permissões
sudo chown -R www-data:www-data /opt/morpheus

# Verificar dependências
cd /opt/morpheus/backend
source venv/bin/activate
pip install -r requirements.txt
```

#### Frontend não carrega
```bash
# Verificar build
cd /opt/morpheus/frontend
pnpm run build

# Verificar nginx
sudo nginx -t
sudo systemctl reload nginx
```

#### Banco de dados inacessível
```bash
# Verificar status PostgreSQL
sudo systemctl status postgresql

# Verificar conexão
psql -U morpheus -h localhost morpheus_db
```

## 📈 Otimizações de Performance

### 1. Configurar Cache Redis (Opcional)
```bash
sudo apt install redis-server
pip install redis flask-caching
```

### 2. Configurar CDN (Recomendado)
- Use CloudFlare ou AWS CloudFront
- Configure cache para assets estáticos
- Ative compressão gzip

### 3. Otimizar PostgreSQL
```bash
sudo nano /etc/postgresql/13/main/postgresql.conf
```

```conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

## ✅ Checklist de Deploy

- [ ] Servidor configurado e atualizado
- [ ] PostgreSQL instalado e configurado
- [ ] Backend deployado e funcionando
- [ ] Frontend buildado e servido pelo Nginx
- [ ] SSL configurado e funcionando
- [ ] Firewall configurado
- [ ] Backups automatizados
- [ ] Monitoramento ativo
- [ ] DNS apontando para o servidor
- [ ] Testes de funcionalidade realizados

## 📞 Suporte Pós-Deploy

Para suporte após o deploy:
- 📧 Email: devops@morpheus.com
- 📱 WhatsApp: (11) 99999-9999
- 🎫 Sistema de tickets: https://support.morpheus.com

---

**Deploy realizado com sucesso! 🎉**

