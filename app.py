"""Flask backend for the Enhanced AlphaFold & PDB 3D viewer.

This enhanced version supports both AlphaFold and PDB databases, provides
detailed protein metadata, export functionality, and improved error handling.
Features include dual database search, visualization controls, and comprehensive
protein information display.
"""

import json
import logging
import os
import re
import urllib.parse
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import requests
from flask import Flask, Response, abort, jsonify, render_template, request, send_file
from flask_cors import CORS
from datetime import datetime
import tempfile
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_PORT = int(os.environ.get("PORT", "5000"))
ALLOWED_PROXY_HOSTS = {"alphafold.ebi.ac.uk", "files.rcsb.org", "www.rcsb.org"}

app = Flask(__name__)
CORS(app)


# UniProt accession format. See https://www.uniprot.org/help/accession_numbers
UNIPROT_RE = re.compile(
    r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})$",
    re.IGNORECASE,
)

# Letters allowed for simple amino-acid sequence detection.
VALID_AA_LETTERS = set("ACDEFGHIKLMNPQRSTVWY")


def is_uniprot_id(q: str) -> bool:
    """Return True if *q* matches the UniProt accession pattern."""

    return bool(UNIPROT_RE.match(q.strip()))


def is_amino_acid_sequence(q: str) -> bool:
    """Return True if *q* looks like a primary amino-acid sequence.

    The heuristic requires at least 10 canonical residues. Ambiguous
    letters like B/Z/X are intentionally disallowed.
    """

    s = q.strip().upper()
    return len(s) >= 10 and all(c in VALID_AA_LETTERS for c in s)


def is_pdb_id(q: str) -> bool:
    """Return True if *q* matches the PDB ID pattern (4 characters)."""
    return bool(re.match(r'^[0-9][A-Za-z0-9]{3}$', q.strip()))


def build_afdb_pdb_url(accession: str) -> str:
    """Construct the AlphaFold DB PDB URL for *accession*.

    AlphaFold DB version 4 models follow the pattern
    ``https://alphafold.ebi.ac.uk/files/AF-<ACC>-F1-model_v4.pdb``.
    """

    acc = accession.strip().upper()
    return f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v4.pdb"


def build_pdb_url(pdb_id: str) -> str:
    """Construct the PDB file URL for a given PDB ID."""
    pdb = pdb_id.strip().upper()
    return f"https://files.rcsb.org/download/{pdb}.pdb"


@lru_cache(maxsize=256)
def get_protein_metadata(accession: str) -> Optional[Dict]:
    """Get detailed protein metadata from UniProt API."""
    try:
        url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant information
            metadata = {
                "accession": accession,
                "protein_name": "",
                "gene_name": "",
                "organism": "",
                "length": 0,
                "mass": 0,
                "function": "",
                "keywords": [],
                "ec_number": "",
                "go_terms": []
            }
            
            # Extract protein names
            if "proteinDescription" in data:
                desc = data["proteinDescription"]
                if "recommendedName" in desc and "fullName" in desc["recommendedName"]:
                    metadata["protein_name"] = desc["recommendedName"]["fullName"]["value"]
                elif "submissionNames" in desc and desc["submissionNames"]:
                    metadata["protein_name"] = desc["submissionNames"][0]["fullName"]["value"]
            
            # Extract gene name
            if "genes" in data and data["genes"]:
                if "geneName" in data["genes"][0]:
                    metadata["gene_name"] = data["genes"][0]["geneName"]["value"]
            
            # Extract organism
            if "organism" in data:
                metadata["organism"] = data["organism"]["scientificName"]
            
            # Extract sequence info
            if "sequence" in data:
                metadata["length"] = data["sequence"]["length"]
                metadata["mass"] = data["sequence"]["molWeight"]
            
            # Extract function/comments
            if "comments" in data:
                for comment in data["comments"]:
                    if comment["commentType"] == "FUNCTION" and "texts" in comment:
                        metadata["function"] = comment["texts"][0]["value"]
                        break
            
            # Extract keywords
            if "keywords" in data:
                metadata["keywords"] = [kw["name"] for kw in data["keywords"]]
            
            # Extract EC number
            if "proteinDescription" in data and "recommendedName" in data["proteinDescription"]:
                rec_name = data["proteinDescription"]["recommendedName"]
                if "ecNumbers" in rec_name:
                    metadata["ec_number"] = rec_name["ecNumbers"][0]["value"]
            
            return metadata
            
    except Exception as exc:
        logger.warning("Failed to get metadata for %s: %s", accession, exc)
    
    return None


@lru_cache(maxsize=256)
def get_pdb_metadata(pdb_id: str) -> Optional[Dict]:
    """Get metadata for a PDB structure."""
    try:
        url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.upper()}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            metadata = {
                "pdb_id": pdb_id.upper(),
                "title": data.get("struct", {}).get("title", ""),
                "resolution": data.get("rcsb_entry_info", {}).get("resolution_combined", []),
                "method": data.get("exptl", [{}])[0].get("method", "") if data.get("exptl") else "",
                "deposition_date": data.get("rcsb_accession_info", {}).get("deposit_date", ""),
                "organism": "",
                "chains": data.get("rcsb_entry_info", {}).get("polymer_entity_count_protein", 0)
            }
            
            # Get organism info
            if "rcsb_entity_source_organism" in data:
                organisms = data["rcsb_entity_source_organism"]
                if organisms:
                    metadata["organism"] = organisms[0].get("scientific_name", "")
            
            return metadata
            
    except Exception as exc:
        logger.warning("Failed to get PDB metadata for %s: %s", pdb_id, exc)
    
    return None


@lru_cache(maxsize=256)
def uniprot_lookup_by_name(name: str) -> Optional[str]:
    """Resolve a protein *name* to a UniProt accession using UniProt's REST API.

    Returns ``None`` on failure.
    """

    params = {
        "query": name,
        "format": "tsv",
        "fields": "accession,protein_name,organism_name",
        "size": 1,
    }
    try:
        r = requests.get(
            "https://rest.uniprot.org/uniprotkb/search",
            params=params,
            timeout=10,
        )
        r.raise_for_status()
    except Exception as exc:  # pragma: no cover - network failures
        logger.warning("UniProt lookup failed for '%s': %s", name, exc)
        return None

    lines = r.text.strip().splitlines()
    if len(lines) < 2:
        return None
    header = lines[0].split("\t")
    try:
        acc_idx = header.index("Entry")
    except ValueError:
        logger.warning("UniProt response missing 'Entry' column: %s", header)
        return None
    first = lines[1].split("\t")
    return first[acc_idx]


@app.get("/")
def index() -> str:
    """Render the main page."""

    return render_template("index.html")


@app.get("/api/health")
def health() -> Response:
    """Simple health check endpoint."""

    return jsonify({"status": "ok"})


@app.post("/search")
def search() -> Response:
    """Enhanced search supporting both AlphaFold and PDB databases.

    Request body: ``{"query": "<UniProt ID, PDB ID, or protein name>"}``

    Returns detailed information about the protein including metadata and
    available structure sources (AlphaFold and/or PDB).
    """

    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    if is_amino_acid_sequence(query):
        return (
            jsonify({
                "error": "Searching by amino acid sequence is not yet supported.",
                "suggestion": "Try using a UniProt ID (e.g., P05067) or protein name (e.g., insulin)"
            }),
            400,
        )

    result = {
        "query": query,
        "sources": [],
        "metadata": None,
        "primary_source": None
    }

    # Check if it's a PDB ID
    if is_pdb_id(query):
        pdb_id = query.upper()
        pdb_url = build_pdb_url(pdb_id)
        
        # Verify PDB file exists
        try:
            head = requests.head(pdb_url, timeout=10)
            if head.status_code < 400:
                result["sources"].append({
                    "type": "PDB",
                    "id": pdb_id,
                    "url": pdb_url,
                    "description": f"Experimental structure from Protein Data Bank"
                })
                result["primary_source"] = "PDB"
                
                # Get PDB metadata
                pdb_metadata = get_pdb_metadata(pdb_id)
                if pdb_metadata:
                    result["metadata"] = pdb_metadata
                    
        except Exception as exc:
            logger.info("PDB check failed for %s: %s", pdb_id, exc)
    
    # Check if it's a UniProt ID or resolve from name
    uniprot_acc = None
    if is_uniprot_id(query):
        uniprot_acc = query.upper()
    else:
        uniprot_acc = uniprot_lookup_by_name(query)
    
    if uniprot_acc:
        afdb_url = build_afdb_pdb_url(uniprot_acc)
        
        # Check if AlphaFold structure exists
        try:
            head = requests.head(afdb_url, timeout=10)
            if head.status_code < 400:
                result["sources"].append({
                    "type": "AlphaFold",
                    "id": uniprot_acc,
                    "url": afdb_url,
                    "description": f"AI-predicted structure from AlphaFold DB"
                })
                
                if not result["primary_source"]:
                    result["primary_source"] = "AlphaFold"
                
                # Get UniProt metadata (prefer this over PDB metadata for proteins)
                uniprot_metadata = get_protein_metadata(uniprot_acc)
                if uniprot_metadata:
                    result["metadata"] = uniprot_metadata
                    
        except Exception as exc:
            logger.info("AlphaFold check failed for %s: %s", uniprot_acc, exc)

    if not result["sources"]:
        return jsonify({
            "error": f"No structures found for '{query}'",
            "suggestion": "Try a different UniProt ID, PDB ID, or protein name"
        }), 404

    return jsonify(result)


@app.get("/api/metadata/<source_type>/<structure_id>")
def get_metadata_endpoint(source_type: str, structure_id: str) -> Response:
    """Get detailed metadata for a specific structure."""
    
    if source_type.lower() == "alphafold":
        metadata = get_protein_metadata(structure_id)
    elif source_type.lower() == "pdb":
        metadata = get_pdb_metadata(structure_id)
    else:
        return jsonify({"error": "Invalid source type. Use 'alphafold' or 'pdb'"}), 400
    
    if not metadata:
        return jsonify({"error": f"Metadata not found for {structure_id}"}), 404
    
    return jsonify(metadata)


@app.post("/api/export")
def export_structure() -> Response:
    """Export structure in various formats."""
    
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    format_type = data.get("format", "pdb").lower()
    
    if not url:
        return jsonify({"error": "Missing structure URL"}), 400
    
    if format_type not in ["pdb", "mmcif"]:
        return jsonify({"error": "Unsupported format. Use 'pdb' or 'mmcif'"}), 400
    
    try:
        # For now, we'll just return the PDB content
        # In a full implementation, you'd convert between formats
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        filename = f"structure.{format_type}"
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format_type}', delete=False) as f:
            f.write(response.text)
            temp_path = f.name
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='chemical/x-pdb' if format_type == 'pdb' else 'chemical/x-mmcif'
        )
        
    except Exception as exc:
        logger.error("Export failed: %s", exc)
        return jsonify({"error": f"Export failed: {str(exc)}"}), 500


@app.get("/proxy")
def proxy() -> Response:
    """Stream protein structure files to avoid CORS issues.

    Usage: ``/proxy?url=https://alphafold.ebi.ac.uk/files/AF-P05067-F1-model_v4.pdb``
    Supports both AlphaFold and PDB hosts listed in :data:`ALLOWED_PROXY_HOSTS`.
    """

    raw_url = request.args.get("url", "")
    if not raw_url:
        return abort(400, "Missing url parameter")

    try:
        parsed = urllib.parse.urlparse(raw_url)
    except Exception:
        return abort(400, "Invalid URL format")

    if parsed.scheme not in {"http", "https"}:
        return abort(400, "Unsupported URL scheme")
    if parsed.hostname not in ALLOWED_PROXY_HOSTS:
        return abort(400, f"Host not allowed. Supported hosts: {', '.join(ALLOWED_PROXY_HOSTS)}")

    try:
        upstream = requests.get(raw_url, stream=True, timeout=30)
        upstream.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.warning("Upstream fetch failed for %s: %s", raw_url, exc)
        return abort(502, f"Failed to fetch structure: {str(exc)}")

    content_type = upstream.headers.get("Content-Type", "text/plain")

    def gen():
        for chunk in upstream.iter_content(chunk_size=65536):
            if chunk:
                yield chunk

    return Response(gen(), status=200, content_type=content_type)


if __name__ == "__main__":  # pragma: no cover
    import sys
    import socket
    
    def is_port_available(port):
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return True
        except OSError:
            return False
    
    # Check for port argument
    port = APP_PORT
    for i, arg in enumerate(sys.argv):
        if arg == '--port' and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                print(f"Invalid port number: {sys.argv[i + 1]}")
                sys.exit(1)
    
    # Try different ports if the specified one is busy
    available_port = None
    for attempt_port in [port, 5001, 5002, 5003, 8000, 8080]:
        if is_port_available(attempt_port):
            available_port = attempt_port
            break
    
    if available_port:
        print(f"🚀 Starting AlphaFold 3D Protein Viewer on port {available_port}")
        print(f"📱 Open http://localhost:{available_port} in your browser")
        app.run(host="0.0.0.0", port=available_port, debug=False)
    else:
        print("❌ Could not find an available port. Please stop other services or specify a different port.")

