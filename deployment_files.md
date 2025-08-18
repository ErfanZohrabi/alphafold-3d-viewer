# AlphaFold 3D Protein Viewer - Deployment Files

## 📁 Project Structure
```
alphafold-viewer/
├── app.py                  # Flask backend (main application)
├── templates/
│   └── index.html         # Frontend template
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration (optional)
├── render.yaml           # Render deployment config
├── railway.json          # Railway deployment config
└── README.md             # Documentation
```

## 📦 requirements.txt
```txt
Flask==2.3.3
requests==2.31.0
gunicorn==21.2.0
Werkzeug==2.3.7
```

## 🐳 Dockerfile (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## ☁️ Deployment Options

### 1. Render.com Deployment

Create `render.yaml`:
```yaml
services:
  - type: web
    name: alphafold-viewer
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

**Steps for Render:**
1. Push code to GitHub repository
2. Connect GitHub to Render.com
3. Create new "Web Service"
4. Select your repository
5. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3.11

### 2. Railway Deployment

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Steps for Railway:**
1. Connect GitHub to Railway.app
2. Deploy from GitHub repository
3. Railway automatically detects Python and installs dependencies
4. Set environment variables if needed

### 3. Heroku Deployment

Create `Procfile`:
```
web: gunicorn app:app
```

Create `runtime.txt`:
```
python-3.11.7
```

**Steps for Heroku:**
1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create alphafold-viewer`
4. Deploy: `git push heroku main`

### 4. Vercel Deployment

Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "./app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ]
}
```

## 🔧 Environment Variables

For production deployment, consider these environment variables:

```bash
FLASK_ENV=production
PORT=5000
FLASK_DEBUG=False
```

## 🚀 Local Development

1. **Clone/Create the project:**
```bash
mkdir alphafold-viewer
cd alphafold-viewer
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python app.py
```

5. **Open browser:**
```
http://localhost:5000
```

## 📝 API Endpoints

- `GET /` - Main application page
- `POST /search` - Search for protein structures
  - Request body: `{"query": "P05067"}`
  - Response: Protein structure data with 3D model URL

## 🧪 Test Cases

Try these examples:
- **UniProt IDs**: P05067, P04637, P01308
- **Protein names**: insulin, hemoglobin, amyloid
- **Sequences**: MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG

## 🛠️ Features Added

### Enhanced Backend:
- ✅ Better error handling and logging
- ✅ Input validation for UniProt IDs
- ✅ Protein sequence validation
- ✅ Search by protein name
- ✅ Caching with @lru_cache
- ✅ Additional protein metadata
- ✅ Production-ready configuration

### Enhanced Frontend:
- ✅ Modern, responsive design
- ✅ Loading states and animations
- ✅ Protein information display
- ✅ Interactive examples
- ✅ 3D viewer controls
- ✅ Mobile-friendly interface
- ✅ Error handling with user feedback

## 🔗 Quick Deploy Links

**Render**: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

**Railway**: [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

**Heroku**: [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com)

## 📚 Documentation Links

- [AlphaFold Database API](https://alphafold.ebi.ac.uk/api-docs)
- [UniProt API](https://www.uniprot.org/help/api)
- [Mol* Viewer](https://molstar.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)

Ready to deploy! 🚀