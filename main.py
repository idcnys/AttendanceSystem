from flask import Flask, render_template, request, session, redirect,abort
from flask_session import Session  # For server-side session management
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os
import socket
import shutil

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"  # Use filesystem-based sessions
Session(app)

ADMIN_IPS = []  

def get_present_ips():
    # returns all ips that has responded to the form
    with open('present_ips.txt', 'r') as f:
        return set(f.read().strip().split())
    

def add_present_ip(ip):
    with open('present_ips.txt', 'a') as f:
        f.write(ip+'\n')

def admin_ip_required(f):
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr
        
        # For debugging (prints the connecting IP)
        print(f"Connection attempt from IP: {client_ip}")
        
        if client_ip not in ADMIN_IPS:
            abort(403, description="Access denied - Admin only")  # Forbidden
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        ADMIN_IPS.append(local_ip)
        s.close()
        return local_ip
    except Exception as e:
        print(f"Could not determine local IP: {e}")
        return "0.0.0.0"

users = {
    "2403121": "MD.TAUSIF AL SAHAD",
    "2403122": "MOST. UMME KULSUM",
    "2403123": "MD AMINUL ISLAM SIFAT",
    "2403124": "YASIR ARAFAT",
    "2403125": "DEWAN ABID HASAN",
    "2403126": "AFRA TAHSIN ANIKA",
    "2403127": "SHADMAN AHMED",
    "2403128": "KHUSHBO NAHID",
    "2403129": "SUMON MAJUMDER",
    "2403130": "MD. ABDUL MUKIT",
    "2403131": "ATHAI DEY",
    "2403132": "TASNUVA TABASSUM AMY",
    "2403133": "SHARIQUL ISLAM",
    "2403134": "URBOSHI MAHMUD",
    "2403135": "MD SHADHIN ALI",
    "2403136": "PRANTIK PAUL",
    "2403137": "AFTAB UDDIN",
    "2403138": "ABDULLAH AL BAKI SIFAT",
    "2403139": "SUJOY RABIDAS",
    "2403140": "TASAQUF AHNAF",
    "2403141": "MD SAJID AHMED",
    "2403142": "BITTO SAHA",
    "2403143": "MD TASDID HOSSAIN ANTOR",
    "2403144": "IMRAN KABIR FAHAD",
    "2403145": "MD.NAZMUS SAQUIB SINAN",
    "2403146": "MD RABIB REHMAN",
    "2403147": "MD. MIRAJUL ISLAM",
    "2403148": "MD. SAMIUL ISLAM",
    "2403149": "AREFIN NOUSED RATUL",
    "2403150": "SUPRIO ROY CHOWDHURY",
    "2403151": "SHAFAYET HOSSAIN SHUVO",
    "2403152": "MD. TANVIR CHOWDHURY",
    "2403153": "MA SHIBLI SADIK SIHAB",
    "2403154": "MD. MORCHHALIN ALAM AMIO",
    "2403155": "ARNOB BENEDICT TUDU",
    "2403156": "MD. SHOYKOT MOLLA",
    "2403157": "MD.TAHMIM ULLAH",
    "2403158": "MD. SAROAR JAHAN TIUS",
    "2403159": "TAFSIRUL AHMED AZAN",
    "2403160": "NILAY PAUL PARTHA",
    "2403161": "MD. FAZLA HASSAN RABBI",
    "2403162": "SALMAN AHMED SABBIR",
    "2403163": "MD TANVIR AHMED",
    "2403164": "MOINUDDIN KABIR",
    "2403165": "AVIJET CHAKRABORTY",
    "2403166": "MD. SAMI SADIK",
    "2403167": "MD.MEHEDI HASAN",
    "2403168": "MD.TASNIMUL HASAN",
    "2403169": "MD. MUBINUR RAHMAN",
    "2403170": "ESIKA TANZUM YAME",
    "2403171": "MD. SAZEDUL ISLAM SUNNY",
    "2403172": "MD FAZLE RABBI",
    "2403173": "SAYEM BIN SALIM",
    "2403174": "MD. ERAM OHID",
    "2403175": "SARA ARPA",
    "2403176": "JANNATUL MAWA TANHA",
    "2403177": "MD.SAHARIAR JOY",
    "2403178": "ANUPAM ANJUM SHAHITYA",
    "2403179": "FARDIN BIN ASLAM NUMAN",
    "2403180": "A Q M MAHDI HAQUE"
}

@app.route('/')
def home():
    client_ip = request.remote_addr
    #for those chalak public jara cache clear kore abar attempt korbe
    if client_ip in get_present_ips():
        return "Error: You have already submitted your attendance from this device", 403
    
    # valo manush kintu niyot kharap
    if session.get('restricted'):
        return "Error: Access to home page restricted for this session", 403
    
    who = ''
    which = ''
    duration = ''
    
    with open('who.txt', 'r') as f:
        who = f.read().strip()
    with open('which.txt', 'r') as f:
        which = f.read().strip()
    
    return render_template("index.html", tname=who, subject=which, duration=duration)

@app.route('/create')
@admin_ip_required
def create():
    return render_template("create.html")

@app.route("/initiate", methods=['POST'])
def initiate():
    teacherName = request.form.get("tname")
    subject = request.form.get("sub")
    duration = request.form.get("length")
    
    
    #updating the session details
    with open('who.txt', 'w') as f:
        f.write(teacherName)
    with open('which.txt', 'w') as f:
        f.write(subject)
    
    
    #clearing prev data, present roll & ips
    with open('present.txt', 'w') as f:
        f.write('')
    with open('present_ips.txt', 'w') as f:
        f.write('')
    
    
    
    #allowing restricted users if the ip is same as before, we wont do that though
    session.clear()
    if os.path.exists("flask_session"):  # Replace with your folder name
        shutil.rmtree("flask_session")
    return "Successfully created!"

@app.route("/render")
@admin_ip_required
def rendPdf():
    try:
        with open('who.txt', 'r') as f:
            teacher_name = f.read().strip()
        with open('which.txt', 'r') as f:
            subject = f.read().strip()
    except FileNotFoundError:
        pass

    
    try:
        with open('present.txt', 'r') as f:
            present_rolls = f.read().strip().split()
    except FileNotFoundError:
        present_rolls = []

    
    current_datetime = datetime.now()
    date_str = current_datetime.strftime("%d-%m-%Y")
    time_str = current_datetime.strftime("%H:%M:%S")

    
    total_students = len(users)
    present_count = len(present_rolls)
    attendance_percentage = (present_count / total_students * 100) if total_students > 0 else 0

    if os.path.exists(os.path.join(os.getcwd(), "static/attendance.pdf")):
        os.remove(os.path.join(os.getcwd(), "static/attendance.pdf"))
    
    pdf_file = "static/attendance.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    
    title = Paragraph(f"{subject} Attendance Sheet {date_str}", styles['Heading3'])
    elements.append(title)
    elements.append(Spacer(1, 12))  

    
    header = Paragraph(
        f"Teacher: <b>{teacher_name}</b> &nbsp;&nbsp;Subject: <b>{subject}</b>&nbsp;&nbsp;Date: <b>{date_str}</b>&nbsp;&nbsp;Time: {time_str}",
        styles['Normal']
    )
    elements.append(header)
    elements.append(Spacer(1, 12))  

    
    data = [["Roll", "Name", "Status"]]
    for roll, name in sorted(users.items(), key=lambda x: x[0]):
        status = "Present" if roll in present_rolls else "Absent"
        data.append([roll, name, status])

    
    table = Table(data)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), 
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), 
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), 
        ('FONTSIZE', (0, 0), (-1, 0), 12), 
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12), 
        ('GRID', (0, 0), (-1, -1), 1, colors.black), 
    ])

    
    for row_idx, row in enumerate(data[1:], start=1):  
        status = row[2] 
        if status == "Present":
            table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.lightgreen)
        else:  
            table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.lightcoral)

    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 12)) 

    
    percentage_text = Paragraph(
        f"Attendance Percentage: {attendance_percentage:.2f}% ({present_count}/{total_students})",
        styles['Normal']
    )
    elements.append(percentage_text)

    
    doc.build(elements)

    # Reseting who.txt and which.txt
    with open('who.txt', 'w') as f:
        f.write("unknown")
    with open('which.txt', 'w') as f:
        f.write("unknown")

    return "Thanks for using our system. PDF available at <a href='/static/attendance.pdf'>/static/attendance.pdf</a>"

@app.route("/addPresent", methods=['POST'])
def addPresent():
    roll = request.form.get("roll")
    client_ip = request.remote_addr
    
    # jara beshi chalak
    if client_ip in get_present_ips():
        return "Error: You have already submitted your attendance from this device", 400
    
    if roll:
        # Validate roll number
        if roll not in users:
            return "Error: Invalid roll number", 400
        with open("present.txt", "r") as f:
            existing_rolls = f.read().split()
            if roll in existing_rolls:
                return "Error: Roll number already exists", 400
            with open("present.txt", "a") as f:
                f.write(f"{roll} ")
                add_present_ip(client_ip)  # two factor safety
                session['restricted'] = True  # vai r access pabe na xD
                return render_template("congo.html")
    else:
        return "Error: No roll number provided", 400
if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"\n Welcome to attendance system,\n\n Users portal: \033[32mhttp://{local_ip}:5000\033[0m from other devices on your network\n Create Sheet: \033[32mhttp://{local_ip}:5000/create\033[0m\n Render PDF: \033[32mhttp://{local_ip}:5000/render\033[0m\n\n\n All rights reserved by \033[36mBITTO SAHA a.k.a dcnys\033[0m\n\n")
    app.run(host=local_ip, port=5000, debug=True)
    
