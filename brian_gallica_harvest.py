# -*- coding: utf-8 -*-
import hashlib, unicodedata, re, csv, requests
from xml.etree import ElementTree as ET

CANONICAL = "Brian Christopher Perkins - 1975-05-11 Toledo, OH"

def normalize_bytes(s: str) -> bytes:
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"[\u2013\u2014\u2212]", "-", s)
    s = re.sub(r"[\u200B\u200C\u200D\uFEFF]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.encode("utf-8")

def hash_chain_13(canonical: str):
    h = hashlib.sha256(normalize_bytes(canonical)).digest()
    out = [h]
    for _ in range(12):
        h = hashlib.sha256(h).digest()
        out.append(h)
    return [b.hex() for b in out]

def sru_search(query_cql: str, max_records: int = 10):
    url = "https://gallica.bnf.fr/SRU"
    params = {
        "version": "1.2",
        "operation": "searchRetrieve",
        "query": query_cql,
        "maximumRecords": str(max_records),
        "suggest": "0",
    }
    headers = {
        "User-Agent": "ResearchBot/1.0 (contact: you@email.com)"
    }
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def parse_arks_from_sru(xml_text: str):
    arks = sorted(set(re.findall(r"ark:/12148/[a-z0-9]+", xml_text)))
    return arks

def iiif_manifest_url(ark: str):
    return f"https://gallica.bnf.fr/iiif/{ark}/manifest.json"

def fetch_manifest(ark: str):
    headers = {
        "User-Agent": "ResearchBot/1.0 (contact: you@email.com)"
    }
    r = requests.get(iiif_manifest_url(ark), headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def get_canvases(manifest_json):
    if "sequences" in manifest_json:  # v2
        return manifest_json["sequences"][0]["canvases"]
    if "items" in manifest_json:      # v3
        return manifest_json["items"]
    return []

def fetch_ocr_plain(ark: str):
    url = f"https://gallica.bnf.fr/{ark}/texteBrut"
    headers = {
        "User-Agent": "ResearchBot/1.0 (contact: you@email.com)"
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def clean_text(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"[\u200B\u200C\u200D\uFEFF]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def pick_indices(layer_hex: str, ndocs: int, npages: int, text_len: int):
    I = int(layer_hex, 16)
    doc_idx = I % ndocs
    page_idx = (I // ndocs) % max(1, npages)
    off = (I // (ndocs * max(1, npages))) % max(1, text_len)
    return doc_idx, page_idx, off

def main():
    layers = hash_chain_13(CANONICAL)

    cql = '(gallica all "alchimie") and (dc.type any "monographie")'
    sru_xml = sru_search(cql, max_records=12)
    arks = parse_arks_from_sru(sru_xml)

    if len(arks) < 3:
        raise RuntimeError("Corpus too small — broaden the SRU query or raise maximumRecords.")

    rows = []
    for i, h in enumerate(layers, start=1):
        # pick doc
        doc_idx, _, _ = pick_indices(h, len(arks), 1, 1)
        ark = arks[doc_idx]

        # pull manifest to get number of pages
        try:
            manifest = fetch_manifest(ark)
            canvases = get_canvases(manifest)
            npages = max(1, len(canvases))
        except Exception as e:
            print(f"Skipping ARK {ark} due to manifest error: {e}")
            continue

        # fetch OCR (whole doc text) — fallback if not available
        try:
            ocr_raw = fetch_ocr_plain(ark)
            ocr = clean_text(ocr_raw)
            tlen = len(ocr)
        except Exception:
            ocr = ""
            tlen = 1

        # pick page + offset
        doc_idx, page_idx, off = pick_indices(h, len(arks), npages, max(1, tlen))

        snippet = ""
        if ocr:
            lo = max(0, off - 200)
            hi = min(len(ocr), off + 200)
            snippet = ocr[lo:hi]

        rows.append({
            "Layer": f"L{i}",
            "DigestHex": h,
            "ARK": ark,
            "PageIndex0": page_idx,
            "Offset": off,
            "Snippet": snippet[:800],
            "IIIF_Manifest": iiif_manifest_url(ark),
            "OCR_URL": f"https://gallica.bnf.fr/{ark}/texteBrut",
        })

    if not rows:
        print("No valid documents found - all ARKs failed to load")
        return

    with open("audit.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("Wrote audit.csv with deterministic pulls for L1–L13.")

if __name__ == "__main__":
    main()
