import os
import re
import json
import urllib.parse
from functools import lru_cache
from typing import Optional

import requests
from flask import Flask, request, jsonify, render_template, Response, abort
from flask_cors import CORS

APP_PORT = int(os.environ.get("PORT", "5000"))
ALLOWED_PROXY_HOSTS = {"alphafold.ebi.ac.uk"}  # keep this tight

app = Flask(__name__)
CORS(app)

UNIPROT_RE = re.compile(
    r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})$",
    re.IGNORECASE,
)


def is_uniprot_id(q: str) -> bool:
    return bool(UNIPROT_RE.match(q.strip()))


def build_afdb_pdb_url(accession: str) -> str:
    # AlphaFold DB file naming (version 4 models)
    # Example: https://alphafold.ebi.ac.uk/files/AF-P05067-F1-model_v4.pdb
    acc = accession.strip().upper()
    return f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v4.pdb"


@lru_cache(maxsize=256)
def uniprot_lookup_by_name(name: str) -> Optional[str]:
    """
    Resolve a protein 'name' to a UniProt accession using UniProt's REST API.
    We request 1 best hit. Fallback: None.
    """
    try:
        # fields kept small to minimize payload;  size=1 for the top hit
        params = {
            "query": name,
            "format": "tsv",
            "fields": "accession,protein_name,organism_name",
            "size": 1,
        }
        r = requests.get(
            "https://rest.uniprot.org/uniprotkb/search",
            params=params,
            timeout=10,
        )
        r.raise_for_status()
        lines = r.text.strip().splitlines()
        if len(lines) < 2:
            return None
        header = lines[0].split("\t")
        acc_idx = header.index("Entry")
        first = lines[1].split("\t")
        return first[acc_idx]
    except Exception:
        return None


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/search")
def search():
    """
    Input JSON: {"query": "..."} where query is UniProt ID (e.g. P05067) or a protein name (e.g. insulin).
    Output JSON: {"accession": "...", "pdb_url": "..."} or 400 if cannot resolve.
    """
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Missing 'query'"}), 400

    if is_uniprot_id(query):
        acc = query.upper()
    else:
        acc = uniprot_lookup_by_name(query)
        if not acc:
            return jsonify({"error": "Could not resolve to a UniProt accession"}), 404

    pdb_url = build_afdb_pdb_url(acc)

    # Optional: quick HEAD to verify existence (small extra cost but nicer UX)
    try:
        head = requests.head(pdb_url, timeout=10)
        if head.status_code >= 400:
            return jsonify({"error": f"AlphaFold file not found for {acc}"}), 404
    except Exception as e:
        return jsonify({"error": f"Upstream check failed: {e}"}), 502

    return jsonify({"accession": acc, "pdb_url": pdb_url})


@app.get("/proxy")
def proxy():
    """
    Stream a remote AlphaFold file to the browser to avoid CORS/mixed-content issues.
    Usage: /proxy?url=https://alphafold.ebi.ac.uk/files/AF-P05067-F1-model_v4.pdb
    Only whitelisted hosts are allowed.
    """
    raw_url = request.args.get("url", "")
    if not raw_url:
        return abort(400, "Missing url")

    # sanitize and restrict host
    try:
        parsed = urllib.parse.urlparse(raw_url)
    except Exception:
        return abort(400, "Invalid url")

    if parsed.scheme not in {"http", "https"}:
        return abort(400, "Unsupported scheme")
    if parsed.hostname not in ALLOWED_PROXY_HOSTS:
        return abort(400, "Host not allowed")

    try:
        upstream = requests.get(raw_url, stream=True, timeout=30)
    except Exception as e:
        return abort(502, f"Upstream error: {e}")

    if upstream.status_code >= 400:
        return abort(upstream.status_code)

    # pass through content-type; default text/plain to be safe
    content_type = upstream.headers.get("Content-Type", "text/plain")

    # stream chunks
    def gen():
        for chunk in upstream.iter_content(chunk_size=65536):
            if chunk:
                yield chunk

    return Response(gen(), status=200, content_type=content_type)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)

