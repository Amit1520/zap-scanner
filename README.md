# Web Vulnerability Scanner Dashboard

A modern web interface for running OWASP ZAP vulnerability scans and viewing reports.

## Features

- ✅ Input a target URL
- ✅ Start a scan (via OWASP ZAP)
- ✅ View live scan status
- ✅ Download HTML/PDF report
- ✅ Show vulnerability summary

## Prerequisites

1. Python 3.7+
2. OWASP ZAP installed and running
3. wkhtmltopdf (for PDF report generation)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install wkhtmltopdf:
- Windows: Download from https://wkhtmltopdf.org/downloads.html
- Linux: `sudo apt install wkhtmltopdf`
- macOS: `brew install wkhtmltopdf`

## Usage

1. Start ZAP in daemon mode:
```bash
zap.sh -daemon -port 8090 -config api.disablekey=true
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
zap-scanner-web/
│
├── app.py                  # Flask backend
├── zap_scanner.py          # Scan logic
├── templates/
│   ├── index.html         # Homepage with form
│   └── report.html        # Report summary UI
├── reports/               # Generated reports
└── requirements.txt       # Python dependencies
```

## Security Note

This tool is for authorized security testing only. Always obtain proper permission before scanning any website. 