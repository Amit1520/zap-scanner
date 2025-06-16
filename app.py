from flask import Flask, render_template, request, send_file, redirect, url_for, session, jsonify, abort
from zap_scanner import scan_target, ScanJob, scan_with_progress
import threading
import uuid
import os
import secrets

app = Flask(__name__)
# Use environment variable for secret key, fallback to generated key for development
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

tasks = {}

def get_latest_summary():
    scan_id = session.get('scan_id')
    if scan_id and scan_id in tasks:
        return tasks[scan_id].summary
    return {'total_scans': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

@app.route('/')
def home():
    summary = get_latest_summary()
    return render_template('dashboard.html', summary=summary)

@app.route('/dashboard')
def dashboard():
    summary = get_latest_summary()
    return render_template('dashboard.html', summary=summary)

@app.route('/scan', methods=['GET'])
def scan():
    return render_template('scan.html')

@app.route('/api/start_scan', methods=['POST'])
def api_start_scan():
    data = request.get_json()
    target_url = data.get('target_url')
    scan_type = data.get('scan_type', 'quick')
    if not target_url:
        return jsonify({'error': 'Target URL required'}), 400
    # Clean up previous reports for this session
    old_scan_id = session.get('scan_id')
    if old_scan_id and old_scan_id in tasks:
        job = tasks[old_scan_id]
        for path in [job.html_report_path, job.pdf_report_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
        del tasks[old_scan_id]
    scan_id = str(uuid.uuid4())
    job = ScanJob(target_url, scan_type, scan_id)
    t = threading.Thread(target=scan_with_progress, args=(job,))
    job.thread = t
    t.start()
    tasks[scan_id] = job
    session['scan_id'] = scan_id
    return jsonify({'scan_id': scan_id})

@app.route('/api/scan_status')
def api_scan_status():
    scan_id = session.get('scan_id')
    if not scan_id or scan_id not in tasks:
        return jsonify({'error': 'No scan found'}), 404
    job = tasks[scan_id]
    return jsonify({
        'progress': job.progress,
        'current_test': job.current_test,
        'done': job.done,
        'status': job.status,
        'error': job.error,
        'results': job.results,
        'summary': job.summary
    })

@app.route('/download/<report_type>')
def download(report_type):
    scan_id = session.get('scan_id')
    if not scan_id or scan_id not in tasks:
        abort(404)
    job = tasks[scan_id]
    if report_type == 'html':
        path = job.html_report_path
    elif report_type == 'pdf':
        path = job.pdf_report_path
    else:
        return "Invalid report type", 400
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True)

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/abort_scan', methods=['POST'])
def abort_scan():
    scan_id = session.get('scan_id')
    if scan_id and scan_id in tasks:
        tasks[scan_id].abort_event.set()
        return jsonify({'status': 'aborted'})
    return jsonify({'status': 'no_scan'}), 400

if __name__ == '__main__':
    # Get port from environment variable (Render sets PORT)
    port = int(os.environ.get('PORT', 5000))
    # Only use debug mode in development
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug) 