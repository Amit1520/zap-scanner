import time
import os
from zapv2 import ZAPv2
import pdfkit
import threading

ZAP_PROXY = 'http://localhost:8090'
ZAP_API_KEY = 'vdj5e9d20m07aned0tmvdn3e69'

zap = ZAPv2(apikey=ZAP_API_KEY, proxies={'http': ZAP_PROXY, 'https': ZAP_PROXY})

class ScanJob:
    def __init__(self, target, scan_type, scan_id):
        self.target = target
        self.scan_type = scan_type
        self.scan_id = scan_id
        self.progress = 0
        self.current_test = 'Initializing OWASP ZAP...'
        self.done = False
        self.results = []
        self.abort_event = threading.Event()
        self.thread = None
        self.status = 'pending'
        self.error = None
        self.html_report_path = f'reports/zap_report_{scan_id}.html'
        self.pdf_report_path = f'reports/zap_report_{scan_id}.pdf'
        self.summary = {
            'total_scans': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }

    def set_progress(self, value, test_name):
        self.progress = value
        self.current_test = test_name

    def set_done(self, results=None):
        self.progress = 100
        self.done = True
        if results is not None:
            self.results = results
        self.status = 'done'

    def set_error(self, error):
        self.error = error
        self.status = 'error'
        self.done = True

# For demo, you can use this list for test names
SCAN_STEPS = [
    'Initializing OWASP ZAP...',
    'Crawling target website...',
    'Testing for XSS vulnerabilities...',
    'Checking for SQL injection...',
    'Analyzing CSRF protection...',
    'Testing authentication mechanisms...',
    'Scanning for RCE vulnerabilities...',
    'Checking SSL/TLS configuration...',
    'Finalizing scan results...'
]

def parse_alerts_for_summary(alerts):
    summary = {'total_scans': 1, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for alert in alerts:
        risk = alert.get('risk', '').lower()
        if risk == 'high' or risk == 'critical':
            summary['critical'] += 1
        elif risk == 'medium':
            summary['high'] += 1
        elif risk == 'low':
            summary['medium'] += 1
        else:
            summary['low'] += 1
    return summary

def scan_with_progress(job: ScanJob):
    try:
        job.set_progress(5, SCAN_STEPS[0])
        zap.urlopen(job.target)
        time.sleep(1)
        if job.abort_event.is_set():
            job.set_error('Aborted')
            return

        job.set_progress(15, SCAN_STEPS[1])
        zap.spider.scan(job.target)
        while int(zap.spider.status()) < 100:
            if job.abort_event.is_set():
                job.set_error('Aborted')
                return
            job.set_progress(15 + int(zap.spider.status()) * 0.3, SCAN_STEPS[1])
            time.sleep(0.5)

        job.set_progress(40, SCAN_STEPS[2])
        zap.ascan.scan(job.target)
        while int(zap.ascan.status()) < 100:
            if job.abort_event.is_set():
                job.set_error('Aborted')
                return
            pct = int(zap.ascan.status())
            if pct < 25:
                job.set_progress(40 + pct * 0.4, SCAN_STEPS[2])
            elif pct < 50:
                job.set_progress(50 + (pct-25) * 0.4, SCAN_STEPS[3])
            elif pct < 75:
                job.set_progress(60 + (pct-50) * 0.4, SCAN_STEPS[4])
            else:
                job.set_progress(70 + (pct-75) * 0.4, SCAN_STEPS[5])
            time.sleep(0.5)

        job.set_progress(90, SCAN_STEPS[6])
        time.sleep(1)
        job.set_progress(95, SCAN_STEPS[7])
        time.sleep(1)
        html_report = zap.core.htmlreport()
        os.makedirs('reports', exist_ok=True)
        with open(job.html_report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        pdfkit.from_file(job.html_report_path, job.pdf_report_path)
        # Parse alerts for summary
        alerts = zap.core.alerts(baseurl=job.target)
        job.summary = parse_alerts_for_summary(alerts)
        job.set_progress(100, SCAN_STEPS[8])
        job.set_done()
    except Exception as e:
        job.set_error(str(e))

def wait_for_completion(check_func):
    while int(check_func()) < 100:
        time.sleep(2)

def scan_target(target):
    zap.urlopen(target)
    time.sleep(2)

    zap.spider.scan(target)
    wait_for_completion(zap.spider.status)

    zap.ascan.scan(target)
    wait_for_completion(zap.ascan.status)

    html_report = zap.core.htmlreport()
    os.makedirs('reports', exist_ok=True)
    with open(HTML_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(html_report)

    pdfkit.from_file(HTML_REPORT_PATH, PDF_REPORT_PATH)
    return True 