# Checklist de Deploy — ENDE Platform

## Pré-requisitos do Servidor

- [ ] Python 3.12 ou superior instalado
- [ ] PostgreSQL 15+ instalado e configurado (opcional; SQLite para teste)
- [ ] Git instalado
- [ ] Acesso SSH ao servidor
- [ ] Nginx ou Apache (para proxy reverso)

## Passos para Produção

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio> ende_platform
cd ende_platform
```

### 2. Configurar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# .\venv\Scripts\Activate.ps1  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

> **Nota**: Se não existir `requirements.txt`, gerar com:
> ```bash
> pip freeze > requirements.txt
> ```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com valores de produção
```

**Configuração obrigatória para produção:**

```env
DEBUG=False
SECRET_KEY=<gerar-nova-chave>
ALLOWED_HOSTS=.seuservidor.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ende_db
DB_USER=ende_user
DB_PASSWORD=<senha-forte>
DB_HOST=localhost
DB_PORT=5432
```

Para gerar uma SECRET_KEY segura:

```python
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 5. Criar base de dados PostgreSQL

```sql
CREATE DATABASE ende_db;
CREATE USER ende_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE ende_db TO ende_user;
ALTER USER ende_user CREATEDB;
```

### 6. Aplicar migrações

```bash
python manage.py migrate
```

### 7. Recolher ficheiros estáticos

```bash
python manage.py collectstatic --noinput
```

### 8. Criar superuser

```bash
python manage.py createsuperuser
```

### 9. Testar o servidor

```bash
python manage.py runserver 0.0.0.0:8000 --insecure
```

Aceder a `http://<ip-do-servidor>:8000/` para verificar.

### 10. Configurar Gunicorn (Linux)

```bash
pip install gunicorn
gunicorn ende_platform.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 11. Configurar Nginx como proxy reverso

```nginx
server {
    listen 80;
    server_name seuservidor.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /home/user/ende_platform/staticfiles;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/user/ende_platform/ende_platform.sock;
    }
}
```

### 12. Configurar systemd (Linux)

Criar `/etc/systemd/system/ende_platform.service`:

```ini
[Unit]
Description=ENDE Platform Gunicorn Daemon
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/home/user/ende_platform
ExecStart=/home/user/ende_platform/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/user/ende_platform/ende_platform.sock \
    ende_platform.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start ende_platform
sudo systemctl enable ende_platform
```

## Verificações Finais

- [ ] `DEBUG=False` no .env
- [ ] `SECRET_KEY` alterada para produção
- [ ] `ALLOWED_HOSTS` configurado
- [ ] Base de dados PostgreSQL criada e migrada
- [ ] Ficheiros estáticos recolhidos (`collectstatic`)
- [ ] Firewall permite porta 80/443
- [ ] HTTPS configurado (Certbot/Let's Encrypt)
- [ ] Backup automático configurado

## Manutenção

### Atualizar código

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart ende_platform
```

### Backup do banco de dados

```bash
pg_dump ende_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Verificar logs

```bash
sudo journalctl -u ende_platform -f
```
