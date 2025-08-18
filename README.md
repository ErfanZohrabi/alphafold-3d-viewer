# 🧬 AlphaFold 3D Protein Viewer

A modern web application for exploring and visualizing protein structures from the AlphaFold database. Built with Flask and featuring an interactive 3D viewer powered by Mol*.

![AlphaFold Viewer](https://img.shields.io/badge/Status-Active-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-blue)
![License](https://img.shields.io/badge/License-MIT-blue)

## 🌟 Features

- **🔍 Multi-Search Options**: Search by UniProt ID, protein name, or amino acid sequence
- **🎨 Interactive 3D Visualization**: Powered by Mol* viewer with full rotation, zoom, and inspection controls
- **📊 Detailed Protein Information**: View organism, gene names, confidence scores, and more
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **⚡ Real-time Data**: Fetches latest structures directly from AlphaFold database
- **🚀 Easy Deployment**: Ready for deployment on Render, Railway, Heroku, or Vercel

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/alphafold-3d-viewer.git
   cd alphafold-3d-viewer
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

## 🧪 Usage Examples

Try these sample searches to get started:

- **UniProt IDs**: `P05067` (Amyloid beta), `P04637` (p53), `P01308` (Insulin)
- **Protein Names**: `insulin`, `hemoglobin`, `amyloid`, `collagen`
- **Sequences**: Enter any valid amino acid sequence (minimum 10 residues)

## 📁 Project Structure

```
alphafold-3d-viewer/
├── app.py                  # Flask backend application
├── templates/
│   └── index.html         # Frontend template with 3D viewer
├── requirements.txt       # Python dependencies
├── deployment_files.md    # Deployment configurations
├── README.md              # This file
└── .gitignore            # Git ignore rules
```

## 🛠️ Technical Features

### Backend (Flask)
- ✅ RESTful API endpoints for protein search
- ✅ Integration with AlphaFold and UniProt databases
- ✅ Input validation and error handling
- ✅ Caching with LRU cache for performance
- ✅ Comprehensive logging
- ✅ Production-ready configuration

### Frontend
- ✅ Modern, responsive UI with CSS Grid/Flexbox
- ✅ Interactive 3D protein visualization
- ✅ Real-time search with loading states
- ✅ Protein metadata display
- ✅ Mobile-optimized design
- ✅ Accessibility features

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`      | Main application page |
| POST   | `/search`| Search for protein structures |

### Search API Example

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "P05067"}'
```

## 🚀 Deployment Options

### 1. Render.com
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

### 2. Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

### 3. Heroku
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com)

See `deployment_files.md` for detailed deployment instructions for each platform.

## ⚙️ Configuration

### Environment Variables

```bash
FLASK_ENV=production      # Set to production for deployment
PORT=5000                # Port number (default: 5000)
FLASK_DEBUG=False        # Disable debug mode in production
```

## 🧬 Supported Input Formats

### UniProt IDs
- Standard format: `P05067`, `Q9Y6C9`
- The application validates UniProt ID format automatically

### Protein Names
- Common names: `insulin`, `hemoglobin`, `collagen`
- Scientific names are also supported

### Amino Acid Sequences
- Minimum length: 10 amino acids
- Valid amino acids: `ACDEFGHIKLMNPQRSTVWY`
- Example: `MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG`

## 🔬 Data Sources

- **[AlphaFold Database](https://alphafold.ebi.ac.uk/)**: Protein structure predictions
- **[UniProt](https://www.uniprot.org/)**: Protein sequence and annotation data
- **[Mol* Viewer](https://molstar.org/)**: 3D molecular visualization

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AlphaFold team** at DeepMind for revolutionizing protein structure prediction
- **Mol* team** for the excellent 3D molecular viewer
- **UniProt** for comprehensive protein databases
- **Flask community** for the amazing web framework

## 📞 Support

If you have any questions or run into issues:

1. Check the [Issues](https://github.com/YOUR_USERNAME/alphafold-3d-viewer/issues) page
2. Create a new issue with detailed information
3. Join the discussion in our community

## 🔗 Links

- [Live Demo](https://your-deployment-url.com)
- [AlphaFold Database](https://alphafold.ebi.ac.uk/)
- [Mol* Documentation](https://molstar.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

Made with ❤️ for the protein research community
