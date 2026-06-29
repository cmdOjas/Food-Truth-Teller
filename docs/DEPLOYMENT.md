# Deployment Guide

## Production Checklist

- [ ] Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Set `OPENAI_API_KEY`
- [ ] Configure `DATABASE_URL` pointing to production PostgreSQL
- [ ] Configure `REDIS_URL` pointing to production Redis
- [ ] Set `FLASK_ENV=production`
- [ ] Train the ML model and copy `health_model.pkl` to `ML_MODEL_PATH`
- [ ] Set up HTTPS (nginx / Caddy reverse proxy)
- [ ] Configure firewall to only expose ports 80/443

## Docker Production Deploy

```bash
# 1. Build images
docker compose -f docker-compose.yml build

# 2. Train ML model (one-time)
docker compose --profile ml run --rm ml

# 3. Start services
docker compose up -d

# 4. Initialize DB (first deploy only)
docker compose exec backend flask --app run.py create-db
```

## Heroku / Render / Railway

1. Set all environment variables in the dashboard.
2. `Procfile` (create in project root):
   ```
   web: cd backend && gunicorn --bind 0.0.0.0:$PORT run:app
   ```
3. Add PostgreSQL and Redis add-ons.

## Nginx Reverse Proxy (example)

```nginx
server {
    listen 443 ssl;
    server_name api.yourapp.com;

    ssl_certificate /etc/letsencrypt/live/yourapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourapp.com/privkey.pem;

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;           # Required for streaming chat responses
        proxy_read_timeout 120s;
    }
}
```

## Database Migrations

```bash
flask --app run.py db init        # first time
flask --app run.py db migrate -m "migration name"
flask --app run.py db upgrade
```

## Scaling

- Backend: increase gunicorn `--workers` (rule: 2 × CPU + 1)
- Use Redis for session/rate-limit state (already configured)
- Use read replicas for analytics queries
- ML model is stateless — mount the pkl file as a read-only volume
