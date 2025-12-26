import hashlib, unicodedata, re
import json

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

def pick_indices(layer_hex: str, ndocs: int, npages: int, text_len: int):
    I = int(layer_hex, 16)
    doc_idx = I % ndocs
    page_idx = (I // ndocs) % max(1, npages)
    off = (I // (ndocs * max(1, npages))) % max(1, text_len)
    return doc_idx, page_idx, off

def main():
    layers = hash_chain_13(CANONICAL)
    
    # Mock ARKs (simulating what would be returned from SRU search)
    mock_arks = [
        "ark:/12148/cb30657183x",
        "ark:/12148/bpt6k65374s", 
        "ark:/12148/cb30346886x",
        "ark:/12148/bpt6k33731631",
        "ark:/12148/cb325073617",
        "ark:/12148/bpt6k63136911",
        "ark:/12148/bpt6k1040322",
        "ark:/12148/bpt6k3412439p",
        "ark:/12148/bpt6k624285",
        "ark:/12148/cb35436604v"
    ]
    
    print("Hash Chain Layers:")
    for i, layer in enumerate(layers, 1):
        print(f"L{i}: {layer}")
    
    print("\nDeterministic Selection Demo:")
    print("Using mock corpus of {} documents".format(len(mock_arks)))
    
    rows = []
    for i, h in enumerate(layers, start=1):
        # Mock document selection
        doc_idx, page_idx, off = pick_indices(h, len(mock_arks), 100, 50000)
        ark = mock_arks[doc_idx]
        
        row = {
            "Layer": f"L{i}",
            "DigestHex": h,
            "ARK": ark,
            "PageIndex0": page_idx,
            "Offset": off,
            "Snippet": f"[Mock snippet from {ark} page {page_idx} offset {off}]",
            "IIIF_Manifest": f"https://gallica.bnf.fr/iiif/{ark}/manifest.json",
            "OCR_URL": f"https://gallica.bnf.fr/{ark}/texteBrut",
        }
        rows.append(row)
        
        print(f"L{i}: ARK={ark}, Page={page_idx}, Offset={off}")
    
    # Save demo results
    with open("demo_audit.csv", "w", newline="", encoding="utf-8") as f:
        import csv
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    
    print(f"\nWrote demo_audit.csv with {len(rows)} deterministic selections")
    
    # Also save the hash layers
    with open("brian_layers.json", "w", encoding="utf-8") as f:
        json.dump({"canonical": CANONICAL, "layers": layers}, f, indent=2)
    
    print("Wrote brian_layers.json with hash chain")

if __name__ == "__main__":
    main()
