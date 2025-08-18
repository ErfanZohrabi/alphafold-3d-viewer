from flask import Flask, render_template, request, jsonify
import requests
import re
import logging
from functools import lru_cache
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# API endpoints
ALPHAFOLD_API = "https://alphafold.ebi.ac.uk/api/prediction/{}"
UNIPROT_API = "https://rest.uniprot.org/uniprotkb/search"
UNIPROT_ENTRY_API = "https://rest.uniprot.org/uniprotkb/{}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        logger.info(f"Searching for: {query}")
        
        # Check if it's a UniProt ID (pattern: letter(s) followed by digits)
        if is_uniprot_id(query):
            result = fetch_by_uniprot_id(query)
            if result:
                return jsonify(result)
        
        # Check if it's a protein sequence
        if is_protein_sequence(query):
            result = fetch_by_sequence(query.upper())
            if result:
                return jsonify(result)
            else:
                return jsonify({"error": "No matching protein found in UniProt database"}), 404
        
        # Try to search by protein name
        result = fetch_by_protein_name(query)
        if result:
            return jsonify(result)
        
        return jsonify({
            "error": "Invalid input. Please enter:\n- UniProt ID (e.g., P05067)\n- Protein sequence (amino acids)\n- Protein name"
        }), 400
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def is_uniprot_id(query):
    """Check if query matches UniProt ID pattern"""
    pattern = r'^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$'
    return bool(re.match(pattern, query.upper()))

def is_protein_sequence(query):
    """Check if query is a valid protein sequence"""
    valid_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
    return (len(query) >= 10 and 
            all(c.upper() in valid_amino_acids for c in query if c.isalpha()))

@lru_cache(maxsize=100)
def fetch_by_uniprot_id(uniprot_id):
    """Fetch protein structure from AlphaFold using UniProt ID"""
    url = ALPHAFOLD_API.format(uniprot_id.upper())
    
    try:
        response = requests.get(url, timeout=30)
        logger.info(f"AlphaFold API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                entry = data[0]
                
                # Fetch additional protein info from UniProt
                protein_info = fetch_protein_info(uniprot_id)
                
                return {
                    "id": entry["entryId"],
                    "organism": entry.get("organismScientificName", "Unknown"),
                    "model_url": entry["pdbUrl"],
                    "confidence_url": entry.get("paeUrl"),
                    "confidence_score": entry.get("globalMetricValue"),
                    "model_created": entry.get("modelCreatedDate"),
                    "protein_name": protein_info.get("protein_name", "Unknown"),
                    "gene_name": protein_info.get("gene_name", "Unknown"),
                    "length": entry.get("uniprotEnd", 0) - entry.get("uniprotStart", 0) + 1
                }
        elif response.status_code == 404:
            logger.warning(f"No AlphaFold structure found for {uniprot_id}")
            return None
        else:
            logger.error(f"AlphaFold API error: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None

def fetch_protein_info(uniprot_id):
    """Fetch additional protein information from UniProt"""
    try:
        url = UNIPROT_ENTRY_API.format(uniprot_id.upper())
        params = {
            "fields": "protein_name,gene_names"
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "protein_name": data.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "Unknown"),
                "gene_name": data.get("genes", [{}])[0].get("geneName", {}).get("value", "Unknown") if data.get("genes") else "Unknown"
            }
    except Exception as e:
        logger.warning(f"Failed to fetch protein info: {str(e)}")
    
    return {"protein_name": "Unknown", "gene_name": "Unknown"}

def fetch_by_sequence(sequence):
    """Search for protein by amino acid sequence"""
    params = {
        "query": f"sequence:{sequence}",
        "format": "json",
        "fields": "accession,protein_name,organism_name",
        "size": "1"
    }
    
    try:
        response = requests.get(UNIPROT_API, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                uniprot_id = data["results"][0]["primaryAccession"]
                logger.info(f"Found UniProt ID {uniprot_id} for sequence")
                return fetch_by_uniprot_id(uniprot_id)
    except Exception as e:
        logger.error(f"Sequence search error: {str(e)}")
    
    return None

def fetch_by_protein_name(protein_name):
    """Search for protein by name"""
    params = {
        "query": f"protein_name:{protein_name}",
        "format": "json",
        "fields": "accession,protein_name,organism_name",
        "size": "1"
    }
    
    try:
        response = requests.get(UNIPROT_API, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                uniprot_id = data["results"][0]["primaryAccession"]
                logger.info(f"Found UniProt ID {uniprot_id} for protein name")
                return fetch_by_uniprot_id(uniprot_id)
    except Exception as e:
        logger.error(f"Protein name search error: {str(e)}")
    
    return None

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)