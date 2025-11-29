"""SIEM integration for exporting alerts to ELK Stack, OpenSearch, and Splunk."""
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class ElasticsearchExporter:
    """Export alerts to Elasticsearch/OpenSearch."""
    
    def __init__(self, hosts: List[str], index_prefix: str = "sentinel-alerts"):
        """
        Initialize Elasticsearch exporter.
        
        Args:
            hosts: List of Elasticsearch hosts
            index_prefix: Index name prefix
        """
        self.hosts = hosts
        self.index_prefix = index_prefix
        self.client = None
        
        logger.info(f"Initializing Elasticsearch exporter: {hosts}")
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Elasticsearch."""
        try:
            from elasticsearch import Elasticsearch
            
            self.client = Elasticsearch(
                self.hosts,
                verify_certs=False,  # For development
                ssl_show_warn=False
            )
            
            # Test connection
            if self.client.ping():
                logger.info("Connected to Elasticsearch")
            else:
                logger.error("Failed to connect to Elasticsearch")
                self.client = None
                
        except ImportError:
            logger.warning("elasticsearch-py not installed, using HTTP fallback")
            self.client = None
        except Exception as e:
            logger.error(f"Elasticsearch connection error: {e}")
            self.client = None
    
    def export_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Export alert to Elasticsearch.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            True if export successful
        """
        if self.client is None:
            return self._http_export(alert)
        
        try:
            # Generate index name with date
            date_str = datetime.now().strftime("%Y.%m.%d")
            index_name = f"{self.index_prefix}-{date_str}"
            
            # Prepare document
            doc = self._prepare_document(alert)
            
            # Index document
            response = self.client.index(
                index=index_name,
                document=doc
            )
            
            logger.debug(f"Alert exported to Elasticsearch: {response['_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to Elasticsearch: {e}")
            return False
    
    def _http_export(self, alert: Dict[str, Any]) -> bool:
        """Fallback HTTP export."""
        try:
            import requests
            
            date_str = datetime.now().strftime("%Y.%m.%d")
            index_name = f"{self.index_prefix}-{date_str}"
            
            doc = self._prepare_document(alert)
            
            # POST to Elasticsearch HTTP API
            url = f"{self.hosts[0]}/{index_name}/_doc"
            response = requests.post(url, json=doc, timeout=10)
            
            if response.status_code in [200, 201]:
                logger.debug("Alert exported via HTTP")
                return True
            else:
                logger.error(f"HTTP export failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"HTTP export error: {e}")
            return False
    
    def _prepare_document(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare alert document for Elasticsearch."""
        return {
            '@timestamp': datetime.fromtimestamp(alert.get('ts', time.time())).isoformat(),
            'alert_id': alert.get('id'),
            'severity': alert.get('severity'),
            'score': alert.get('score'),
            'source': {
                'ip': alert.get('src'),
                'port': alert.get('src_port', 0)
            },
            'destination': {
                'ip': alert.get('dst'),
                'port': alert.get('dst_port', 0)
            },
            'sensor_id': alert.get('sensor_id'),
            'tags': ['sentinel', 'threat', alert.get('severity', 'unknown')],
            'event': {
                'kind': 'alert',
                'category': 'threat',
                'type': 'indicator',
                'outcome': 'success'
            }
        }
    
    def bulk_export(self, alerts: List[Dict[str, Any]]) -> int:
        """
        Bulk export multiple alerts.
        
        Args:
            alerts: List of alerts
            
        Returns:
            Number of successfully exported alerts
        """
        if not self.client:
            return sum(1 for alert in alerts if self.export_alert(alert))
        
        try:
            from elasticsearch.helpers import bulk
            
            date_str = datetime.now().strftime("%Y.%m.%d")
            index_name = f"{self.index_prefix}-{date_str}"
            
            # Prepare bulk actions
            actions = [
                {
                    '_index': index_name,
                    '_source': self._prepare_document(alert)
                }
                for alert in alerts
            ]
            
            # Bulk index
            success, failed = bulk(self.client, actions, raise_on_error=False)
            
            logger.info(f"Bulk export: {success} successful, {failed} failed")
            return success
            
        except Exception as e:
            logger.error(f"Bulk export error: {e}")
            return 0


class SplunkExporter:
    """Export alerts to Splunk HTTP Event Collector (HEC)."""
    
    def __init__(self, hec_url: str, hec_token: str, index: str = "sentinel"):
        """
        Initialize Splunk exporter.
        
        Args:
            hec_url: Splunk HEC URL
            hec_token: HEC authentication token
            index: Splunk index name
        """
        self.hec_url = hec_url.rstrip('/')
        self.hec_token = hec_token
        self.index = index
        
        logger.info(f"Initialized Splunk exporter: {hec_url}")
    
    def export_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Export alert to Splunk.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            True if export successful
        """
        try:
            import requests
            
            # Prepare HEC event
            event = {
                'time': alert.get('ts', time.time()),
                'host': alert.get('sensor_id', 'sentinel'),
                'source': 'sentinel',
                'sourcetype': 'sentinel:alert',
                'index': self.index,
                'event': self._prepare_event(alert)
            }
            
            # Send to HEC
            headers = {
                'Authorization': f'Splunk {self.hec_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.hec_url}/services/collector/event",
                json=event,
                headers=headers,
                verify=False,  # For development
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug("Alert exported to Splunk")
                return True
            else:
                logger.error(f"Splunk export failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Splunk export error: {e}")
            return False
    
    def _prepare_event(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare alert event for Splunk."""
        return {
            'alert_id': alert.get('id'),
            'severity': alert.get('severity'),
            'score': alert.get('score'),
            'src_ip': alert.get('src'),
            'dst_ip': alert.get('dst'),
            'src_port': alert.get('src_port', 0),
            'dst_port': alert.get('dst_port', 0),
            'sensor_id': alert.get('sensor_id'),
            'timestamp': datetime.fromtimestamp(alert.get('ts', time.time())).isoformat()
        }


class CEFExporter:
    """Export alerts in Common Event Format (CEF) for universal SIEM compatibility."""
    
    def __init__(self, syslog_host: str = "localhost", syslog_port: int = 514):
        """
        Initialize CEF exporter.
        
        Args:
            syslog_host: Syslog server host
            syslog_port: Syslog server port
        """
        self.syslog_host = syslog_host
        self.syslog_port = syslog_port
        
        logger.info(f"Initialized CEF exporter: {syslog_host}:{syslog_port}")
    
    def export_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Export alert in CEF format.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            True if export successful
        """
        try:
            cef_message = self._format_cef(alert)
            return self._send_syslog(cef_message)
            
        except Exception as e:
            logger.error(f"CEF export error: {e}")
            return False
    
    def _format_cef(self, alert: Dict[str, Any]) -> str:
        """
        Format alert as CEF message.
        
        CEF Format:
        CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
        """
        # CEF header
        version = 0
        vendor = "Sentinel"
        product = "Autonomous Cyber Sentinel"
        device_version = "1.0"
        signature_id = alert.get('id', 'unknown')
        name = f"Threat Detected - {alert.get('severity', 'unknown').upper()}"
        severity = self._map_severity(alert.get('severity', 'low'))
        
        # CEF extensions
        extensions = {
            'src': alert.get('src', ''),
            'dst': alert.get('dst', ''),
            'spt': alert.get('src_port', 0),
            'dpt': alert.get('dst_port', 0),
            'cs1': alert.get('sensor_id', ''),
            'cs1Label': 'SensorID',
            'cn1': alert.get('score', 0.0),
            'cn1Label': 'ThreatScore',
            'msg': f"Threat detected with score {alert.get('score', 0.0):.2f}"
        }
        
        extension_str = ' '.join(f"{k}={v}" for k, v in extensions.items())
        
        cef_message = f"CEF:{version}|{vendor}|{product}|{device_version}|{signature_id}|{name}|{severity}|{extension_str}"
        
        return cef_message
    
    def _map_severity(self, severity: str) -> int:
        """Map severity to CEF severity (0-10)."""
        mapping = {
            'low': 3,
            'medium': 6,
            'high': 9,
            'critical': 10
        }
        return mapping.get(severity.lower(), 5)
    
    def _send_syslog(self, message: str) -> bool:
        """Send message via syslog."""
        try:
            import socket
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message.encode('utf-8'), (self.syslog_host, self.syslog_port))
            sock.close()
            
            logger.debug("CEF message sent via syslog")
            return True
            
        except Exception as e:
            logger.error(f"Syslog send error: {e}")
            return False


class SIEMIntegrationManager:
    """Manage multiple SIEM integrations."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SIEM integration manager.
        
        Args:
            config: Configuration dictionary
        """
        self.exporters: List[Any] = []
        self.config = config
        
        logger.info("Initializing SIEM integrations")
        self._initialize_exporters()
    
    def _initialize_exporters(self) -> None:
        """Initialize configured exporters."""
        # Elasticsearch/OpenSearch
        if self.config.get('elasticsearch', {}).get('enabled', False):
            es_config = self.config['elasticsearch']
            exporter = ElasticsearchExporter(
                hosts=es_config.get('hosts', ['http://localhost:9200']),
                index_prefix=es_config.get('index_prefix', 'sentinel-alerts')
            )
            self.exporters.append(exporter)
            logger.info("Elasticsearch exporter enabled")
        
        # Splunk
        if self.config.get('splunk', {}).get('enabled', False):
            splunk_config = self.config['splunk']
            exporter = SplunkExporter(
                hec_url=splunk_config.get('hec_url'),
                hec_token=splunk_config.get('hec_token'),
                index=splunk_config.get('index', 'sentinel')
            )
            self.exporters.append(exporter)
            logger.info("Splunk exporter enabled")
        
        # CEF/Syslog
        if self.config.get('cef', {}).get('enabled', False):
            cef_config = self.config['cef']
            exporter = CEFExporter(
                syslog_host=cef_config.get('syslog_host', 'localhost'),
                syslog_port=cef_config.get('syslog_port', 514)
            )
            self.exporters.append(exporter)
            logger.info("CEF exporter enabled")
    
    def export_alert(self, alert: Dict[str, Any]) -> Dict[str, bool]:
        """
        Export alert to all configured SIEMs.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Dictionary of exporter -> success status
        """
        results = {}
        
        for exporter in self.exporters:
            exporter_name = exporter.__class__.__name__
            try:
                success = exporter.export_alert(alert)
                results[exporter_name] = success
            except Exception as e:
                logger.error(f"{exporter_name} export failed: {e}")
                results[exporter_name] = False
        
        return results
    
    def bulk_export(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Bulk export alerts to all configured SIEMs.
        
        Args:
            alerts: List of alerts
            
        Returns:
            Dictionary of exporter -> count of successful exports
        """
        results = {}
        
        for exporter in self.exporters:
            exporter_name = exporter.__class__.__name__
            try:
                if hasattr(exporter, 'bulk_export'):
                    count = exporter.bulk_export(alerts)
                else:
                    count = sum(1 for alert in alerts if exporter.export_alert(alert))
                results[exporter_name] = count
            except Exception as e:
                logger.error(f"{exporter_name} bulk export failed: {e}")
                results[exporter_name] = 0
        
        return results
