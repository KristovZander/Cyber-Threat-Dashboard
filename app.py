from flask import Flask, render_template, request, make_response
from utils.threat_api import check_ip_virustotal, check_ip_abuseipdb
from utils.db import save_scan, get_recent_scans
from xhtml2pdf import pisa
from io import BytesIO
import os
from dotenv import load_dotenv
import datetime
import matplotlib.pyplot as plt
import os
from io import BytesIO
from PIL import Image
import base64

#from utils.db import clear_all_scans

load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    vt_result = None
    abuse_result = None
    ip = ""

    if request.method == "POST":
        ip = request.form.get("ip")
        if ip:
            vt_result = check_ip_virustotal(ip)
            abuse_result = check_ip_abuseipdb(ip)
            save_scan(ip, vt_result, abuse_result)

    scans = get_recent_scans()
    return render_template("index.html", ip=ip, vt_result=vt_result, abuse_result=abuse_result, scans=scans)

@app.route("/report")
def generate_pdf():
    ip = request.args.get("ip")
    vt_result = eval(request.args.get("vt"))
    abuse_result = eval(request.args.get("abuse"))
    now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")

    # Generate VirusTotal Pie Chart
    vt_labels = ['Malicious', 'Suspicious', 'Undetected', 'Harmless', 'Timeout']
    vt_values = [
        vt_result.get('malicious', 0),
        vt_result.get('suspicious', 0),
        vt_result.get('undetected', 0),
        vt_result.get('harmless', 0),
        vt_result.get('timeout', 0)
    ]

    plt.figure(figsize=(4, 4))
    plt.pie(vt_values, labels=vt_labels, autopct='%1.1f%%', colors=['#ef4444', '#f97316', '#a3a3a3', '#4ade80', '#60a5fa'])
    plt.title('VirusTotal Threat Distribution')
    vt_img_path = os.path.join("static", "vt_chart.png")
    plt.savefig(vt_img_path)
    plt.close()

    # Generate AbuseIPDB Bar Chart
    from utils.db import get_recent_scans
    scans = get_recent_scans(limit=5)
    ips = [scan["ip"] for scan in scans]
    scores = [scan["abuse_ipdb"]["abuseConfidenceScore"] for scan in scans]

    plt.figure(figsize=(6, 3))
    plt.bar(ips, scores, color="#f87171")
    plt.title("AbuseIPDB Score (Last 5 Scans)")
    plt.ylabel("Abuse Score")
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.tight_layout()
    abuse_img_path = os.path.join("static", "abuse_chart.png")
    plt.savefig(abuse_img_path)
    plt.close()

    # Pass image paths to the template
    html = render_template("report_template.html", ip=ip, vt_result=vt_result, abuse_result=abuse_result, date=now,
                           vt_chart=vt_img_path, abuse_chart=abuse_img_path)

    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    pdf.seek(0)

    response = make_response(pdf.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={ip}_report.pdf"
    return response


'''@app.route("/clear")
def clear_data():
    clear_all_scans()
    return "✅ All scans cleared from database.'''

if __name__ == "__main__":
    app.run(debug=True)
