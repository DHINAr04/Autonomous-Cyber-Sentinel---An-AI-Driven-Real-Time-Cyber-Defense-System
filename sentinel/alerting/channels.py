"""Multi-channel alert delivery system."""
import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AlertChannel:
    """Configuration for an alert channel."""
    name: str
    enabled: bool
    min_severity: AlertSeverity
    config: Dict[str, Any]


class EmailChannel:
    """Email alert channel."""
    
    def __init__(self, config: Dict[str, Any]):
        self.smtp_host = config.get('smtp_host', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_user = config.get('smtp_user', '')
        self.smtp_password = config.get('smtp_password', '')
        self.from_email = config.get('from_email', self.smtp_user)
        self.to_emails = config.get('to_emails', [])
        self.enabled = bool(self.smtp_user and self.smtp_password and self.to_emails)
    
    async def send_alert(self, alert: Dict[str, Any], explanation: Dict[str, Any] = None) -> bool:
        """Send alert via email."""
        if not self.enabled:
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Security Alert: {alert.get('severity', 'unknown').upper()} - {alert.get('id', 'N/A')}"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            
            # Create email body
            text_body = self._create_text_body(alert, explanation)
            html_body = self._create_html_body(alert, explanation)
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            async with aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port) as smtp:
                await smtp.starttls()
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email alert failed: {e}")
            return False
    
    def _create_text_body(self, alert: Dict[str, Any], explanation: Dict[str, Any] = None) -> str:
        """Create plain text email body."""
        body = "SECURITY ALERT\n"
        body += "=" * 50 + "\n\n"
        body += f"Alert ID: {alert.get('id', 'N/A')}\n"
        body += f"Severity: {alert.get('severity', 'unknown').upper()}\n"
        body += f"Confidence: {alert.get('score', 0):.1%}\n"
        body += f"Timestamp: {alert.get('timestamp', 'N/A')}\n\n"
        
        body += f"Source IP: {alert.get('src_ip', 'N/A')}\n"
        body += f"Destination IP: {alert.get('dst_ip', 'N/A')}\n"
        body += f"Sensor: {alert.get('sensor_id', 'N/A')}\n\n"
        
        if explanation:
            body += "PRIMARY REASONS:\n"
            for reason in explanation.get('primary_reasons', []):
                body += f"  • {reason}\n"
            body += "\n"
            
            if explanation.get('threat_intelligence', {}).get('findings'):
                body += "THREAT INTELLIGENCE:\n"
                for finding in explanation['threat_intelligence']['findings']:
                    body += f"  • {finding}\n"
                body += "\n"
            
            body += "RECOMMENDED ACTIONS:\n"
            for rec in explanation.get('recommendations', [])[:5]:
                body += f"  {rec}\n"
        
        body += "\n" + "=" * 50 + "\n"
        body += "This is an automated alert from Autonomous Cyber Sentinel\n"
        
        return body
    
    def _create_html_body(self, alert: Dict[str, Any], explanation: Dict[str, Any] = None) -> str:
        """Create HTML email body."""
        severity = alert.get('severity', 'unknown')
        severity_colors = {
            'low': '#4CAF50',
            'medium': '#FF9800',
            'high': '#FF5722',
            'critical': '#D32F2F'
        }
        color = severity_colors.get(severity, '#757575')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: {color}; color: white; padding: 20px; border-radius: 5px; }}
                .content {{ padding: 20px; background: #f5f5f5; margin: 20px 0; border-radius: 5px; }}
                .section {{ margin: 15px 0; }}
                .label {{ font-weight: bold; color: #555; }}
                .value {{ color: #333; }}
                ul {{ list-style-type: none; padding-left: 0; }}
                li {{ padding: 5px 0; }}
                .footer {{ text-align: center; color: #777; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 Security Alert: {severity.upper()}</h2>
                <p>Alert ID: {alert.get('id', 'N/A')}</p>
            </div>
            
            <div class="content">
                <div class="section">
                    <span class="label">Confidence:</span> 
                    <span class="value">{alert.get('score', 0):.1%}</span>
                </div>
                <div class="section">
                    <span class="label">Source IP:</span> 
                    <span class="value">{alert.get('src_ip', 'N/A')}</span>
                </div>
                <div class="section">
                    <span class="label">Destination IP:</span> 
                    <span class="value">{alert.get('dst_ip', 'N/A')}</span>
                </div>
                <div class="section">
                    <span class="label">Sensor:</span> 
                    <span class="value">{alert.get('sensor_id', 'N/A')}</span>
                </div>
        """
        
        if explanation:
            html += """
                <div class="section">
                    <h3>Primary Reasons:</h3>
                    <ul>
            """
            for reason in explanation.get('primary_reasons', []):
                html += f"<li>• {reason}</li>"
            html += "</ul></div>"
            
            if explanation.get('threat_intelligence', {}).get('findings'):
                html += """
                    <div class="section">
                        <h3>Threat Intelligence:</h3>
                        <ul>
                """
                for finding in explanation['threat_intelligence']['findings']:
                    html += f"<li>• {finding}</li>"
                html += "</ul></div>"
            
            html += """
                <div class="section">
                    <h3>Recommended Actions:</h3>
                    <ul>
            """
            for rec in explanation.get('recommendations', [])[:5]:
                html += f"<li>{rec}</li>"
            html += "</ul></div>"
        
        html += """
            </div>
            <div class="footer">
                <p>This is an automated alert from Autonomous Cyber Sentinel</p>
            </div>
        </body>
        </html>
        """
        
        return html


class SlackChannel:
    """Slack alert channel."""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get('webhook_url', '')
        self.channel = config.get('channel', '#security')
        self.username = config.get('username', 'Cyber Sentinel')
        self.enabled = bool(self.webhook_url)
    
    async def send_alert(self, alert: Dict[str, Any], explanation: Dict[str, Any] = None) -> bool:
        """Send alert to Slack."""
        if not self.enabled:
            return False
        
        try:
            severity = alert.get('severity', 'unknown')
            severity_emojis = {
                'low': '🟢',
                'medium': '🟡',
                'high': '🟠',
                'critical': '🔴'
            }
            emoji = severity_emojis.get(severity, '⚪')
            
            # Create Slack message
            message = {
                'channel': self.channel,
                'username': self.username,
                'icon_emoji': ':shield:',
                'attachments': [{
                    'color': self._get_color(severity),
                    'title': f'{emoji} Security Alert: {severity.upper()}',
                    'text': f"Alert ID: {alert.get('id', 'N/A')}",
                    'fields': [
                        {
                            'title': 'Confidence',
                            'value': f"{alert.get('score', 0):.1%}",
                            'short': True
                        },
                        {
                            'title': 'Source IP',
                            'value': alert.get('src_ip', 'N/A'),
                            'short': True
                        },
                        {
                            'title': 'Destination IP',
                            'value': alert.get('dst_ip', 'N/A'),
                            'short': True
                        },
                        {
                            'title': 'Sensor',
                            'value': alert.get('sensor_id', 'N/A'),
                            'short': True
                        }
                    ],
                    'footer': 'Autonomous Cyber Sentinel',
                    'ts': int(alert.get('timestamp', 0))
                }]
            }
            
            # Add explanation if available
            if explanation and explanation.get('primary_reasons'):
                reasons_text = '\n'.join([f"• {r}" for r in explanation['primary_reasons'][:3]])
                message['attachments'][0]['fields'].append({
                    'title': 'Primary Reasons',
                    'value': reasons_text,
                    'short': False
                })
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Slack alert failed: {e}")
            return False
    
    def _get_color(self, severity: str) -> str:
        """Get color for severity."""
        colors = {
            'low': 'good',
            'medium': 'warning',
            'high': 'danger',
            'critical': '#D32F2F'
        }
        return colors.get(severity, '#757575')


class WebhookChannel:
    """Generic webhook alert channel."""
    
    def __init__(self, config: Dict[str, Any]):
        self.url = config.get('url', '')
        self.headers = config.get('headers', {})
        self.enabled = bool(self.url)
    
    async def send_alert(self, alert: Dict[str, Any], explanation: Dict[str, Any] = None) -> bool:
        """Send alert via webhook."""
        if not self.enabled:
            return False
        
        try:
            payload = {
                'alert': alert,
                'explanation': explanation,
                'timestamp': alert.get('timestamp'),
                'source': 'autonomous-cyber-sentinel'
            }
            
            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"Webhook alert failed: {e}")
            return False


class AlertingSystem:
    """Main alerting system coordinating multiple channels."""
    
    def __init__(self, config_file: str = 'alerting_config.yml'):
        self.channels: Dict[str, Any] = {}
        self.load_config(config_file)
    
    def load_config(self, config_file: str) -> None:
        """Load alerting configuration."""
        # Try to load from file
        if os.path.exists(config_file):
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
        else:
            # Use environment variables
            config = self._load_from_env()
        
        # Initialize channels
        if config.get('email', {}).get('enabled'):
            self.channels['email'] = EmailChannel(config['email'])
        
        if config.get('slack', {}).get('enabled'):
            self.channels['slack'] = SlackChannel(config['slack'])
        
        if config.get('webhook', {}).get('enabled'):
            self.channels['webhook'] = WebhookChannel(config['webhook'])
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            'email': {
                'enabled': bool(os.getenv('ALERT_EMAIL_ENABLED', '')),
                'smtp_host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'smtp_user': os.getenv('SMTP_USER', ''),
                'smtp_password': os.getenv('SMTP_PASSWORD', ''),
                'from_email': os.getenv('ALERT_FROM_EMAIL', ''),
                'to_emails': os.getenv('ALERT_TO_EMAILS', '').split(',')
            },
            'slack': {
                'enabled': bool(os.getenv('ALERT_SLACK_ENABLED', '')),
                'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
                'channel': os.getenv('SLACK_CHANNEL', '#security')
            },
            'webhook': {
                'enabled': bool(os.getenv('ALERT_WEBHOOK_ENABLED', '')),
                'url': os.getenv('WEBHOOK_URL', ''),
                'headers': json.loads(os.getenv('WEBHOOK_HEADERS', '{}'))
            }
        }
    
    async def send_alert(self, alert: Dict[str, Any], explanation: Dict[str, Any] = None) -> Dict[str, bool]:
        """
        Send alert through all configured channels.
        
        Args:
            alert: Alert dictionary
            explanation: Optional explanation from XAI module
        
        Returns:
            Dictionary of channel names to success status
        """
        severity = AlertSeverity(alert.get('severity', 'low'))
        results = {}
        
        # Send to each channel
        tasks = []
        for channel_name, channel in self.channels.items():
            # Check if channel should receive this severity
            if self._should_send(channel, severity):
                if channel_name == 'email':
                    tasks.append(('email', channel.send_alert(alert, explanation)))
                elif channel_name == 'slack':
                    tasks.append(('slack', channel.send_alert(alert, explanation)))
                elif channel_name == 'webhook':
                    tasks.append(('webhook', channel.send_alert(alert, explanation)))
        
        # Execute all sends concurrently
        if tasks:
            task_results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
            for (channel_name, _), result in zip(tasks, task_results):
                results[channel_name] = result if not isinstance(result, Exception) else False
        
        return results
    
    def _should_send(self, channel: Any, severity: AlertSeverity) -> bool:
        """Determine if alert should be sent to channel based on severity."""
        # For now, send all alerts to all channels
        # Can be enhanced with per-channel severity thresholds
        return True
    
    def send_alert_sync(self, alert: Dict[str, Any], explanation: Dict[str, Any] = None) -> Dict[str, bool]:
        """Synchronous wrapper for send_alert."""
        return asyncio.run(self.send_alert(alert, explanation))
