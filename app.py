"""Flask backend for the AlphaFold 3D viewer.

This version hardens the search endpoint and makes the proxy more robust.
It gracefully handles upstream network failures, verifies query types and
ensures endpoints work when the app is hosted under a sub-path.
"""

import logging
import os
import re
import urllib.parse
from functools import lru_cache
from typing import Optional

import requests
from flask import Flask, Response, abort, jsonify, render_template, request
from flask_cors import CORS


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_PORT = int(os.environ.get("PORT", "5000"))
ALLOWED_PROXY_HOSTS = {"alphafold.ebi.ac.uk"}

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


def build_afdb_pdb_url(accession: str) -> str:
    """Construct the AlphaFold DB PDB URL for *accession*.

    AlphaFold DB version 4 models follow the pattern
    ``https://alphafold.ebi.ac.uk/files/AF-<ACC>-F1-model_v4.pdb``.
    """

    acc = accession.strip().upper()
    return f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v4.pdb"


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
    """Resolve a UniProt accession and return the AlphaFold DB URL.

    Request body: ``{"query": "<UniProt ID or protein name>"}``

    If the query looks like an amino-acid sequence we return a 400 error with
    an explanatory message, since sequence search is not supported yet.
    """

    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Missing 'query'"}), 400

    if is_amino_acid_sequence(query):
        return (
            jsonify({"error": "Searching by amino acid sequence is not yet supported."}),
            400,
        )

    if is_uniprot_id(query):
        acc = query.upper()
    else:
        acc = uniprot_lookup_by_name(query)
        if not acc:
            return jsonify({"error": "Could not resolve to a UniProt accession"}), 404

    pdb_url = build_afdb_pdb_url(acc)

    # Verify the file exists with a HEAD request, but fail softly if network
    # access is blocked. In that case we still return the URL so the client can
    # attempt to fetch it via the proxy.
    try:
        head = requests.head(pdb_url, timeout=10)
        if head.status_code >= 400:
            return jsonify({"error": f"AlphaFold file not found for {acc}"}), 404
    except Exception as exc:  # pragma: no cover - network failures
        logger.info("Skipping HEAD check for %s due to %s", pdb_url, exc)

    return jsonify({"accession": acc, "pdb_url": pdb_url})


@app.get("/proxy")
def proxy() -> Response:
    """Stream an AlphaFold PDB file to the client to avoid CORS issues.

    Usage: ``/proxy?url=https://alphafold.ebi.ac.uk/files/AF-P05067-F1-model_v4.pdb``
    Only hosts listed in :data:`ALLOWED_PROXY_HOSTS` are permitted.
    """

    raw_url = request.args.get("url", "")
    if not raw_url:
        return abort(400, "Missing url")

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
    except Exception as exc:  # pragma: no cover - network failures
        logger.warning("Upstream fetch failed for %s: %s", raw_url, exc)
        return abort(502, f"Upstream error: {exc}")

    if upstream.status_code >= 400:
        return abort(upstream.status_code)

    content_type = upstream.headers.get("Content-Type", "text/plain")

    def gen():
        for chunk in upstream.iter_content(chunk_size=65536):
            if chunk:
                yield chunk

    return Response(gen(), status=200, content_type=content_type)


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=APP_PORT)

