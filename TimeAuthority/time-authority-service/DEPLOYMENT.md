# Deployment Guide - Time Authority x402 Service

This guide covers deploying your timestamping service to various cloud platforms.

## 🌐 Platform Comparison

| Platform | Difficulty | Free Tier | Best For |
|----------|-----------|-----------|----------|
| Railway.app | ⭐ Easy | 500 hours/month | Quick deployment, no config |
| Render.com | ⭐⭐ Easy | 750 hours/month | Web services, automatic HTTPS |
| Fly.io | ⭐⭐⭐ Medium | 3 VMs free | Global edge deployment |
| Google Cloud Run | ⭐⭐⭐ Medium | 2M requests/month | Serverless, auto-scaling |
| Digital Ocean | ⭐⭐⭐⭐ Advanced | $200 credit | Full VPS control |

---

## 🚂 Railway.app (Recommended - Easiest)

### Why Railway?
- Zero configuration needed
- Automatic HTTPS
- Built-in environment variables
- GitHub integration
- $5 free credit monthly

### Steps:

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login**
```bash
railway login
```

3. **Initialize project**
```bash
cd /path/to/your/service
railway init
```

4. **Set environment variable**
```bash
railway variables set RECIPIENT_ADDRESS=your_coinbase_wallet_address
```

5. **Deploy**
```bash
railway up
```

6. **Get your URL**
```bash
railway domain
```

Your service will be live at: `https://your-service.railway.app`

---

## 🎨 Render.com

### Why Render?
- Free HTTPS and custom domains
- Auto-deploy from GitHub
- Good for web services
- 750 free hours/month

### Steps:

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/time-authority.git
git push -u origin main
```

2. **Create new Web Service on Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repo

3. **Configure Service**
   - **Name**: time-authority
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python timestamp_service.py`

4. **Add Environment Variable**
   - Go to "Environment" tab
   - Add: `RECIPIENT_ADDRESS` = `your_coinbase_wallet_address`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)

Your service will be at: `https://time-authority.onrender.com`

---

## ✈️ Fly.io

### Why Fly.io?
- Deploy to edge locations worldwide
- Good free tier
- Fast global performance
- Persistent volumes available

### Steps:

1. **Install Fly CLI**
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Login**
```bash
fly auth login
```

3. **Create Dockerfile** (in your project directory)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "timestamp_service.py"]
```

4. **Create fly.toml**
```toml
app = "time-authority"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

5. **Launch app**
```bash
fly launch
```

6. **Set environment variable**
```bash
fly secrets set RECIPIENT_ADDRESS=your_coinbase_wallet_address
```

7. **Deploy**
```bash
fly deploy
```

Your service will be at: `https://time-authority.fly.dev`

---

## ☁️ Google Cloud Run

### Why Cloud Run?
- Serverless - only pay for requests
- Auto-scales to zero
- 2 million requests/month free
- Fast cold starts

### Steps:

1. **Install Google Cloud SDK**
```bash
# Mac
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
```

2. **Login and set project**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD exec python timestamp_service.py
```

4. **Build and push to Container Registry**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/time-authority
```

5. **Deploy to Cloud Run**
```bash
gcloud run deploy time-authority \
  --image gcr.io/YOUR_PROJECT_ID/time-authority \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars RECIPIENT_ADDRESS=your_coinbase_wallet_address
```

Your service will be at: `https://time-authority-xxxxx-uc.a.run.app`

---

## 🐳 Docker Deployment (Any Platform)

### Build Image

```bash
docker build -t time-authority .
```

### Run Locally
```bash
docker run -p 8000:8000 \
  -e RECIPIENT_ADDRESS=your_wallet \
  time-authority
```

### Push to Docker Hub
```bash
docker tag time-authority yourusername/time-authority
docker push yourusername/time-authority
```

### Deploy on any Docker host
```bash
docker pull yourusername/time-authority
docker run -d -p 80:8000 \
  -e RECIPIENT_ADDRESS=your_wallet \
  --name time-authority \
  yourusername/time-authority
```

---

## 🔐 Environment Variables

Set these on your platform:

```bash
RECIPIENT_ADDRESS=0xYourCoinbaseWalletAddress
COINBASE_API_KEY=your_api_key  # Optional, for payment verification
PORT=8000  # Or platform's required port
```

---

## 📊 Monitoring

### View Logs

**Railway:**
```bash
railway logs
```

**Render:**
- View in dashboard → "Logs" tab

**Fly.io:**
```bash
fly logs
```

**Cloud Run:**
```bash
gcloud run services logs read time-authority
```

### Check Service Health

```bash
curl https://your-service-url.com/
curl https://your-service-url.com/stats
```

---

## 🔄 Continuous Deployment

### GitHub Actions (for any platform)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Time Authority

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Railway
      run: |
        npm install -g @railway/cli
        railway link ${{ secrets.RAILWAY_PROJECT_ID }}
        railway up
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

Add secrets in GitHub repo settings:
- `RAILWAY_TOKEN`
- `RAILWAY_PROJECT_ID`

---

## 💰 Cost Estimates

### Light Usage (1,000 timestamps/month)
- **Railway**: Free ($5 credit covers it)
- **Render**: Free (750 hours)
- **Fly.io**: Free (within limits)
- **Cloud Run**: Free (2M requests free)

### Medium Usage (50,000 timestamps/month)
- **Railway**: ~$3-5/month
- **Render**: ~$7/month
- **Fly.io**: ~$3-5/month
- **Cloud Run**: ~$2-3/month

### High Usage (500,000 timestamps/month)
- **Railway**: ~$15-20/month
- **Render**: ~$25/month
- **Fly.io**: ~$10-15/month
- **Cloud Run**: ~$10-12/month

---

## 🚨 Production Checklist

Before going live:

- [ ] Replace `RECIPIENT_ADDRESS` with your real wallet
- [ ] Set up payment verification (Coinbase API)
- [ ] Enable HTTPS (most platforms do this automatically)
- [ ] Set up monitoring/alerts
- [ ] Back up transaction logs regularly
- [ ] Test with small payments first
- [ ] Add rate limiting (optional)
- [ ] Set up custom domain (optional)
- [ ] Configure CORS for your agents
- [ ] Document your API for agent developers

---

## 📞 Support

**Platform Issues:**
- Railway: https://discord.gg/railway
- Render: https://render.com/docs
- Fly.io: https://community.fly.io
- Cloud Run: https://cloud.google.com/run/docs

**x402 Protocol:**
- Coinbase Developer Discord: https://discord.gg/coinbase

**Payment Issues:**
- Coinbase Support: https://help.coinbase.com

---

## 🎉 You're Ready!

Choose your platform and deploy. Within 10 minutes, your timestamping service will be live and ready to serve AI agents worldwide!
