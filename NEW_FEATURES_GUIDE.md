# 🎉 New Features Installation & Usage Guide

## 🚀 **Quick Start**

### **Step 1: Install New Dependencies**

Run the installation script:
```powershell
.\install_new_features.bat
```

Or manually:
```powershell
.\.venv\Scripts\Activate.ps1
pip install matplotlib plotly pandas jinja2 reportlab pillow aiosmtplib
```

### **Step 2: Restart the Server**

Stop the current server (Ctrl+C) and restart:
```powershell
.\start_server.bat
```

### **Step 3: Access Enhanced Dashboard**

Open your browser:
```
http://localhost:8001
```

---

## 📊 **Using the Report Generation Feature**

### **Method 1: Dashboard Button (Easiest)**

1. Open http://localhost:8001
2. Wait for some alerts to be generated (30 seconds)
3. Click the **"📊 Generate Report"** button
4. Wait 5-10 seconds for generation
5. Click the download link that appears
6. Open the PDF report

### **Method 2: API Call**

```bash
# Generate report
curl http://localhost:8001/report/generate

# Response:
# {
#   "status": "success",
#   "report_path": "reports/incident_report_20241124_203045.pdf",
#   "message": "Report generated successfully"
# }

# Download the report
curl http://localhost:8001/report/download/incident_report_20241124_203045.pdf -O
```

### **Method 3: Python Script**

```python
import requests
import time

# Wait for some data
print("Waiting for data collection...")
time.sleep(60)

# Generate report
print("Generating report...")
response = requests.get('http://localhost:8001/report/generate')
result = response.json()

if result['status'] == 'success':
    print(f"✓ Report generated: {result['report_path']}")
    
    # Get filename
    filename = result['report_path'].split('/')[-1]
    
    # Download
    report_url = f'http://localhost:8001/report/download/{filename}'
    report_data = requests.get(report_url)
    
    with open(filename, 'wb') as f:
        f.write(report_data.content)
    
    print(f"✓ Downloaded: {filename}")
else:
    print(f"✗ Error: {result['message']}")
```

---

## 🔍 **Understanding the Report**

### **Report Sections**

#### **1. Executive Summary**
- Total alerts, investigations, actions
- Severity breakdown
- Threat verdicts
- Response time metrics

#### **2. Threat Analysis**
- **Severity Distribution Chart** - Pie chart showing high/medium/low alerts
- **Timeline Graph** - Hourly alert trends
- **Top Threats Table** - Most critical incidents

#### **3. Investigation Details**
- TI source utilization
- Risk score analysis
- Verdict distribution
- Confidence metrics

#### **4. Response Actions**
- Actions taken breakdown
- Action type distribution
- Reversibility status
- Safety gate levels

#### **5. Event Logs**
- Chronological event listing
- Complete audit trail
- Timestamps for all events

#### **6. Recommendations**
- Security best practices
- Action items
- Compliance guidance

---

## 🎨 **Report Customization**

### **Time Range**

Generate reports for different time periods:

```bash
# Last 24 hours (default)
curl http://localhost:8001/report/generate?time_range=24h

# Last 7 days
curl http://localhost:8001/report/generate?time_range=7d

# Last 30 days
curl http://localhost:8001/report/generate?time_range=30d
```

### **Report Location**

Reports are saved in:
```
reports/
├── incident_report_20241124_203045.pdf
├── incident_report_20241124_204530.pdf
└── charts/
    ├── severity_20241124_203045.png
    ├── timeline_20241124_203045.png
    └── ...
```

---

## 🔍 **New Threat Intelligence Sources**

### **6 Active Sources**

#### **1. VirusTotal**
- IP reputation scores
- Malware detection
- Community votes

#### **2. AbuseIPDB**
- Abuse confidence scores
- Report history
- Category classification

#### **3. AlienVault OTX**
- Threat pulses
- IOC correlation
- Community intelligence

#### **4. IPQualityScore** ⭐ NEW
- Fraud score calculation
- Proxy/VPN detection
- Free tier available

#### **5. ThreatCrowd** ⭐ NEW
- Community threat data
- Historical information
- Reference tracking

#### **6. GreyNoise** ⭐ NEW
- Internet scanner detection
- Noise classification
- Targeted attack identification

### **Enhanced Risk Scoring**

The system now uses **all 6 sources** to calculate risk:

```python
risk_score = (
    0.4 * ml_model_score +
    0.6 * (
        vt_reputation +
        abuseipdb_score +
        otx_pulses +
        ipqs_fraud_score +
        threatcrowd_votes +
        greynoise_classification
    ) / 6
)
```

---

## 📈 **Dashboard Enhancements**

### **New UI Elements**

1. **TI Sources Badge Display**
   - Shows all 6 active sources
   - Color-coded badges
   - Visual confirmation

2. **Report Generation Button**
   - One-click report creation
   - Real-time status updates
   - Download link on completion

3. **Status Notifications**
   - Success/error messages
   - Progress indicators
   - User feedback

### **Improved Navigation**

- Direct links to reports
- Report list view
- Download management

---

## 🎯 **Use Cases**

### **1. Daily Security Review**

```bash
# Generate daily report
curl http://localhost:8001/report/generate?time_range=24h

# Review PDF for:
# - New threats
# - Response effectiveness
# - Trends and patterns
```

### **2. Incident Investigation**

```bash
# Generate detailed report
curl http://localhost:8001/report/generate

# Use report for:
# - Forensic analysis
# - Timeline reconstruction
# - Evidence collection
```

### **3. Compliance Reporting**

```bash
# Generate weekly report
curl http://localhost:8001/report/generate?time_range=7d

# Use for:
# - Audit trails
# - Compliance documentation
# - Management reporting
```

### **4. Threat Intelligence Briefing**

```bash
# Generate comprehensive report
curl http://localhost:8001/report/generate

# Share with:
# - Security team
# - Management
# - Stakeholders
```

---

## 🔧 **Troubleshooting**

### **Report Generation Fails**

**Problem**: Error generating report

**Solutions**:
1. Ensure dependencies are installed:
   ```powershell
   pip install matplotlib plotly pandas reportlab pillow
   ```

2. Check if `reports/` directory exists:
   ```powershell
   mkdir reports
   mkdir reports\charts
   ```

3. Verify data exists:
   ```bash
   curl http://localhost:8001/stats
   ```

### **Charts Not Appearing**

**Problem**: PDF has no charts

**Solutions**:
1. Install matplotlib:
   ```powershell
   pip install matplotlib
   ```

2. Check chart directory:
   ```powershell
   dir reports\charts
   ```

### **Download Link Not Working**

**Problem**: Cannot download report

**Solutions**:
1. Check report was generated:
   ```bash
   curl http://localhost:8001/report/list
   ```

2. Verify file exists:
   ```powershell
   dir reports\*.pdf
   ```

3. Use direct download:
   ```bash
   curl http://localhost:8001/report/download/filename.pdf -O
   ```

---

## 📊 **Sample Report Output**

### **What to Expect**

```
📄 incident_report_20241124_203045.pdf
├── Page 1: Cover & Executive Summary
│   ├── Report metadata
│   ├── Key statistics
│   └── Summary text
├── Page 2: Threat Analysis
│   ├── Severity pie chart
│   ├── Timeline graph
│   └── Analysis text
├── Page 3: Threat Details
│   ├── Top 10 threats table
│   └── Detailed breakdown
├── Page 4: Investigation
│   ├── TI findings
│   ├── Source utilization chart
│   └── Risk analysis
├── Page 5: Response Actions
│   ├── Actions summary
│   ├── Distribution chart
│   └── Audit trail
├── Page 6: Event Logs
│   ├── Chronological table
│   └── Complete history
└── Page 7: Recommendations
    ├── Security advice
    └── Action items
```

---

## 🎓 **Best Practices**

### **1. Regular Reporting**

Generate reports regularly:
- **Daily**: Quick security review
- **Weekly**: Trend analysis
- **Monthly**: Comprehensive assessment

### **2. Report Retention**

Keep reports for:
- Compliance requirements
- Historical analysis
- Incident investigation

### **3. Review Process**

Establish a review workflow:
1. Generate report
2. Review findings
3. Take action on recommendations
4. Document changes
5. Archive report

### **4. Sharing Reports**

- **Internal**: Share with security team
- **Management**: Executive summaries
- **Compliance**: Audit documentation
- **External**: Incident response partners

---

## 🚀 **Advanced Features**

### **Scheduled Reports** (Future Enhancement)

```python
# Add to cron/scheduler
# Generate daily report at 9 AM
0 9 * * * curl http://localhost:8001/report/generate
```

### **Email Reports** (Ready to Configure)

```python
# Configure SMTP in .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### **Custom Report Templates** (Extensible)

Modify `sentinel/reporting/generator.py` to:
- Add custom sections
- Change styling
- Include additional data
- Customize charts

---

## ✅ **Verification Checklist**

After installation, verify:

- [ ] Dependencies installed successfully
- [ ] Server restarts without errors
- [ ] Dashboard shows 6 TI sources
- [ ] Report button appears
- [ ] Can generate report
- [ ] PDF downloads successfully
- [ ] Charts appear in PDF
- [ ] All sections present
- [ ] Data is accurate

---

## 🎉 **You're All Set!**

Your Autonomous Cyber Sentinel now has:

✅ **6 Threat Intelligence Sources**
✅ **Automated PDF Reports**
✅ **Professional Charts**
✅ **Enhanced Dashboard**
✅ **Complete Audit Trail**
✅ **Security Recommendations**

**Start generating reports and exploring the enhanced features!** 🛡️📊
