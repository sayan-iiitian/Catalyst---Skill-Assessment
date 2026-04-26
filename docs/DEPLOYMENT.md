# Deployment Guide

## Overview

Catalyst can be deployed in multiple ways:
1. **Local Development** - For development and testing
2. **Streamlit Cloud** - Quick cloud deployment
3. **Docker** - Containerized deployment
4. **Self-Hosted VPS** - Full control

## Option 1: Local Development

### Requirements
- Python 3.10+
- Git

### Setup Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/catalyst-skill-assessment.git
cd catalyst-skill-assessment

# 2. Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (optional - uses mock by default)
cp .env.example .env
# Edit .env if using HuggingFace or Ollama

# 5. Run application
streamlit run app.py
```

**Access:** http://localhost:8501

---

## Option 2: Streamlit Cloud (Recommended for Hackathon)

### Prerequisites
- GitHub account with repo push access
- Streamlit account (free)

### Deployment Steps

**Step 1: Push to GitHub**
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Catalyst skill assessment platform"
git branch -M main
git remote add origin https://github.com/yourusername/catalyst-skill-assessment.git
git push -u origin main
```

**Step 2: Deploy to Streamlit Cloud**
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository
4. Choose branch: `main`
5. Set main file path: `app.py`
6. Click "Deploy"

**Step 3: Configure Secrets (if using HuggingFace API)**
1. In Streamlit Cloud dashboard, go to app settings
2. Click "Secrets"
3. Add your environment variables:
```
HF_API_TOKEN = "your_token_here"
LLM_API_PROVIDER = "huggingface"
```

**Step 4: Share URL**
- Your app will be live at: `https://[username]-catalyst-skill-assessment.streamlit.app`

### Free Tier Limitations
- Limited compute resources
- May take 30-60 seconds for first LLM call
- Suitable for demo (accepts slower response times)

---

## Option 3: Docker Deployment

### Prerequisites
- Docker installed
- Docker Hub account (optional, for image registry)

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run Locally

```bash
# Build image
docker build -t catalyst:latest .

# Run container
docker run -p 8501:8501 \
  -e HF_API_TOKEN=your_token \
  -e LLM_API_PROVIDER=huggingface \
  catalyst:latest
```

**Access:** http://localhost:8501

### Deploy to Docker Hub

```bash
# Login
docker login

# Tag image
docker tag catalyst:latest yourusername/catalyst:latest

# Push
docker push yourusername/catalyst:latest
```

### Deploy to Cloud (AWS ECS, Google Cloud Run, etc.)

**AWS ECS Example:**
```bash
# Tag for ECR
docker tag catalyst:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/catalyst:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/catalyst:latest

# Create ECS task definition and service
# (See AWS ECS documentation)
```

---

## Option 4: Self-Hosted VPS (DigitalOcean, Linode, AWS EC2)

### Prerequisites
- Linux VPS (Ubuntu 20.04+)
- SSH access
- Domain name (optional)

### Setup Steps

**1. Connect to VPS**
```bash
ssh root@your_ip_address
```

**2. Update System**
```bash
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx
```

**3. Clone Repository**
```bash
cd /opt
git clone https://github.com/yourusername/catalyst-skill-assessment.git
cd catalyst-skill-assessment
```

**4. Create Virtual Environment**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**5. Set Environment Variables**
```bash
cat > .env << EOF
HF_API_TOKEN=your_token_here
LLM_API_PROVIDER=huggingface
DEBUG=False
EOF
chmod 600 .env
```

**6. Create Systemd Service**
```bash
cat > /etc/systemd/system/catalyst.service << EOF
[Unit]
Description=Catalyst Streamlit App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/catalyst-skill-assessment
Environment="PATH=/opt/catalyst-skill-assessment/venv/bin"
ExecStart=/opt/catalyst-skill-assessment/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable catalyst
systemctl start catalyst
```

**7. Configure Nginx Reverse Proxy**
```bash
cat > /etc/nginx/sites-available/catalyst << 'EOF'
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -s /etc/nginx/sites-available/catalyst /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

**8. Enable HTTPS (Let's Encrypt)**
```bash
certbot --nginx -d your_domain.com
```

**Access:** https://your_domain.com

### Monitoring

```bash
# Check service status
systemctl status catalyst

# View logs
journalctl -u catalyst -f

# Monitor resources
htop
```

---

## Option 5: Using Ollama (Local LLM)

If you want to avoid API costs and use a local LLM:

### Install Ollama
1. Download from https://ollama.ai
2. Install and run: `ollama serve`
3. Pull a model: `ollama pull mistral` (or `ollama pull llama2`)

### Configure Catalyst
```bash
# .env
LLM_API_PROVIDER=ollama
```

### Run Together
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Catalyst
source venv/bin/activate
streamlit run app.py
```

**Note:** First request will be slower as model loads into memory.

---

## Performance Optimization

### For Production

1. **Caching**
   - Cache LLM responses for common skills
   - Use Redis for distributed caching

2. **Database**
   - Store assessment results
   - Cache learning resources

3. **Load Balancing**
   - Multiple Streamlit workers behind load balancer
   - Use Gunicorn + Streamlit server

4. **Monitoring**
   - Set up error tracking (Sentry)
   - Monitor response times (New Relic, Datadog)

### Example: Gunicorn + Streamlit
```bash
pip install gunicorn
gunicorn --workers 4 --threads 2 --timeout 60 --access-logfile - --error-logfile - --bind 0.0.0.0:8501 "streamlit.web.cli:_main_run_app(sys.argv, app)"
```

---

## Troubleshooting

### Issue: "Module not found" error
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: HuggingFace API rate limit
```bash
# Use mock provider for testing
LLM_API_PROVIDER=mock
```

### Issue: Slow response times
```bash
# Use Ollama for instant local responses
# Download and run Ollama first
LLM_API_PROVIDER=ollama
```

### Issue: High memory usage
```bash
# Reduce model size in config.py
# Use smaller models like TinyLLaMA
```

---

## Security Best Practices

1. **API Tokens**
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
   - Rotate tokens regularly

2. **Network**
   - Use HTTPS (Let's Encrypt)
   - Enable firewall rules
   - Restrict to IP whitelist if needed

3. **Data**
   - No personal data stored
   - Stateless application (can be scaled)
   - Clear browser cache for sensitive inputs

4. **Updates**
   - Keep Python and dependencies updated
   - Monitor security advisories

---

## Scaling Considerations

For high-traffic deployments:

1. **Horizontal Scaling**
   - Run multiple Streamlit instances
   - Use load balancer (Nginx, HAProxy)
   - Shared cache layer (Redis)

2. **Async Processing**
   - Use Celery for background LLM calls
   - WebSocket for real-time updates

3. **Database**
   - PostgreSQL for result storage
   - ElasticSearch for full-text search

4. **CDN**
   - Cloudflare for static assets
   - Optimize bundle size

---

## Submission Checklist

- [ ] Code pushed to public GitHub repo
- [ ] README.md with setup instructions
- [ ] `.env.example` file present
- [ ] Application runs locally without errors
- [ ] Demo video (3-5 minutes) uploaded
- [ ] Architecture diagram documented
- [ ] Sample inputs/outputs included
- [ ] Deployment URL (if deployed) working
- [ ] Repository access shared with `hackathon@deccan.ai`

---

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: Check docs/ folder
- Email: support@deccanexperts.ai
- Discord: https://discord.gg/aczDnqNR
