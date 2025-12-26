import requests
from bs4 import BeautifulSoup

WINDOW = 250  # characters before/after offset

layers = [
    ("L1",  "cb30657183x", 43, 1158),
    ("L2",  "bpt6k63136911", 79, 30994),
    ("L3",  "cb30657183x", 86, 43329),
    ("L4",  "bpt6k63136911", 65, 27722),
    ("L5",  "bpt6k65374s", 70, 15877),
    ("L6",  "bpt6k33731631", 14, 16263),
    ("L7",  "cb30657183x", 57, 16087),
    ("L8",  "cb30657183x", 52, 42155),
    ("L9",  "cb325073617", 97, 3105),
    ("L10", "cb30346886x", 47, 19849),
    ("L11", "bpt6k63136911", 51, 8572),
    ("L12", "bpt6k63136911", 8, 14133),
    ("L13", "bpt6k65374s", 77, 3416),
]

HEADERS = {
    "User-Agent": "GallicaResearch/1.0 (contact: you@example.com)"
}

def fetch_ocr(ark):
    url = f"https://gallica.bnf.fr/ark:/12148/{ark}/texteBrut"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ")
    # normalize whitespace
    return " ".join(text.split())

def extract_window(text, offset, window=WINDOW):
    start = max(0, offset - window)
    end = min(len(text), offset + window)
    return text[start:end]

def main():
    cache = {}

    for layer, ark, page, offset in layers:
        if ark not in cache:
            print(f"\nFetching OCR for {ark} …")
            cache[ark] = fetch_ocr(ark)

        text = cache[ark]
        snippet = extract_window(text, offset)

        print("\n" + "="*80)
        print(f"{layer} — ark:/12148/{ark} — Page {page} — Offset {offset}")
        print("-"*80)
        print(snippet)
        print("="*80)

if __name__ == "__main__":
    main()
