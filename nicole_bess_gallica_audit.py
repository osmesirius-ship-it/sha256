#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nicole Bess Gallica Audit Trail System
13-Layer SHA-256 Hash Cascade for deterministic document selection from Gallica Digital Library
"""

import hashlib
import unicodedata
import requests
import json
import csv
import re
from typing import List, Dict, Tuple, Optional
import time
import random

# Nicole Bess canonical identity string
CANONICAL = "Nicole Bess – 1996-03-06T17:46 Phoenix, AZ"

# Provided 13-layer SHA-256 hash cascade
PROVIDED_HASHES = [
    "43bdd61eb54f6db9c23e911cbd48c70192a4cb7fb8e31a02794f00ef6b82f4ca",
    "57bc68a9898e8cc6c930d479cafe703d7496cea7fa6d50295b560c7419ec5ac0", 
    "edb4aae8cc966c69d7b85aabf838c6fa09a89e668a4e57377e03f8f81627f5e4",
    "47b976f71f0762df086053a6c2788c73e09f19558588a467b627916e358330ff",
    "55e34c8cd1fb524c4e642b86c1c57d162d595fbf74c3df5be1fcad5cbf5d0fba",
    "e8d09e14486a73faf5625621409c21409934907c3c889472388d48a9b9651809",
    "888772f88bd45768ebfce471d935ce6a6d6793d1941ddbc4f9587c20d6a85bd9",
    "45c9500441d229af504f28096a5592844ae941810d0be5f9b049c54acee95efb",
    "c71de44f4c64693c1f7abc5785f0c9eb7a9926f82f556f219267325f3401d824",
    "cf8e2a9f117c43d7feeeb534b2aff103aebdbc27f32947617119545625324fe4",
    "24321707b2a3dc5991d5cedb7ae1d0b0e8891b117e009d4271a5792ebe4a5fcd",
    "9c7bb215182da1dc0b551119acd8c529578f01cfe2e3877525670be58b2699a1",
    "7443ecf02daa8b89c0cbc21d779770b97af67c9f411153a2feeeb8fbc3bb9e0b"
]

def normalize_bytes(s: str) -> bytes:
    """Unicode NFC normalize and clean special characters"""
    normalized = unicodedata.normalize('NFC', s)
    # Remove control characters and normalize whitespace
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', normalized)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.encode('utf-8')

def hash_chain_13(canonical: str) -> List[str]:
    """Generate 13-layer SHA-256 hash chain"""
    current = canonical
    layers = []
    
    for i in range(13):
        digest = hashlib.sha256(normalize_bytes(current)).hexdigest()
        layers.append(digest)
        current = digest
    
    return layers

def pick_indices(hex_hash: str, doc_count: int, max_pages: int, max_chars: int) -> Tuple[int, int, int]:
    """Deterministically select document, page, and character offset from hash"""
    # Use first 8 bytes for document selection
    doc_bytes = bytes.fromhex(hex_hash[:16])
    doc_idx = int.from_bytes(doc_bytes, 'big') % doc_count
    
    # Use next 8 bytes for page selection  
    page_bytes = bytes.fromhex(hex_hash[16:32])
    page_idx = int.from_bytes(page_bytes, 'big') % max_pages
    
    # Use last 8 bytes for character offset
    offset_bytes = bytes.fromhex(hex_hash[32:48])
    char_offset = int.from_bytes(offset_bytes, 'big') % max_chars
    
    return doc_idx, page_idx, char_offset

def sru_search(query_cql: str, max_records: int = 50) -> str:
    """Search Gallica SRU API"""
    url = "https://gallica.bnf.fr/SRU"
    params = {
        "version": "1.2",
        "operation": "searchRetrieve", 
        "query": query_cql,
        "maximumRecords": str(max_records),
        "suggest": "0"
    }
    headers = {
        "User-Agent": "ResearchBot/1.0 (contact: nicole@research.bot)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"SRU search error: {e}")
        return ""

def fetch_manifest(ark: str) -> Optional[Dict]:
    """Fetch IIIF manifest for document metadata"""
    url = f"https://gallica.bnf.fr/iiif/{ark}/manifest.json"
    headers = {
        "User-Agent": "ResearchBot/1.0 (contact: nicole@research.bot)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Manifest fetch error for {ark}: {e}")
        return None

def fetch_ocr_plain(ark: str) -> Optional[str]:
    """Fetch OCR text for document"""
    url = f"https://gallica.bnf.fr/{ark}/texteBrut"
    headers = {
        "User-Agent": "ResearchBot/1.0 (contact: nicole@research.bot)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"OCR fetch error for {ark}: {e}")
        return None

def extract_arks_from_sru(sru_response: str) -> List[str]:
    """Extract ARK identifiers from SRU response"""
    arks = []
    # Look for ARK patterns in the response
    ark_pattern = r'ark:/12148/[^<\s]+'
    matches = re.findall(ark_pattern, sru_response)
    arks.extend(matches)
    return list(set(arks))  # Remove duplicates

def get_text_snippet(text: str, offset: int, length: int = 200) -> str:
    """Extract text snippet at given offset"""
    if not text or offset >= len(text):
        return "[No text available]"
    
    start = max(0, offset)
    end = min(len(text), start + length)
    snippet = text[start:end]
    
    # Clean up the snippet
    snippet = re.sub(r'\s+', ' ', snippet)
    snippet = snippet.strip()
    
    if len(snippet) < 10:
        return "[Text fragment too short]"
    
    return snippet

def analyze_text_content(text: str, layer_num: int, hex_hash: str) -> Dict:
    """Perform textual analysis on extracted content"""
    if not text or len(text) < 50:
        return {
            "word_count": 0,
            "language_hint": "unknown",
            "themes": [],
            "sentiment": "neutral",
            "keywords": []
        }
    
    # Basic text statistics
    words = text.split()
    word_count = len(words)
    
    # Simple language detection based on common words
    french_words = ['le', 'la', 'les', 'de', 'et', 'un', 'une', 'des', 'il', 'elle']
    english_words = ['the', 'and', 'of', 'to', 'in', 'is', 'it', 'you', 'that', 'he']
    
    french_count = sum(1 for word in words if word.lower() in french_words)
    english_count = sum(1 for word in words if word.lower() in english_words)
    
    language_hint = "french" if french_count > english_count else "english"
    
    # Theme detection based on keywords
    themes = []
    text_lower = text.lower()
    
    theme_keywords = {
        "philosophy": ["philosoph", "pensée", "esprit", "âme", "conscience"],
        "science": ["science", "nature", "expérience", "observation", "théorie"],
        "religion": ["dieu", "religion", "spirituel", "sacré", "prière"],
        "history": ["histoire", "temps", "passé", "ancien", "mémoire"],
        "literature": ["poème", "roman", "vers", "littérature", "écriture"],
        "mysticism": ["mystique", "occulte", "magie", "spirituel", "initiation"]
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            themes.append(theme)
    
    # Sentiment analysis (simplified)
    positive_words = ['beau', 'bon', 'bien', 'joie', 'amour', 'lumière', 'vérité']
    negative_words = ['mal', 'peur', 'noir', 'mort', 'souffrance', 'darkness']
    
    pos_count = sum(1 for word in words if word.lower() in positive_words)
    neg_count = sum(1 for word in words if word.lower() in negative_words)
    
    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    # Extract keywords (most frequent words)
    keywords = []
    if words:
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if len(word_lower) > 4:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        keywords = sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:10]
    
    return {
        "word_count": word_count,
        "language_hint": language_hint,
        "themes": themes,
        "sentiment": sentiment,
        "keywords": keywords
    }

def main():
    """Main audit trail execution"""
    print("=== Nicole Bess Gallica Audit Trail System ===")
    print(f"Canonical: {CANONICAL}")
    print(f"Using provided 13-layer SHA-256 cascade")
    print()
    
    # Use provided hashes instead of generating
    layers = PROVIDED_HASHES
    
    # Search for relevant documents in Gallica
    print("Searching Gallica for relevant documents...")
    search_queries = [
        'gallica all "philosophie"',
        'gallica all "science"',
        'gallica all "mysticism"',
        'gallica all "occult"',
        'gallica all "spiritualité"'
    ]
    
    all_arks = []
    for query in search_queries:
        print(f"Searching: {query}")
        sru_response = sru_search(query, max_records=20)
        if sru_response:
            arks = extract_arks_from_sru(sru_response)
            all_arks.extend(arks)
            print(f"Found {len(arks)} ARKs")
        time.sleep(1)  # Rate limiting
    
    # Remove duplicates and limit
    all_arks = list(set(all_arks))[:30]  # Limit to 30 documents
    print(f"Total unique ARKs: {len(all_arks)}")
    
    if not all_arks:
        print("No ARKs found, using mock data for demonstration")
        all_arks = [
            "ark:/12148/cb30657183x",
            "ark:/12148/bpt6k65374s", 
            "ark:/12148/cb32855771v",
            "ark:/12148/bpt6k58051f",
            "ark:/12148/cb31596080n"
        ]
    
    # Process each hash layer
    audit_results = []
    
    for i, hex_hash in enumerate(layers, start=1):
        print(f"\n--- Layer {i} ---")
        print(f"Hash: {hex_hash}")
        
        # Select document, page, and offset deterministically
        doc_idx, page_idx, char_offset = pick_indices(hex_hash, len(all_arks), 100, 50000)
        selected_ark = all_arks[doc_idx]
        
        print(f"Selected ARK: {selected_ark}")
        print(f"Page index: {page_idx}, Character offset: {char_offset}")
        
        # Fetch document metadata
        manifest = fetch_manifest(selected_ark)
        page_count = 0
        title = "Unknown"
        
        if manifest:
            title = manifest.get('label', 'Unknown')
            # Count pages from manifest
            sequences = manifest.get('sequences', [])
            if sequences:
                canvases = sequences[0].get('canvases', [])
                page_count = len(canvases)
        
        # Fetch OCR text
        ocr_text = fetch_ocr_plain(selected_ark)
        text_snippet = ""
        analysis = {}
        
        if ocr_text:
            text_snippet = get_text_snippet(ocr_text, char_offset, 200)
            analysis = analyze_text_content(text_snippet, i, hex_hash)
        else:
            text_snippet = "[OCR text unavailable]"
            analysis = {"error": "No OCR data available"}
        
        # Store result
        result = {
            "layer": i,
            "hash_hex": hex_hash,
            "ark": selected_ark,
            "title": title,
            "page_index": page_idx,
            "page_count": page_count,
            "char_offset": char_offset,
            "text_snippet": text_snippet,
            "analysis": analysis,
            "iiif_manifest": f"https://gallica.bnf.fr/iiif/{selected_ark}/manifest.json",
            "ocr_url": f"https://gallica.bnf.fr/{selected_ark}/texteBrut"
        }
        
        audit_results.append(result)
        
        print(f"Title: {title}")
        print(f"Pages: {page_count}")
        print(f"Text snippet: {text_snippet[:100]}...")
        print(f"Analysis: {analysis}")
        
        time.sleep(2)  # Rate limiting
    
    # Save results to CSV
    csv_file = "nicole_bess_audit.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'layer', 'hash_hex', 'ark', 'title', 'page_index', 'page_count',
            'char_offset', 'text_snippet', 'word_count', 'language_hint',
            'themes', 'sentiment', 'keywords', 'iiif_manifest', 'ocr_url'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in audit_results:
            row = {
                'layer': result['layer'],
                'hash_hex': result['hash_hex'],
                'ark': result['ark'],
                'title': result['title'],
                'page_index': result['page_index'],
                'page_count': result['page_count'],
                'char_offset': result['char_offset'],
                'text_snippet': result['text_snippet'],
                'word_count': result['analysis'].get('word_count', 0),
                'language_hint': result['analysis'].get('language_hint', 'unknown'),
                'themes': ';'.join(result['analysis'].get('themes', [])),
                'sentiment': result['analysis'].get('sentiment', 'neutral'),
                'keywords': ';'.join(result['analysis'].get('keywords', [])),
                'iiif_manifest': result['iiif_manifest'],
                'ocr_url': result['ocr_url']
            }
            writer.writerow(row)
    
    print(f"\nResults saved to {csv_file}")
    
    # Save hash cascade to JSON
    cascade_data = {
        "canonical": CANONICAL,
        "layers": layers,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("nicole_bess_layers.json", 'w', encoding='utf-8') as f:
        json.dump(cascade_data, f, indent=2)
    
    print("Hash cascade saved to nicole_bess_layers.json")
    print("\n=== Audit Complete ===")

if __name__ == "__main__":
    main()
