# Brute-Force Login Detection System

## Project Overview
A cybersecurity project designed to detect suspicious login activity and identify potential brute-force attacks using Python-based detection logic and security monitoring.

## Key Features
- Detection of repeated failed login attempts.
- Threshold-based attack detection.
- Honeypot integration for identifying suspicious activity.
- Dashboard for visualizing login attempts and attack patterns.
- Security report generation in PDF format.
- Automated alerts and email notifications, if configured.

## Technologies Used
- **Language:** Python
- **Interface:** Tkinter
- **Visualization:** Matplotlib
- **Reporting:** ReportLab
- **Data Storage:** JSON and log files
- **Libraries:** NumPy, Pillow

## How It Works
1. Monitors and records login attempts.
2. Analyzes failed attempts against configured thresholds.
3. Identifies suspicious activity and potential brute-force attacks.
4. Displays attack statistics on the dashboard.
5. Generates security reports for further analysis.

## Project Structure
- `main.py` — Main application
- `requirements.txt` — Python dependencies
- `README.md` — Project documentation

## Future Enhancements
- Integration with SIEM platforms.
- Improved detection of distributed brute-force attacks.
- Enhanced threat intelligence and alerting capabilities.




