"""Dynamic honeypot deployment and attacker behavior analysis."""
import logging
import socket
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DynamicHoneypot:
    """Deploy and manage dynamic honeypots to deceive attackers."""
    
    def __init__(self):
        self.active_honeypots: Dict[str, Dict[str, Any]] = {}
        self.interaction_logs: List[Dict[str, Any]] = []
        self.learned_ttps: List[Dict[str, Any]] = []
        
        logger.info("Dynamic honeypot system initialized")
    
    def deploy_honeypot(self, threat_type: str, port: Optional[int] = None) -> Dict[str, Any]:
        """
        Deploy appropriate honeypot based on threat type.
        
        Args:
            threat_type: Type of threat to honeypot
            port: Port to listen on (auto-assigned if None)
            
        Returns:
            Honeypot configuration
        """
        if threat_type == 'ssh_brute_force':
            return self.deploy_ssh_honeypot(port or 2222)
        elif threat_type == 'web_attack':
            return self.deploy_web_honeypot(port or 8080)
        elif threat_type == 'ftp_attack':
            return self.deploy_ftp_honeypot(port or 2121)
        elif threat_type == 'telnet_attack':
            return self.deploy_telnet_honeypot(port or 2323)
        else:
            return self.deploy_generic_honeypot(port or 9999)
    
    def deploy_ssh_honeypot(self, port: int = 2222) -> Dict[str, Any]:
        """Deploy SSH honeypot."""
        honeypot_id = f"ssh_{port}_{int(time.time())}"
        
        config = {
            'id': honeypot_id,
            'type': 'ssh',
            'port': port,
            'status': 'active',
            'deployed_at': time.time(),
            'interactions': 0
        }
        
        # Start honeypot thread
        thread = threading.Thread(
            target=self._run_ssh_honeypot,
            args=(honeypot_id, port),
            daemon=True
        )
        thread.start()
        
        config['thread'] = thread
        self.active_honeypots[honeypot_id] = config
        
        logger.info(f"SSH honeypot deployed: {honeypot_id} on port {port}")
        return config
    
    def _run_ssh_honeypot(self, honeypot_id: str, port: int) -> None:
        """Run SSH honeypot server."""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', port))
            server_socket.listen(5)
            server_socket.settimeout(1.0)  # Non-blocking
            
            logger.info(f"SSH honeypot listening on port {port}")
            
            while honeypot_id in self.active_honeypots:
                try:
                    client_socket, address = server_socket.accept()
                    
                    # Log interaction
                    self._log_interaction(honeypot_id, 'ssh', address[0], {
                        'port': port,
                        'protocol': 'ssh'
                    })
                    
                    # Send fake SSH banner
                    client_socket.send(b"SSH-2.0-OpenSSH_7.4\r\n")
                    
                    # Receive data
                    try:
                        data = client_socket.recv(1024)
                        if data:
                            self._analyze_ssh_attempt(honeypot_id, address[0], data)
                    except:
                        pass
                    
                    client_socket.close()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.debug(f"SSH honeypot error: {e}")
            
            server_socket.close()
            
        except Exception as e:
            logger.error(f"SSH honeypot failed: {e}")
    
    def deploy_web_honeypot(self, port: int = 8080) -> Dict[str, Any]:
        """Deploy web application honeypot."""
        honeypot_id = f"web_{port}_{int(time.time())}"
        
        config = {
            'id': honeypot_id,
            'type': 'web',
            'port': port,
            'status': 'active',
            'deployed_at': time.time(),
            'interactions': 0
        }
        
        thread = threading.Thread(
            target=self._run_web_honeypot,
            args=(honeypot_id, port),
            daemon=True
        )
        thread.start()
        
        config['thread'] = thread
        self.active_honeypots[honeypot_id] = config
        
        logger.info(f"Web honeypot deployed: {honeypot_id} on port {port}")
        return config
    
    def _run_web_honeypot(self, honeypot_id: str, port: int) -> None:
        """Run web honeypot server."""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', port))
            server_socket.listen(5)
            server_socket.settimeout(1.0)
            
            logger.info(f"Web honeypot listening on port {port}")
            
            while honeypot_id in self.active_honeypots:
                try:
                    client_socket, address = server_socket.accept()
                    
                    # Log interaction
                    self._log_interaction(honeypot_id, 'web', address[0], {
                        'port': port,
                        'protocol': 'http'
                    })
                    
                    # Receive HTTP request
                    try:
                        data = client_socket.recv(4096)
                        if data:
                            request = data.decode('utf-8', errors='ignore')
                            self._analyze_web_attack(honeypot_id, address[0], request)
                            
                            # Send fake response
                            response = (
                                "HTTP/1.1 200 OK\r\n"
                                "Content-Type: text/html\r\n"
                                "Server: Apache/2.4.41\r\n"
                                "\r\n"
                                "<html><body><h1>Welcome</h1></body></html>"
                            )
                            client_socket.send(response.encode())
                    except:
                        pass
                    
                    client_socket.close()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.debug(f"Web honeypot error: {e}")
            
            server_socket.close()
            
        except Exception as e:
            logger.error(f"Web honeypot failed: {e}")
    
    def deploy_ftp_honeypot(self, port: int = 2121) -> Dict[str, Any]:
        """Deploy FTP honeypot."""
        honeypot_id = f"ftp_{port}_{int(time.time())}"
        
        config = {
            'id': honeypot_id,
            'type': 'ftp',
            'port': port,
            'status': 'active',
            'deployed_at': time.time(),
            'interactions': 0
        }
        
        self.active_honeypots[honeypot_id] = config
        logger.info(f"FTP honeypot deployed: {honeypot_id} on port {port}")
        
        return config
    
    def deploy_telnet_honeypot(self, port: int = 2323) -> Dict[str, Any]:
        """Deploy Telnet honeypot."""
        honeypot_id = f"telnet_{port}_{int(time.time())}"
        
        config = {
            'id': honeypot_id,
            'type': 'telnet',
            'port': port,
            'status': 'active',
            'deployed_at': time.time(),
            'interactions': 0
        }
        
        self.active_honeypots[honeypot_id] = config
        logger.info(f"Telnet honeypot deployed: {honeypot_id} on port {port}")
        
        return config
    
    def deploy_generic_honeypot(self, port: int = 9999) -> Dict[str, Any]:
        """Deploy generic TCP honeypot."""
        honeypot_id = f"generic_{port}_{int(time.time())}"
        
        config = {
            'id': honeypot_id,
            'type': 'generic',
            'port': port,
            'status': 'active',
            'deployed_at': time.time(),
            'interactions': 0
        }
        
        self.active_honeypots[honeypot_id] = config
        logger.info(f"Generic honeypot deployed: {honeypot_id} on port {port}")
        
        return config
    
    def _log_interaction(self, honeypot_id: str, honeypot_type: str,
                        attacker_ip: str, metadata: Dict[str, Any]) -> None:
        """Log honeypot interaction."""
        interaction = {
            'timestamp': time.time(),
            'honeypot_id': honeypot_id,
            'honeypot_type': honeypot_type,
            'attacker_ip': attacker_ip,
            'metadata': metadata
        }
        
        self.interaction_logs.append(interaction)
        
        # Update honeypot stats
        if honeypot_id in self.active_honeypots:
            self.active_honeypots[honeypot_id]['interactions'] += 1
        
        logger.info(f"Honeypot interaction: {attacker_ip} -> {honeypot_type}")
    
    def _analyze_ssh_attempt(self, honeypot_id: str, attacker_ip: str, data: bytes) -> None:
        """Analyze SSH brute force attempt."""
        try:
            data_str = data.decode('utf-8', errors='ignore')
            
            # Extract TTPs
            ttps = {
                'technique': 'SSH Brute Force',
                'attacker_ip': attacker_ip,
                'timestamp': time.time(),
                'data_sample': data_str[:100]
            }
            
            self.learned_ttps.append(ttps)
            logger.debug(f"SSH TTP learned from {attacker_ip}")
            
        except Exception as e:
            logger.debug(f"SSH analysis error: {e}")
    
    def _analyze_web_attack(self, honeypot_id: str, attacker_ip: str, request: str) -> None:
        """Analyze web attack patterns."""
        try:
            # Detect common attack patterns
            attack_patterns = {
                'sql_injection': ['union', 'select', 'drop', 'insert', '--'],
                'xss': ['<script>', 'javascript:', 'onerror='],
                'path_traversal': ['../', '..\\', '%2e%2e'],
                'command_injection': ['|', ';', '&&', '`']
            }
            
            detected_attacks = []
            for attack_type, patterns in attack_patterns.items():
                if any(pattern.lower() in request.lower() for pattern in patterns):
                    detected_attacks.append(attack_type)
            
            if detected_attacks:
                ttps = {
                    'technique': 'Web Attack',
                    'attack_types': detected_attacks,
                    'attacker_ip': attacker_ip,
                    'timestamp': time.time(),
                    'request_sample': request[:200]
                }
                
                self.learned_ttps.append(ttps)
                logger.info(f"Web attack TTPs learned: {detected_attacks} from {attacker_ip}")
            
        except Exception as e:
            logger.debug(f"Web analysis error: {e}")
    
    def analyze_attacker_behavior(self, honeypot_logs: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Analyze attacker behavior from honeypot logs.
        
        Args:
            honeypot_logs: Optional logs to analyze (uses internal logs if None)
            
        Returns:
            Analysis results with TTPs and recommendations
        """
        logs = honeypot_logs or self.interaction_logs
        
        if not logs:
            return {
                'total_interactions': 0,
                'unique_attackers': 0,
                'ttps': [],
                'recommendations': []
            }
        
        # Analyze logs
        unique_ips = set(log['attacker_ip'] for log in logs)
        
        # Extract TTPs
        ttps = self.extract_ttps(logs)
        
        # Generate recommendations
        recommendations = self.update_detection_rules(ttps)
        
        return {
            'total_interactions': len(logs),
            'unique_attackers': len(unique_ips),
            'most_active_attacker': max(set(log['attacker_ip'] for log in logs),
                                       key=lambda ip: sum(1 for log in logs if log['attacker_ip'] == ip)),
            'ttps': ttps,
            'recommendations': recommendations
        }
    
    def extract_ttps(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract Tactics, Techniques, and Procedures from logs."""
        return self.learned_ttps
    
    def update_detection_rules(self, ttps: List[Dict[str, Any]]) -> List[str]:
        """Generate detection rules based on learned TTPs."""
        recommendations = []
        
        for ttp in ttps:
            technique = ttp.get('technique', 'Unknown')
            
            if 'SSH' in technique:
                recommendations.append(f"Block IP: {ttp.get('attacker_ip')} (SSH brute force)")
                recommendations.append("Enable SSH key-only authentication")
                recommendations.append("Implement fail2ban for SSH")
            
            elif 'Web Attack' in technique:
                attack_types = ttp.get('attack_types', [])
                if 'sql_injection' in attack_types:
                    recommendations.append("Enable WAF rules for SQL injection")
                if 'xss' in attack_types:
                    recommendations.append("Enable XSS protection headers")
                recommendations.append(f"Block IP: {ttp.get('attacker_ip')} (Web attack)")
        
        return list(set(recommendations))  # Remove duplicates
    
    def stop_honeypot(self, honeypot_id: str) -> bool:
        """Stop a running honeypot."""
        if honeypot_id in self.active_honeypots:
            del self.active_honeypots[honeypot_id]
            logger.info(f"Honeypot stopped: {honeypot_id}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get honeypot statistics."""
        return {
            'active_honeypots': len(self.active_honeypots),
            'total_interactions': len(self.interaction_logs),
            'learned_ttps': len(self.learned_ttps),
            'honeypot_types': list(set(h['type'] for h in self.active_honeypots.values()))
        }
    
    def export_ttps(self, filepath: str = 'honeypot_ttps.json') -> None:
        """Export learned TTPs to file."""
        with open(filepath, 'w') as f:
            json.dump({
                'ttps': self.learned_ttps,
                'interactions': self.interaction_logs[-1000:],  # Last 1000
                'exported_at': datetime.now().isoformat()
            }, f, indent=2)
        
        logger.info(f"TTPs exported to {filepath}")
