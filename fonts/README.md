# Font Files for SHA-256 Analysis Project

## Overview
This directory contains custom font files for displaying Annunaki language characters and English text in documentation and analysis outputs.

## Font Files

### Annunaki Language Font
- **File**: `annunaki.woff`
- **Purpose**: Display ancient Annunaki cuneiform-style characters
- **Usage**: CSS font-family: 'Annunaki'
- **Character Set**: Ancient Mesopotamian symbols, cuneiform derivatives

### English Documentation Font  
- **File**: `documentation.woff`
- **Purpose**: Clean, readable English text for technical documentation
- **Usage**: CSS font-family: 'Documentation'
- **Character Set**: Full English alphabet, numbers, symbols

## CSS Implementation

```css
@font-face {
    font-family: 'Annunaki';
    src: url('./annunaki.woff') format('woff');
    font-weight: normal;
    font-style: normal;
}

@font-face {
    font-family: 'Documentation';
    src: url('./documentation.woff') format('woff');
    font-weight: normal;
    font-style: normal;
}

.annunaki-text {
    font-family: 'Annunaki', serif;
    font-size: 1.2em;
}

.documentation-text {
    font-family: 'Documentation', sans-serif;
    font-size: 1em;
    line-height: 1.6;
}
```

## Installation

### Web Usage
1. Copy font files to your web server's `/fonts` directory
2. Include the CSS font-face declarations in your stylesheet
3. Apply font classes to HTML elements

### Local Development
1. Install fonts in your system's font directory:
   - macOS: `/Library/Fonts/` or `~/Library/Fonts/`
   - Windows: `C:\Windows\Fonts\`
   - Linux: `/usr/share/fonts/` or `~/.fonts/`

## Character Mapping

### Annunaki Script
The Annunaki font includes characters for:
- Numeric symbols (1-100)
- Planetary symbols
- Elemental representations
- Sacred geometric forms

### English Support
Full Unicode support including:
- Latin alphabet (A-Z, a-z)
- Numbers (0-9)
- Punctuation and symbols
- Extended Unicode characters

## Browser Compatibility
- Chrome 6+
- Firefox 3.6+
- Safari 5.1+
- Edge 12+
- IE 9+ (limited support)

## File Formats
- **WOFF**: Web Open Font Format (primary)
- **WOFF2**: Compressed version (if available)
- **TTF**: TrueType (fallback)

## License
These fonts are created specifically for the SHA-256 analysis project and should be used according to project licensing terms.

## Development Notes
- Fonts optimized for screen rendering
- Embedded hinting for better readability
- Compressed for web performance
- Cross-platform compatibility tested
