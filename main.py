"""
================================================================================
BRUTE FORCE DETECTION SYSTEM v2.2
================================================================================
Complete Working Version - Generates PDF reports matching exact format
================================================================================
"""

from datetime import datetime, timedelta
import random
import time
import smtplib
import tkinter as tk
from tkinter import ttk, messagebox
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import threading
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib
matplotlib.use('TkAgg')


class AdvancedBruteForceDetector:
    
    def __init__(self, window):
        self.window = window
        self.window.title("🛡️ Advanced Brute Force Detection System v2.2")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2c3e50')
        
        self.base_failed_limit = 3
        self.time_window = 60
        self.adaptive_mode = True
        self.honeypot_active = True
        
        self.login_attempts = []
        self.blocked_ips = set()
        self.ip_attempt_count = defaultdict(int)
        self.ip_failure_patterns = defaultdict(list)
        self.attack_statistics = {
            'total_attacks': 0,
            'unique_attackers': set(),
            'common_passwords': defaultdict(int)
        }
        
        self.honeypot_users = {
            'admin_hidden': 'fake_password_123',
            'root_backup': 'temp_pass',
            'superuser': 'secret123',
            'administrator': 'admin123'
        }
        
        # ===== EMAIL CONFIG =====
        self.email_enabled = True
        self.sender_email = "sreediyasanjith26@gmail.com"
        self.receiver_email = "seemasanju.ss@gmail.com"
        self.email_password = "ykgo tnoj vcyo ymuj"  # App password with spaces
        
        self.simulation_active = False
        self.simulation_stop = False
        
        self.load_data()
        self.initialize_files()
        self.setup_gui()
        self.add_demo_data()
    
    # ========================================================================
    # INITIALIZATION
    # ========================================================================
    
    def add_demo_data(self):
        if len(self.login_attempts) == 0:
            demo_ips = ['192.168.1.100', '192.168.1.101', '10.0.0.50', '192.168.1.102']
            for i in range(15):
                ip = random.choice(demo_ips)
                status = random.choice(['SUCCESS', 'FAIL', 'FAIL', 'SUCCESS'])
                self.login_attempts.append({
                    "ip": ip, "status": status,
                    "time": datetime.now() - timedelta(minutes=random.randint(1, 30)),
                    "username": f"demo_user{i}",
                    "password": "demo123" if status == "FAIL" else ""
                })
                self.ip_attempt_count[ip] += 1
                if status == "FAIL":
                    self.attack_statistics['common_passwords']['demo123'] += 1
            self.log_message("📊 Demo data loaded", "INFO")
            self.update_dashboard()
            self.update_graphs()
    
    def initialize_files(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists('reports'):
            os.makedirs('reports')
        for file in ['data/logs.txt', 'data/blocked_ips.txt', 'data/system_data.json']:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    if file.endswith('.json'):
                        json.dump({}, f)
                    else:
                        f.write('')
    
    # ========================================================================
    # GUI SETUP
    # ========================================================================
    
    def setup_gui(self):
        style = ttk.Style()
        style.theme_use('clam')
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.main_tab = ttk.Frame(notebook)
        notebook.add(self.main_tab, text="📊 Dashboard")
        self.setup_dashboard()
        
        self.viz_tab = ttk.Frame(notebook)
        notebook.add(self.viz_tab, text="📈 Attack Analytics")
        self.setup_visualization()
        
        self.honeypot_tab = ttk.Frame(notebook)
        notebook.add(self.honeypot_tab, text="🍯 Honeypot Console")
        self.setup_honeypot()
        
        self.threat_tab = ttk.Frame(notebook)
        notebook.add(self.threat_tab, text="🛡️ Threat Intel")
        self.setup_threat_intel()
        
        self.settings_tab = ttk.Frame(notebook)
        notebook.add(self.settings_tab, text="⚙️ Settings")
        self.setup_settings()
        
        self.update_dashboard()
    
    def setup_dashboard(self):
        control_frame = tk.Frame(self.main_tab, bg='#ecf0f1', relief='raised', bd=2)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        buttons = [
            ("🛑 STOP", self.stop_simulation, '#e74c3c'),
            ("🚀 Attack", self.start_attack_simulation, '#c0392b'),
            ("👤 Normal", self.start_normal_simulation, '#3498db'),
            ("🗑️ Clear", self.clear_logs, '#95a5a6'),
            ("📄 Export PDF", self.export_and_email_pdf, '#e67e22'),
            ("🍯 Honeypot", self.test_honeypot, '#9b59b6'),
            ("📧 Test Email", self.send_test_email, '#1abc9c'),
        ]
        for text, cmd, color in buttons:
            tk.Button(control_frame, text=text, command=cmd, bg=color, fg='white',
                     font=('Arial', 10, 'bold'), padx=15, pady=8).pack(side='left', padx=5, pady=8)
        
        stats_frame = tk.LabelFrame(self.main_tab, text="📊 Real-time Statistics",
                                    font=('Arial', 12, 'bold'), bg='white')
        stats_frame.pack(fill='x', padx=10, pady=10)
        self.stats_text = tk.Text(stats_frame, height=10, font=('Courier', 10), bg='white')
        self.stats_text.pack(padx=10, pady=10)
        
        middle_frame = tk.Frame(self.main_tab, bg='#ecf0f1')
        middle_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        blocked_frame = tk.LabelFrame(middle_frame, text="🚫 Blocked IPs",
                                      font=('Arial', 12, 'bold'), bg='white')
        blocked_frame.pack(side='left', fill='both', expand=True, padx=5)
        self.blocked_listbox = tk.Listbox(blocked_frame, height=15, font=('Courier', 10), bg='#ffe6e6')
        self.blocked_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        log_frame = tk.LabelFrame(middle_frame, text="📝 Live Attack Log",
                                  font=('Arial', 12, 'bold'), bg='white')
        log_frame.pack(side='right', fill='both', expand=True, padx=5)
        self.log_text = tk.Text(log_frame, height=15, font=('Courier', 9), bg='#f8f9fa', wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def setup_visualization(self):
        self.fig = plt.Figure(figsize=(12, 8), dpi=100)
        self.fig.subplots_adjust(hspace=0.4, wspace=0.3)
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_tab)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        tk.Button(self.viz_tab, text="🔄 Refresh", command=self.update_graphs,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
        self.update_graphs()
    
    def setup_honeypot(self):
        monitor_frame = tk.LabelFrame(self.honeypot_tab, text="🍯 Honeypot Activity",
                                      font=('Arial', 12, 'bold'), bg='white')
        monitor_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.honeypot_log = tk.Text(monitor_frame, height=12, font=('Courier', 9),
                                    bg='#fff3e0', wrap='word')
        self.honeypot_log.pack(fill='both', expand=True, padx=10, pady=10)
        self.honeypot_log.insert(tk.END, "🍯 Honeypot Active - Waiting for attackers...\n")
        
        cred_frame = tk.LabelFrame(self.honeypot_tab, text="🎣 Decoy Credentials",
                                   font=('Arial', 12, 'bold'), bg='white')
        cred_frame.pack(fill='x', padx=10, pady=10)
        cred_text = "\n".join([f"👤 {user} | 🔑 {pwd}" for user, pwd in self.honeypot_users.items()])
        tk.Label(cred_frame, text=cred_text, font=('Courier', 10), bg='#ffffcc', pady=10).pack(pady=10)
        tk.Label(cred_frame, text="⚠️ These are FAKE credentials!",
                font=('Arial', 10, 'bold'), fg='red', bg='#ffffcc').pack(pady=5)
    
    def setup_threat_intel(self):
        intel_frame = tk.Frame(self.threat_tab, bg='#ecf0f1')
        intel_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        pattern_frame = tk.LabelFrame(intel_frame, text="🔍 Attack Patterns",
                                      font=('Arial', 12, 'bold'), bg='white')
        pattern_frame.pack(fill='x', pady=5)
        self.pattern_text = tk.Text(pattern_frame, height=6, font=('Courier', 9), bg='#e8f4f8')
        self.pattern_text.pack(fill='x', padx=10, pady=10)
        
        password_frame = tk.LabelFrame(intel_frame, text="🔐 Top Passwords",
                                       font=('Arial', 12, 'bold'), bg='white')
        password_frame.pack(fill='both', expand=True, pady=5)
        self.password_listbox = tk.Listbox(password_frame, height=8, font=('Courier', 10))
        self.password_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        timeline_frame = tk.LabelFrame(intel_frame, text="⏰ Attack Timeline",
                                       font=('Arial', 12, 'bold'), bg='white')
        timeline_frame.pack(fill='x', pady=5)
        self.timeline_text = tk.Text(timeline_frame, height=4, font=('Courier', 9), bg='#e8f4f8')
        self.timeline_text.pack(fill='x', padx=10, pady=10)
    
    def setup_settings(self):
        settings_frame = tk.Frame(self.settings_tab, bg='#ecf0f1')
        settings_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        email_frame = tk.LabelFrame(settings_frame, text="📧 Email Configuration",
                                    font=('Arial', 12, 'bold'), bg='white')
        email_frame.pack(fill='x', pady=10)
        
        self.email_enabled_var = tk.BooleanVar(value=self.email_enabled)
        tk.Checkbutton(email_frame, text="Enable Email Alerts",
                      variable=self.email_enabled_var, bg='white').pack(pady=5)
        
        tk.Label(email_frame, text="Sender Email:", bg='white').pack(pady=2)
        self.sender_entry = tk.Entry(email_frame, width=40)
        self.sender_entry.insert(0, self.sender_email)
        self.sender_entry.pack(pady=2)
        
        tk.Label(email_frame, text="Receiver Email:", bg='white').pack(pady=2)
        self.receiver_entry = tk.Entry(email_frame, width=40)
        self.receiver_entry.insert(0, self.receiver_email)
        self.receiver_entry.pack(pady=2)
        
        tk.Label(email_frame, text="App Password:", bg='white').pack(pady=2)
        self.password_entry = tk.Entry(email_frame, width=40, show="*")
        self.password_entry.insert(0, self.email_password)
        self.password_entry.pack(pady=2)
        
        tk.Button(settings_frame, text="💾 Save Settings", command=self.save_settings,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=10).pack(pady=20)
    
    # ========================================================================
    # CORE LOGIC
    # ========================================================================
    
    def save_settings(self):
        self.email_enabled = self.email_enabled_var.get()
        self.sender_email = self.sender_entry.get()
        self.receiver_email = self.receiver_entry.get()
        self.email_password = self.password_entry.get()
        messagebox.showinfo("Success", "Settings saved!")
    
    def adaptive_threshold(self, ip):
        if not self.adaptive_mode:
            return self.base_failed_limit
        if ip in self.blocked_ips:
            return 2
        if 9 <= datetime.now().hour <= 17:
            return self.base_failed_limit + 1
        if len(self.ip_failure_patterns[ip]) > 10:
            return max(1, self.base_failed_limit - 1)
        return self.base_failed_limit
    
    def honeypot_check(self, username, password, ip):
        if not self.honeypot_active:
            return False
        if username in self.honeypot_users:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            alert = f"\n{'='*60}\n🚨 HONEYPOT TRIGGERED!\nTime: {ts}\nIP: {ip}\nAttempted: {username}:{password}\nAction: AUTO-BLOCKED\n{'='*60}\n\n"
            self.honeypot_log.insert(tk.END, alert)
            self.honeypot_log.see(tk.END)
            self.log_message(f"HONEYPOT TRIGGERED! IP: {ip}", "CRITICAL")
            if ip not in self.blocked_ips:
                self.blocked_ips.add(ip)
                self.save_data()
                self.update_dashboard()
            return True
        return False
    
    def detect_coordinated_attack(self):
        tw = datetime.now() - timedelta(seconds=30)
        recent = [a for a in self.login_attempts if a['time'] > tw and a['status'] == 'FAIL']
        if len(recent) > 20:
            uips = len(set(a['ip'] for a in recent))
            if uips > 5:
                self.log_message(f"COORDINATED ATTACK! {len(recent)} attempts from {uips} IPs", "CRITICAL")
    
    def login(self, ip, status, username="user", password=""):
        if ip in self.blocked_ips:
            self.log_message(f"BLOCKED IP: {ip}", "WARNING")
            return False
        if self.honeypot_active and self.honeypot_check(username, password, ip):
            return False
        
        now = datetime.now()
        self.login_attempts.append({
            "ip": ip, "status": status, "time": now,
            "username": username, "password": password if status == "FAIL" else ""
        })
        self.ip_attempt_count[ip] += 1
        
        with open("data/logs.txt", "a") as f:
            f.write(f"{ip},{status},{username},{now},{password}\n")
        
        if status == "FAIL":
            self.ip_failure_patterns[ip].append(now)
            if password:
                self.attack_statistics['common_passwords'][password] += 1
            
            threshold = self.adaptive_threshold(ip)
            recent = len([a for a in self.login_attempts
                          if a['ip'] == ip and a['status'] == 'FAIL'
                          and now - a['time'] <= timedelta(seconds=self.time_window)])
            
            if recent >= threshold:
                self.block_ip(ip)
                self.attack_statistics['total_attacks'] += 1
                self.attack_statistics['unique_attackers'].add(ip)
        
        self.save_data()
        self.log_message(f"Login -> {ip} | {status} | User: {username}")
        self.update_dashboard()
        self.detect_coordinated_attack()
        return True
    
    def block_ip(self, ip):
        if ip not in self.blocked_ips:
            self.blocked_ips.add(ip)
            with open("data/blocked_ips.txt", "a") as f:
                f.write(f"{ip},{datetime.now()}\n")
            self.log_message(f"IP BLOCKED: {ip}", "CRITICAL")
            self.update_dashboard()
    
    # ========================================================================
    # PDF REPORT - EXACT FORMAT MATCHING YOUR REFERENCE
    # ========================================================================
    
    def generate_pdf_report(self, save_path):
        """
        Generates PDF report in EXACT format matching reference:
        1. EXECUTIVE SUMMARY
        2. ATTACK STATISTICS
        3. TOP ATTACKING IP ADDRESSES
        4. TOP ATTACK PASSWORDS
        5. BLOCKED IP ADDRESSES
        6. SECURITY RECOMMENDATIONS
        7. CONCLUSION
        """
        try:
            doc = SimpleDocTemplate(
                save_path,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            section_heading = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading1'],
                fontSize=14,
                textColor=colors.HexColor('#1a1a2e'),
                spaceBefore=15,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            
            cell_style = styles['Normal']
            
            # ============================================================
            # SECTION 1: EXECUTIVE SUMMARY
            # ============================================================
            story.append(Paragraph("1. EXECUTIVE SUMMARY", section_heading))
            
            total = len(self.login_attempts)
            failed = len([a for a in self.login_attempts if a['status'] == 'FAIL'])
            success = total - failed
            blocked = len(self.blocked_ips)
            attack_rate = (failed / total * 100) if total > 0 else 0
            
            summary_data = [
                ["Metric", "Value", "Status"],
                ["Total Login Attempts", str(total), "Monitored"],
                ["Failed Attempts", str(failed), "⚠ Attack Detected" if failed > 0 else "✓ Normal"],
                ["Successful Attempts", str(success), "✓ Legitimate Users"],
                ["Blocked IPs", str(blocked), "✓ Blocked" if blocked > 0 else "No Threats"],
                ["Attack Rate", f"{attack_rate:.1f}%", "⚠ High" if attack_rate > 30 else "✓ Low"],
                ["Adaptive Mode", "Enabled" if self.adaptive_mode else "Disabled", "Active"],
                ["Honeypot Status", "Active" if self.honeypot_active else "Inactive", "Active"],
            ]
            
            t1 = Table(summary_data, colWidths=[2.2*inch, 1.8*inch, 2.0*inch])
            t1.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t1)
            story.append(Spacer(1, 0.2*inch))
            
            # ============================================================
            # SECTION 2: ATTACK STATISTICS
            # ============================================================
            story.append(Paragraph("2. ATTACK STATISTICS", section_heading))
            
            attacks = [a for a in self.login_attempts if a['status'] == 'FAIL']
            if attacks:
                first_attack = attacks[0]['time']
                last_attack = attacks[-1]['time']
                duration = last_attack - first_attack
                
                stats_data = [
                    ["Parameter", "Value"],
                    ["Attack Start Time", first_attack.strftime('%Y-%m-%d %H:%M:%S')],
                    ["Attack End Time", last_attack.strftime('%Y-%m-%d %H:%M:%S')],
                    ["Total Attack Duration", str(duration)],
                    ["Total Attacks Detected", str(len(attacks))],
                    ["Attack Frequency", f"{len(attacks)/max(0.1, duration.total_seconds())*60:.2f} per minute"],
                    ["Unique Attackers", str(len(self.attack_statistics['unique_attackers']))],
                ]
            else:
                stats_data = [
                    ["Parameter", "Value"],
                    ["Attack Start Time", "No attacks detected"],
                    ["Attack End Time", "N/A"],
                    ["Total Attack Duration", "N/A"],
                    ["Total Attacks Detected", "0"],
                    ["Attack Frequency", "0 per minute"],
                    ["Unique Attackers", "0"],
                ]
            
            t2 = Table(stats_data, colWidths=[2.8*inch, 3.2*inch])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t2)
            story.append(Spacer(1, 0.2*inch))
            
            # ============================================================
            # SECTION 3: TOP ATTACKING IP ADDRESSES
            # ============================================================
            story.append(Paragraph("3. TOP ATTACKING IP ADDRESSES", section_heading))
            
            if self.ip_attempt_count:
                top_ips = sorted(self.ip_attempt_count.items(), key=lambda x: x[1], reverse=True)[:10]
                ip_data = [["IP Address", "Attempt Count", "Status"]]
                for ip, count in top_ips:
                    status = "Blocked" if ip in self.blocked_ips else "Active"
                    ip_data.append([ip, str(count), status])
            else:
                ip_data = [["IP Address", "Attempt Count", "Status"],
                           ["No attacking IPs detected", "-", "-"]]
            
            t3 = Table(ip_data, colWidths=[2.2*inch, 1.8*inch, 2.0*inch])
            t3.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t3)
            story.append(Spacer(1, 0.2*inch))
            
            # ============================================================
            # SECTION 4: TOP ATTACK PASSWORDS
            # ============================================================
            story.append(Paragraph("4. TOP ATTACK PASSWORDS", section_heading))
            
            if self.attack_statistics['common_passwords']:
                top_pwds = sorted(self.attack_statistics['common_passwords'].items(),
                                  key=lambda x: x[1], reverse=True)[:10]
                pwd_data = [["Password", "Attempts", "Risk Level"]]
                for pwd, count in top_pwds:
                    risk = "Critical" if count > 5 else "High" if count > 2 else "Medium"
                    pwd_data.append([pwd, str(count), risk])
            else:
                pwd_data = [["Password", "Attempts", "Risk Level"],
                            ["No passwords recorded", "-", "-"]]
            
            t4 = Table(pwd_data, colWidths=[2.2*inch, 1.8*inch, 2.0*inch])
            t4.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e67e22')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t4)
            story.append(Spacer(1, 0.2*inch))
            
            # ============================================================
            # SECTION 5: BLOCKED IP ADDRESSES
            # ============================================================
            story.append(Paragraph("5. BLOCKED IP ADDRESSES", section_heading))
            
            if self.blocked_ips:
                blocked_data = [["IP Address", "Status", "Action Taken"]]
                for ip in list(self.blocked_ips)[:20]:
                    blocked_data.append([ip, "Blocked", "Auto-blocked by system"])
            else:
                blocked_data = [["IP Address", "Status", "Action Taken"],
                                ["No IPs have been blocked", "-", "-"]]
            
            t5 = Table(blocked_data, colWidths=[2.2*inch, 1.8*inch, 2.0*inch])
            t5.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t5)
            story.append(Spacer(1, 0.2*inch))
            
            # ============================================================
            # SECTION 6: SECURITY RECOMMENDATIONS
            # ============================================================
            story.append(Paragraph("6. SECURITY RECOMMENDATIONS", section_heading))
            
            recommendations = [
                "• Enable Multi-Factor Authentication (MFA) for all user accounts",
                "• Implement password complexity requirements to prevent weak passwords",
                "• Consider reducing the time window for detection to 30 seconds",
                "• Review and update blocked IPs list regularly",
                "• Conduct regular security awareness training for employees",
            ]
            
            for rec in recommendations:
                story.append(Paragraph(rec, styles['Normal']))
                story.append(Spacer(1, 0.08*inch))
            
            story.append(Spacer(1, 0.2*inch))
            
            # ============================================================
            # SECTION 7: CONCLUSION
            # ============================================================
            story.append(Paragraph("7. CONCLUSION", section_heading))
            
            conclusion = (
                f"The Brute Force Detection System has successfully monitored and analyzed "
                f"{total} login attempts, detecting {failed} potential brute force attacks. "
                f"The system automatically blocked {blocked} suspicious IP addresses, preventing "
                f"unauthorized access attempts. This report has been automatically generated "
                f"and sent to the system administrator."
            )
            story.append(Paragraph(conclusion, styles['Normal']))
            
            # Build the PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            self.log_message(f"PDF generation failed: {str(e)}", "WARNING")
            return False
    
    # ========================================================================
    # EMAIL
    # ========================================================================
    
    def send_email(self, subject, body, attachment_path=None):
        if not self.email_enabled:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    f'attachment; filename={os.path.basename(attachment_path)}')
                    msg.attach(part)
            
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.email_password)
            server.send_message(msg)
            server.quit()
            self.log_message("Email sent successfully", "INFO")
            return True
        except Exception as e:
            self.log_message(f"Email failed: {str(e)}", "WARNING")
            print(f"Email error: {e}")
            return False
    
    def send_test_email(self):
        if not self.email_enabled:
            messagebox.showwarning("Email Disabled", "Enable email in Settings first!")
            return
        
        subject = "Test - Brute Force Detection System"
        body = f"Test email\nTime: {datetime.now()}\nSystem: Active"
        
        if self.send_email(subject, body):
            messagebox.showinfo("Success", "Test email sent!")
        else:
            messagebox.showerror("Error", "Failed to send. Check settings!")
    
    def export_and_email_pdf(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"Security_Report_{timestamp}.pdf"
        pdf_path = os.path.join(desktop_path, pdf_filename)
        
        self.log_message("📄 Generating PDF...", "INFO")
        
        if self.generate_pdf_report(pdf_path):
            self.log_message(f"✅ PDF saved: {pdf_path}", "INFO")
            
            if self.email_enabled:
                self.log_message("📧 Sending email...", "INFO")
                subject = f"Security Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                body = f"Security report attached.\nTotal attempts: {len(self.login_attempts)}\nBlocked IPs: {len(self.blocked_ips)}"
                
                if self.send_email(subject, body, pdf_path):
                    messagebox.showinfo("Success", f"PDF saved & emailed!\n{pdf_path}")
                else:
                    messagebox.showwarning("Partial", f"PDF saved but email failed.\n{pdf_path}")
            else:
                messagebox.showinfo("Success", f"PDF saved!\n{pdf_path}")
        else:
            messagebox.showerror("Error", "PDF generation failed!")
    
    # ========================================================================
    # SIMULATION
    # ========================================================================
    
    def stop_simulation(self):
        if self.simulation_active:
            self.simulation_stop = True
            self.log_message("🛑 Stopping...", "WARNING")
    
    def test_honeypot(self):
        self.login("192.168.1.99", "FAIL", "admin_hidden", "fake_password_123")
        self.log_message("🍯 Honeypot tested!", "INFO")
    
    def start_attack_simulation(self):
        if self.simulation_active:
            messagebox.showwarning("Running", "Stop current simulation first!")
            return
        threading.Thread(target=self.simulate_attack, daemon=True).start()
    
    def start_normal_simulation(self):
        if self.simulation_active:
            messagebox.showwarning("Running", "Stop current simulation first!")
            return
        threading.Thread(target=self.simulate_normal, daemon=True).start()
    
    def simulate_attack(self):
        self.simulation_active = True
        self.simulation_stop = False
        self.log_message("🚨 ATTACK SIMULATION STARTED!", "CRITICAL")
        
        attacker_ips = [f"192.168.1.{i}" for i in range(10, 20)]
        passwords = ['admin123', 'password', '123456', 'root', 'qwerty']
        
        for i in range(30):
            if self.simulation_stop:
                break
            ip = random.choice(attacker_ips)
            self.login(ip, "FAIL", f"user{i}", random.choice(passwords))
            time.sleep(random.uniform(0.1, 0.5))
        
        if not self.simulation_stop:
            self.log_message("✅ Attack simulation completed!", "INFO")
        self.simulation_active = False
    
    def simulate_normal(self):
        self.simulation_active = True
        self.simulation_stop = False
        self.log_message("👤 NORMAL SIMULATION STARTED!", "INFO")
        
        normal_ips = [f"10.0.0.{i}" for i in range(1, 20)]
        
        for i in range(20):
            if self.simulation_stop:
                break
            ip = random.choice(normal_ips)
            status = random.choice(["SUCCESS", "SUCCESS", "FAIL"])
            self.login(ip, status, f"emp{i}", "")
            time.sleep(random.uniform(1, 3))
        
        if not self.simulation_stop:
            self.log_message("✅ Normal simulation completed!", "INFO")
        self.simulation_active = False
    
    # ========================================================================
    # DISPLAY UPDATES
    # ========================================================================
    
    def update_graphs(self):
        if not hasattr(self, 'ax1'):
            return
        
        self.ax1.clear(); self.ax2.clear(); self.ax3.clear(); self.ax4.clear()
        
        times = [a['time'] for a in self.login_attempts if a['status'] == 'FAIL']
        if times:
            self.ax1.hist(times, bins=min(20, len(times)), color='red', alpha=0.7, edgecolor='black')
            self.ax1.set_title('Attack Timeline', fontweight='bold')
        else:
            self.ax1.text(0.5, 0.5, 'No attacks yet', ha='center', va='center', transform=self.ax1.transAxes)
            self.ax1.set_title('Attack Timeline')
        
        if self.ip_attempt_count:
            top_ips = sorted(self.ip_attempt_count.items(), key=lambda x: x[1], reverse=True)[:10]
            ips, counts = zip(*top_ips)
            colors_list = plt.cm.YlOrRd([i/len(ips) for i in range(len(ips))])
            self.ax2.bar(ips, counts, color=colors_list, alpha=0.7, edgecolor='black')
            self.ax2.set_title('Top Attackers', fontweight='bold')
            self.ax2.tick_params(axis='x', rotation=45, labelsize=7)
        else:
            self.ax2.text(0.5, 0.5, 'No data', ha='center', va='center', transform=self.ax2.transAxes)
            self.ax2.set_title('Top Attackers')
        
        success = len([a for a in self.login_attempts if a['status'] == 'SUCCESS'])
        failure = len([a for a in self.login_attempts if a['status'] == 'FAIL'])
        if success + failure > 0:
            self.ax3.pie([success, failure], labels=['Success', 'Failure'],
                        colors=['#2ecc71', '#e74c3c'], autopct='%1.1f%%')
            self.ax3.set_title('Success vs Failure', fontweight='bold')
        else:
            self.ax3.text(0.5, 0.5, 'No data', ha='center', va='center', transform=self.ax3.transAxes)
        
        if len(self.blocked_ips) > 0:
            self.ax4.bar(['Blocked'], [len(self.blocked_ips)], color='#e74c3c', alpha=0.7)
            self.ax4.set_title('Blocked IPs', fontweight='bold')
        else:
            self.ax4.text(0.5, 0.5, 'None blocked', ha='center', va='center', transform=self.ax4.transAxes)
            self.ax4.set_title('Blocked IPs')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_dashboard(self):
        stats = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 SYSTEM STATISTICS                      ║
╠══════════════════════════════════════════════════════════════╣
║ Total Login Attempts:        {len(self.login_attempts):<35} ║
║ Failed Attempts:             {len([a for a in self.login_attempts if a['status'] == 'FAIL']):<35} ║
║ Successful Attempts:         {len([a for a in self.login_attempts if a['status'] == 'SUCCESS']):<35} ║
║ Blocked IPs:                 {len(self.blocked_ips):<35} ║
║ Unique Attackers:            {len(self.attack_statistics['unique_attackers']):<35} ║
║ Total Attacks Detected:      {self.attack_statistics['total_attacks']:<35} ║
║ Adaptive Mode:               {'✅ ON' if self.adaptive_mode else '❌ OFF':<35} ║
║ Honeypot Status:             {'🍯 ACTIVE' if self.honeypot_active else '⭕ INACTIVE':<35} ║
║ Email Alerts:                {'📧 ENABLED' if self.email_enabled else '⭕ DISABLED':<35} ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        if hasattr(self, 'stats_text'):
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats)
        
        if hasattr(self, 'blocked_listbox'):
            self.blocked_listbox.delete(0, tk.END)
            for ip in self.blocked_ips:
                self.blocked_listbox.insert(tk.END, f"🔒 {ip}")
            if not self.blocked_ips:
                self.blocked_listbox.insert(tk.END, "No blocked IPs yet")
        
        self.update_threat_intel()
        self.update_graphs()
    
    def update_threat_intel(self):
        if hasattr(self, 'pattern_text'):
            patterns = "Attack Patterns:\n" + "="*40 + "\n"
            attack_ips = [(ip, len(times)) for ip, times in self.ip_failure_patterns.items() if len(times) > 3]
            if attack_ips:
                for ip, count in attack_ips[:5]:
                    patterns += f"⚠️ {ip}: {count} failures\n"
            else:
                patterns += "No patterns detected\n"
            self.pattern_text.delete(1.0, tk.END)
            self.pattern_text.insert(1.0, patterns)
        
        if hasattr(self, 'password_listbox'):
            self.password_listbox.delete(0, tk.END)
            top_pwds = sorted(self.attack_statistics['common_passwords'].items(),
                            key=lambda x: x[1], reverse=True)[:10]
            if top_pwds:
                for pwd, count in top_pwds:
                    self.password_listbox.insert(tk.END, f"🔑 {pwd}: {count}")
            else:
                self.password_listbox.insert(tk.END, "No passwords recorded")
        
        if hasattr(self, 'timeline_text'):
            attacks = [a for a in self.login_attempts if a['status'] == 'FAIL']
            if attacks:
                first = attacks[0]['time']
                last = attacks[-1]['time']
                duration = last - first
                timeline = f"""
Attack Period: {first.strftime('%H:%M:%S')} to {last.strftime('%H:%M:%S')}
Duration: {duration}
Total: {len(attacks)} attacks
Frequency: {len(attacks)/max(0.1, duration.total_seconds())*60:.2f}/min
"""
                self.timeline_text.delete(1.0, tk.END)
                self.timeline_text.insert(1.0, timeline)
    
    def log_message(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbol = {"INFO": "🟢", "WARNING": "🟡", "CRITICAL": "🔴"}.get(level, "🟢")
        log_entry = f"[{timestamp}] {symbol} {message}\n"
        
        if hasattr(self, 'log_text'):
            self.log_text.insert(1.0, log_entry)
            if int(self.log_text.index('end-1c').split('.')[0]) > 500:
                self.log_text.delete('end-500l', 'end-1c')
    
    # ========================================================================
    # DATA PERSISTENCE
    # ========================================================================
    
    def save_data(self):
        data = {
            'blocked_ips': list(self.blocked_ips),
            'attack_statistics': {
                'total_attacks': self.attack_statistics['total_attacks'],
                'unique_attackers': list(self.attack_statistics['unique_attackers']),
                'common_passwords': dict(self.attack_statistics['common_passwords'])
            }
        }
        with open('data/system_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        try:
            with open('data/system_data.json', 'r') as f:
                data = json.load(f)
                self.blocked_ips = set(data.get('blocked_ips', []))
                stats = data.get('attack_statistics', {})
                self.attack_statistics['total_attacks'] = stats.get('total_attacks', 0)
                self.attack_statistics['unique_attackers'] = set(stats.get('unique_attackers', []))
                self.attack_statistics['common_passwords'] = defaultdict(int, stats.get('common_passwords', {}))
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    def clear_logs(self):
        if messagebox.askyesno("Confirm", "Clear all logs and data?"):
            self.login_attempts.clear()
            self.ip_attempt_count.clear()
            self.ip_failure_patterns.clear()
            self.blocked_ips.clear()
            self.attack_statistics = {
                'total_attacks': 0,
                'unique_attackers': set(),
                'peak_attack_time': None,
                'common_passwords': defaultdict(int)
            }
            
            if hasattr(self, 'log_text'):
                self.log_text.delete(1.0, tk.END)
            if hasattr(self, 'honeypot_log'):
                self.honeypot_log.delete(1.0, tk.END)
                self.honeypot_log.insert(tk.END, "🍯 Honeypot Active - Waiting for attackers...\n")
            
            open('data/logs.txt', 'w').close()
            open('data/blocked_ips.txt', 'w').close()
            
            self.log_message("All logs cleared!", "WARNING")
            self.update_dashboard()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("🛡️ BRUTE FORCE DETECTION SYSTEM v2.2")
    print("="*60)
    print("Starting application...")
    print("")
    
    root = tk.Tk()
    app = AdvancedBruteForceDetector(root)
    
    print("✅ System ready!")
    print("📊 GUI window opened")
    print("")
    print("Quick Start:")
    print("  1. Click 'Normal' - Simulate legitimate users")
    print("  2. Click 'Attack' - Simulate attack")
    print("  3. Click 'Honeypot' - Test trap system")
    print("  4. Click 'Export PDF' - Generate & email report")
    print("")
    
    root.mainloop()