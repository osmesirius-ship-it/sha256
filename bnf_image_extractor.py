#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BnF Image Extractor for Brian and Nicole Audits
Uses IIIF API to extract images from Gallica documents
"""

import requests
import json
import time
import os
from typing import List, Dict, Optional, Tuple
import hashlib

class BnFImageExtractor:
    def __init__(self, delay: float = 3.0):
        """
        Initialize extractor with rate limiting
        delay: seconds between requests (default 3.0 for BnF rate limits)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResearchBot/1.0 (contact: research@bot.ai)'
        })
        
    def get_iiif_manifest(self, ark: str) -> Optional[Dict]:
        """Get IIIF manifest for document"""
        url = f"https://gallica.bnf.fr/iiif/{ark}/manifest.json"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting manifest for {ark}: {e}")
            return None
    
    def get_page_image_urls(self, ark: str, max_pages: int = 10) -> List[str]:
        """Get image URLs for pages in document"""
        manifest = self.get_iiif_manifest(ark)
        if not manifest:
            return []
        
        image_urls = []
        sequences = manifest.get('sequences', [])
        if not sequences:
            return []
        
        canvases = sequences[0].get('canvases', [])
        for i, canvas in enumerate(canvases[:max_pages]):
            images = canvas.get('images', [])
            if images:
                resource = images[0].get('resource', {})
                image_url = resource.get('@id')
                if image_url:
                    # Convert to high-resolution image URL
                    if '/full/' in image_url:
                        image_url = image_url.replace('/full/', '/full/2000,/')
                    image_urls.append(image_url)
        
        return image_urls
    
    def download_image(self, image_url: str, output_path: str) -> bool:
        """Download image from URL"""
        try:
            response = self.session.get(image_url, timeout=60)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
            return False
    
    def extract_images_for_audit(self, audit_csv: str, output_dir: str, max_pages_per_doc: int = 5):
        """Extract images for all documents in audit CSV"""
        import csv
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Read audit results
        with open(audit_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            audit_data = list(reader)
        
        extracted_data = []
        
        for row in audit_data:
            # Handle different CSV formats (Brian vs Nicole)
            ark = row.get('ark') or row.get('ARK')
            layer = row.get('layer') or row.get('Layer')
            page_index = int(row.get('page_index') or row.get('PageIndex0'))
            
            print(f"Processing Layer {layer}: {ark}")
            
            # Get image URLs for this document
            image_urls = self.get_page_image_urls(ark, max_pages_per_doc)
            
            if not image_urls:
                print(f"No images found for {ark}")
                continue
            
            # Download images around the selected page
            start_page = max(0, page_index - 2)
            end_page = min(len(image_urls), page_index + 3)
            
            layer_images = []
            for i in range(start_page, end_page):
                if i < len(image_urls):
                    image_url = image_urls[i]
                    
                    # Clean layer name for filename
                    layer_clean = str(layer).replace('L', '')
                    safe_ark = ark.replace('/', '_').replace(':', '_')
                    filename = f"layer{layer_clean}_page{i}_{safe_ark}.jpg"
                    filepath = os.path.join(output_dir, filename)
                    
                    # Download image
                    if self.download_image(image_url, filepath):
                        layer_images.append({
                            'layer': layer,
                            'ark': ark,
                            'page_index': i,
                            'image_url': image_url,
                            'filepath': filepath,
                            'filename': filename
                        })
                        print(f"Downloaded: {filename}")
                    
                    # Rate limiting
                    time.sleep(self.delay)
            
            extracted_data.extend(layer_images)
        
        # Save extraction metadata
        metadata_file = os.path.join(output_dir, 'extraction_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2)
        
        print(f"Extraction complete. {len(extracted_data)} images downloaded.")
        print(f"Metadata saved to: {metadata_file}")
        
        return extracted_data

def main():
    """Main extraction process"""
    extractor = BnFImageExtractor(delay=3.0)
    
    # Extract images for Brian audit
    print("=== Extracting images for Brian audit ===")
    brian_csv = "/Users/user/CascadeProjects/windsurf-project/demo_audit.csv"
    brian_output = "/Users/user/sha256/brian_images"
    
    if os.path.exists(brian_csv):
        brian_images = extractor.extract_images_for_audit(brian_csv, brian_output, max_pages_per_doc=3)
    else:
        print(f"Brian audit CSV not found: {brian_csv}")
    
    # Extract images for Nicole audit
    print("\n=== Extracting images for Nicole audit ===")
    nicole_csv = "/Users/user/sha256/nicole_bess_audit.csv"
    nicole_output = "/Users/user/sha256/nicole_images"
    
    if os.path.exists(nicole_csv):
        nicole_images = extractor.extract_images_for_audit(nicole_csv, nicole_output, max_pages_per_doc=3)
    else:
        print(f"Nicole audit CSV not found: {nicole_csv}")
    
    print("\n=== Image extraction complete ===")

if __name__ == "__main__":
    main()
