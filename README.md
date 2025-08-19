# 🧬 Enhanced AlphaFold & PDB 3D Protein Viewer

A comprehensive web application for exploring and visualizing protein structures from both AlphaFold database and Protein Data Bank (PDB). Built with Flask and featuring an advanced 3D viewer powered by Mol* with extensive customization options.

![AlphaFold Viewer](https://img.shields.io/badge/Status-Enhanced-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-blue)
![Mol*](https://img.shields.io/badge/Mol*-3.0-purple)
![License](https://img.shields.io/badge/License-MIT-blue)

## 🌟 Enhanced Features

### � **Dual Database Support**
- **AlphaFold Database**: AI-predicted protein structures with confidence scores
- **Protein Data Bank**: Experimental structures from X-ray, NMR, and cryo-EM
- **Smart Detection**: Automatically identifies UniProt IDs, PDB IDs, and protein names
- **Source Comparison**: View structures from multiple sources side-by-side

### 🎨 **Advanced 3D Visualization**
- **Multiple Representations**: Cartoon, Surface, Ball & Stick, Spacefill, Ribbon
- **Color Schemes**: By Chain, Confidence, Secondary Structure, Element, Residue
- **Interactive Controls**: Full rotation, zoom, and inspection capabilities
- **High-Quality Rendering**: Powered by Mol* with WebGL acceleration

### 📊 **Comprehensive Protein Information**
- **Detailed Metadata**: Protein name, gene, organism, molecular weight
- **Structural Info**: Resolution, experimental method, deposition date
- **Functional Data**: EC numbers, GO terms, protein function descriptions
- **Sequence Information**: Length, mass, and sequence-related properties

### � **Export Capabilities**
- **Structure Download**: PDB format export with original data
- **Image Export**: High-resolution screenshots (framework ready)
- **Multiple Formats**: Support for PDB and mmCIF formats
- **Batch Processing**: Ready for multiple structure exports

### 🎛️ **Professional Interface**
- **Modern Design**: Clean, responsive interface with dark mode support
- **Sidebar Controls**: Organized visualization and export controls
- **Source Tabs**: Easy switching between structure sources
- **Mobile Responsive**: Optimized for desktop and mobile devices

### 🔍 **Enhanced Search**
- **Multi-Query Support**: UniProt ID, PDB ID, or protein name
- **Smart Suggestions**: Error messages with helpful suggestions
- **Example Gallery**: 8 diverse example proteins with descriptions
- **Real-time Validation**: Input validation with immediate feedback

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Modern web browser with WebGL support

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ErfanZohrabi/alphafold-3d-viewer.git
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

5. **Open in browser**
   Navigate to `http://localhost:5000` or the displayed URL

## 🎯 Usage Examples

### Search Options

#### **UniProt ID Search**
```
P05067  # Amyloid-β precursor protein
TP53    # Tumor protein p53
```

#### **PDB ID Search**
```
2HHB    # Hemoglobin (classic example)
1A2B    # Various protein structures
```

#### **Protein Name Search**
```
insulin      # Insulin hormone
hemoglobin   # Oxygen transport protein
lysozyme     # Antimicrobial enzyme
```

### Visualization Controls

1. **Representation**: Choose how the protein is displayed
   - **Cartoon**: Shows secondary structure (default)
   - **Surface**: Molecular surface representation
   - **Ball & Stick**: Atomic detail view
   - **Spacefill**: Van der Waals spheres

2. **Color Schemes**: Different coloring methods
   - **By Chain**: Different colors for each protein chain
   - **By Confidence**: AlphaFold confidence scores (blue=high, red=low)
   - **Secondary Structure**: Alpha helices, beta sheets, loops
   - **By Element**: Atomic elements (carbon, oxygen, nitrogen, etc.)

## 🏗️ Architecture

### Backend (Flask)
```
app.py
├── Search endpoints (/search)
├── Metadata API (/api/metadata)
├── Export functionality (/api/export)
├── Structure proxy (/proxy)
└── Health check (/api/health)
```

### Frontend (Mol* + Vanilla JS)
```
templates/index.html
├── Modern responsive UI
├── Mol* 3D viewer integration
├── Search and visualization controls
├── Protein information display
└── Export functionality
```

### Data Sources
- **AlphaFold Database**: AI-predicted structures
- **Protein Data Bank**: Experimental structures  
- **UniProt API**: Protein metadata and annotations

## 🧪 Testing

Run the enhanced test suite:
```bash
python test_enhanced.py
```

Run specific tests:
```bash
# Test basic functions
python -c "from test_enhanced import test_basic_functions; test_basic_functions()"

# Test Flask endpoints
python -c "from test_enhanced import test_flask_app; test_flask_app()"
```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

## 🧪 Usage Examples

Try these sample searches to get started:

- **UniProt IDs**: `P05067` (Amyloid beta), `P04637` (p53), `P01308` (Insulin), `P38398` (BRCA1), `P00533` (EGFR), `P13569` (CFTR), `P12883` (Myosin-7)
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
| GET    | `/api/structure/<UniProt_ID>` | Fetch structure metadata by UniProt ID |

All API endpoints support cross-origin requests for easy integration.

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
