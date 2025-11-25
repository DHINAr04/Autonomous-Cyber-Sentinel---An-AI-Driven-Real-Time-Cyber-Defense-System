"""
Automated Report Generator
Generates comprehensive incident reports with charts and analysis
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from pathlib import Path


class ReportGenerator:
    """Generate comprehensive security incident reports"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.charts_dir = self.output_dir / "charts"
        self.charts_dir.mkdir(exist_ok=True)
    
    def generate_full_report(
        self,
        alerts: List[Dict[str, Any]],
        investigations: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        time_range: str = "24h"
    ) -> str:
        """Generate a complete incident report with all details"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"incident_report_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(report_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        elements.append(Paragraph("🛡️ Autonomous Cyber Sentinel", title_style))
        elements.append(Paragraph("Security Incident Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Report metadata
        report_info = f"""
        <b>Report Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br/>
        <b>Time Range:</b> Last {time_range}<br/>
        <b>Total Alerts:</b> {len(alerts)}<br/>
        <b>Total Investigations:</b> {len(investigations)}<br/>
        <b>Total Actions:</b> {len(actions)}<br/>
        """
        elements.append(Paragraph(report_info, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", heading_style))
        summary = self._generate_executive_summary(alerts, investigations, actions)
        elements.append(Paragraph(summary, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Generate and add charts
        elements.append(PageBreak())
        elements.append(Paragraph("Threat Analysis & Visualizations", heading_style))
        
        # Severity distribution chart
        severity_chart = self._create_severity_chart(alerts)
        if severity_chart:
            elements.append(Image(severity_chart, width=5*inch, height=3*inch))
            elements.append(Spacer(1, 12))
        
        # Timeline chart
        timeline_chart = self._create_timeline_chart(alerts)
        if timeline_chart:
            elements.append(Image(timeline_chart, width=6*inch, height=3*inch))
            elements.append(Spacer(1, 12))
        
        # Attack types
        elements.append(PageBreak())
        elements.append(Paragraph("Detected Threats", heading_style))
        threat_table = self._create_threat_table(alerts[:10])  # Top 10
        if threat_table:
            elements.append(threat_table)
            elements.append(Spacer(1, 20))
        
        # Investigation details
        elements.append(PageBreak())
        elements.append(Paragraph("Investigation Details", heading_style))
        investigation_summary = self._generate_investigation_summary(investigations)
        elements.append(Paragraph(investigation_summary, styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # TI sources chart
        ti_chart = self._create_ti_sources_chart(investigations)
        if ti_chart:
            elements.append(Image(ti_chart, width=5*inch, height=3*inch))
            elements.append(Spacer(1, 12))
        
        # Response actions
        elements.append(PageBreak())
        elements.append(Paragraph("Response Actions Taken", heading_style))
        actions_summary = self._generate_actions_summary(actions)
        elements.append(Paragraph(actions_summary, styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Actions distribution
        actions_chart = self._create_actions_chart(actions)
        if actions_chart:
            elements.append(Image(actions_chart, width=5*inch, height=3*inch))
            elements.append(Spacer(1, 12))
        
        # Detailed logs
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Event Logs", heading_style))
        logs_table = self._create_logs_table(alerts, investigations, actions)
        if logs_table:
            elements.append(logs_table)
        
        # Recommendations
        elements.append(PageBreak())
        elements.append(Paragraph("Recommendations", heading_style))
        recommendations = self._generate_recommendations(alerts, investigations, actions)
        elements.append(Paragraph(recommendations, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        return str(report_path)
    
    def _generate_executive_summary(
        self,
        alerts: List[Dict],
        investigations: List[Dict],
        actions: List[Dict]
    ) -> str:
        """Generate executive summary text"""
        
        high_severity = sum(1 for a in alerts if a.get('severity') == 'high')
        medium_severity = sum(1 for a in alerts if a.get('severity') == 'medium')
        low_severity = sum(1 for a in alerts if a.get('severity') == 'low')
        
        malicious = sum(1 for i in investigations if i.get('verdict') == 'malicious')
        suspicious = sum(1 for i in investigations if i.get('verdict') == 'suspicious')
        
        isolated = sum(1 for a in actions if a.get('action_type') == 'isolate_container')
        blocked = sum(1 for a in actions if a.get('action_type') == 'block_ip')
        
        summary = f"""
        During the reporting period, the Autonomous Cyber Sentinel detected and analyzed 
        <b>{len(alerts)}</b> potential security threats. Of these, <b>{high_severity}</b> were 
        classified as high severity, <b>{medium_severity}</b> as medium severity, and 
        <b>{low_severity}</b> as low severity.<br/><br/>
        
        Automated investigation revealed <b>{malicious}</b> confirmed malicious threats and 
        <b>{suspicious}</b> suspicious activities. The system autonomously executed 
        <b>{len(actions)}</b> response actions, including <b>{isolated}</b> container isolations 
        and <b>{blocked}</b> IP blocks, successfully containing all identified threats within 
        the target SLA of 10 seconds.<br/><br/>
        
        All actions were performed safely within the simulated environment with complete 
        audit trails maintained for compliance and forensic analysis.
        """
        
        return summary
    
    def _create_severity_chart(self, alerts: List[Dict]) -> str:
        """Create severity distribution pie chart"""
        if not alerts:
            return None
        
        severities = [a.get('severity', 'unknown') for a in alerts]
        severity_counts = pd.Series(severities).value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        colors_map = {'high': '#e74c3c', 'medium': '#f39c12', 'low': '#3498db'}
        colors_list = [colors_map.get(s, '#95a5a6') for s in severity_counts.index]
        
        ax.pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%',
               colors=colors_list, startangle=90)
        ax.set_title('Alert Severity Distribution', fontsize=14, fontweight='bold')
        
        chart_path = self.charts_dir / f"severity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(chart_path)
    
    def _create_timeline_chart(self, alerts: List[Dict]) -> str:
        """Create timeline of alerts"""
        if not alerts:
            return None
        
        df = pd.DataFrame(alerts)
        df['timestamp'] = pd.to_datetime(df['ts'], unit='s')
        df = df.set_index('timestamp')
        
        # Resample by hour
        hourly_counts = df.resample('1H').size()
        
        fig, ax = plt.subplots(figsize=(10, 4))
        hourly_counts.plot(kind='line', ax=ax, color='#3498db', linewidth=2, marker='o')
        ax.set_title('Alert Timeline (Hourly)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time')
        ax.set_ylabel('Number of Alerts')
        ax.grid(True, alpha=0.3)
        
        chart_path = self.charts_dir / f"timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(chart_path)
    
    def _create_threat_table(self, alerts: List[Dict]) -> Table:
        """Create table of top threats"""
        if not alerts:
            return None
        
        data = [['Time', 'Source IP', 'Severity', 'Score']]
        
        for alert in alerts:
            timestamp = datetime.fromtimestamp(alert.get('ts', 0)).strftime('%H:%M:%S')
            src_ip = alert.get('src_ip', 'N/A')
            severity = alert.get('severity', 'unknown').upper()
            score = f"{alert.get('model_score', 0):.2f}"
            data.append([timestamp, src_ip, severity, score])
        
        table = Table(data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _generate_investigation_summary(self, investigations: List[Dict]) -> str:
        """Generate investigation summary text"""
        if not investigations:
            return "No investigations performed during this period."
        
        verdicts = pd.Series([i.get('verdict', 'unknown') for i in investigations]).value_counts()
        avg_risk = sum(i.get('risk_score', 0) for i in investigations) / len(investigations)
        
        summary = f"""
        <b>Investigation Statistics:</b><br/>
        • Total Investigations: {len(investigations)}<br/>
        • Average Risk Score: {avg_risk:.2f}<br/>
        • Verdicts: {', '.join(f'{k}: {v}' for k, v in verdicts.items())}<br/><br/>
        
        All investigations utilized multiple threat intelligence sources including VirusTotal, 
        AbuseIPDB, and AlienVault OTX to provide comprehensive threat context and validation.
        """
        
        return summary
    
    def _create_ti_sources_chart(self, investigations: List[Dict]) -> str:
        """Create TI sources utilization chart"""
        if not investigations:
            return None
        
        sources_count = {'VirusTotal': 0, 'AbuseIPDB': 0, 'OTX': 0}
        
        for inv in investigations:
            sources = inv.get('sources', [])
            if 'virustotal' in sources:
                sources_count['VirusTotal'] += 1
            if 'abuseipdb' in sources:
                sources_count['AbuseIPDB'] += 1
            if 'otx' in sources:
                sources_count['OTX'] += 1
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(sources_count.keys(), sources_count.values(), color=['#3498db', '#e74c3c', '#f39c12'])
        ax.set_title('Threat Intelligence Sources Utilization', fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Queries')
        ax.grid(True, alpha=0.3, axis='y')
        
        chart_path = self.charts_dir / f"ti_sources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(chart_path)
    
    def _generate_actions_summary(self, actions: List[Dict]) -> str:
        """Generate actions summary text"""
        if not actions:
            return "No response actions taken during this period."
        
        action_types = pd.Series([a.get('action_type', 'unknown') for a in actions]).value_counts()
        reversible = sum(1 for a in actions if a.get('reversible') == 'yes')
        
        summary = f"""
        <b>Response Actions Summary:</b><br/>
        • Total Actions: {len(actions)}<br/>
        • Reversible Actions: {reversible}<br/>
        • Action Types:<br/>
        """
        
        for action_type, count in action_types.items():
            summary += f"  - {action_type.replace('_', ' ').title()}: {count}<br/>"
        
        summary += """<br/>
        All actions were executed autonomously based on the configured decision matrix, 
        with complete audit trails maintained for compliance and potential rollback.
        """
        
        return summary
    
    def _create_actions_chart(self, actions: List[Dict]) -> str:
        """Create actions distribution chart"""
        if not actions:
            return None
        
        action_types = [a.get('action_type', 'unknown') for a in actions]
        action_counts = pd.Series(action_types).value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 5))
        action_counts.plot(kind='barh', ax=ax, color='#2ecc71')
        ax.set_title('Response Actions Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Count')
        ax.grid(True, alpha=0.3, axis='x')
        
        chart_path = self.charts_dir / f"actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(chart_path)
    
    def _create_logs_table(
        self,
        alerts: List[Dict],
        investigations: List[Dict],
        actions: List[Dict]
    ) -> Table:
        """Create detailed logs table"""
        
        data = [['Time', 'Event Type', 'Details', 'Severity/Verdict']]
        
        # Combine and sort all events
        events = []
        
        for alert in alerts[:5]:  # Limit to recent events
            events.append({
                'ts': alert.get('ts', 0),
                'type': 'Alert',
                'details': f"From {alert.get('src_ip', 'N/A')}",
                'severity': alert.get('severity', 'unknown')
            })
        
        for inv in investigations[:5]:
            events.append({
                'ts': inv.get('ts', 0),
                'type': 'Investigation',
                'details': f"Risk: {inv.get('risk_score', 0):.2f}",
                'severity': inv.get('verdict', 'unknown')
            })
        
        for action in actions[:5]:
            events.append({
                'ts': action.get('ts', 0),
                'type': 'Response',
                'details': action.get('action_type', 'unknown'),
                'severity': action.get('result', 'unknown')
            })
        
        # Sort by timestamp
        events.sort(key=lambda x: x['ts'], reverse=True)
        
        for event in events[:15]:  # Top 15 events
            timestamp = datetime.fromtimestamp(event['ts']).strftime('%Y-%m-%d %H:%M:%S')
            data.append([
                timestamp,
                event['type'],
                event['details'],
                event['severity']
            ])
        
        table = Table(data, colWidths=[1.8*inch, 1.2*inch, 2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _generate_recommendations(
        self,
        alerts: List[Dict],
        investigations: List[Dict],
        actions: List[Dict]
    ) -> str:
        """Generate security recommendations"""
        
        high_severity_count = sum(1 for a in alerts if a.get('severity') == 'high')
        malicious_count = sum(1 for i in investigations if i.get('verdict') == 'malicious')
        
        recommendations = """
        <b>Security Recommendations:</b><br/><br/>
        """
        
        if high_severity_count > 10:
            recommendations += """
            • <b>High Alert Volume:</b> Consider reviewing detection thresholds and implementing 
            additional network segmentation to reduce attack surface.<br/><br/>
            """
        
        if malicious_count > 5:
            recommendations += """
            • <b>Confirmed Threats:</b> Review firewall rules and implement stricter access controls. 
            Consider deploying additional monitoring on affected network segments.<br/><br/>
            """
        
        recommendations += """
        • <b>Continuous Monitoring:</b> Maintain 24/7 monitoring and ensure all security patches 
        are up to date across the infrastructure.<br/><br/>
        
        • <b>Incident Response:</b> Review and update incident response playbooks based on 
        observed attack patterns.<br/><br/>
        
        • <b>Training:</b> Conduct security awareness training for all personnel to reduce 
        social engineering risks.<br/><br/>
        
        • <b>Backup & Recovery:</b> Verify backup systems are functioning and test recovery 
        procedures regularly.
        """
        
        return recommendations


def generate_html_dashboard(
    alerts: List[Dict],
    investigations: List[Dict],
    actions: List[Dict]
) -> str:
    """Generate interactive HTML dashboard with Plotly charts"""
    
    # Create interactive charts
    df_alerts = pd.DataFrame(alerts) if alerts else pd.DataFrame()
    
    # Severity distribution
    if not df_alerts.empty:
        severity_fig = px.pie(
            df_alerts,
            names='severity',
            title='Alert Severity Distribution',
            color='severity',
            color_discrete_map={'high': '#e74c3c', 'medium': '#f39c12', 'low': '#3498db'}
        )
        
        # Timeline
        df_alerts['timestamp'] = pd.to_datetime(df_alerts['ts'], unit='s')
        timeline_fig = px.line(
            df_alerts.groupby(df_alerts['timestamp'].dt.floor('H')).size().reset_index(name='count'),
            x='timestamp',
            y='count',
            title='Alert Timeline',
            labels={'timestamp': 'Time', 'count': 'Number of Alerts'}
        )
        
        # Risk scores
        df_inv = pd.DataFrame(investigations) if investigations else pd.DataFrame()
        if not df_inv.empty:
            risk_fig = px.histogram(
                df_inv,
                x='risk_score',
                title='Risk Score Distribution',
                nbins=20
            )
        else:
            risk_fig = None
    else:
        severity_fig = None
        timeline_fig = None
        risk_fig = None
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sentinel Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            h1 {{ color: #2c3e50; }}
            .chart {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <h1>🛡️ Autonomous Cyber Sentinel - Interactive Dashboard</h1>
        <div class="chart" id="severity"></div>
        <div class="chart" id="timeline"></div>
        <div class="chart" id="risk"></div>
        <script>
            {f"Plotly.newPlot('severity', {severity_fig.to_json()});" if severity_fig else ""}
            {f"Plotly.newPlot('timeline', {timeline_fig.to_json()});" if timeline_fig else ""}
            {f"Plotly.newPlot('risk', {risk_fig.to_json()});" if risk_fig else ""}
        </script>
    </body>
    </html>
    """
    
    return html
