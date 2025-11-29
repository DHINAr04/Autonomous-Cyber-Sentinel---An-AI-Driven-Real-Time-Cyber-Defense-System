"""Zero-Trust policy engine with mTLS and device posture verification."""
import logging
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Trust levels for zero-trust model."""
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4


class DevicePosture:
    """Device posture verification."""
    
    def __init__(self):
        self.device_registry: Dict[str, Dict[str, Any]] = {}
        logger.info("Device posture verification initialized")
    
    def register_device(self, device_id: str, attributes: Dict[str, Any]) -> bool:
        """
        Register a device with its attributes.
        
        Args:
            device_id: Unique device identifier
            attributes: Device attributes (OS, patch level, AV status, etc.)
            
        Returns:
            True if registration successful
        """
        self.device_registry[device_id] = {
            'attributes': attributes,
            'registered_at': time.time(),
            'last_verified': time.time(),
            'trust_score': 0.0
        }
        
        # Calculate initial trust score
        trust_score = self._calculate_trust_score(attributes)
        self.device_registry[device_id]['trust_score'] = trust_score
        
        logger.info(f"Device registered: {device_id} (trust={trust_score:.2f})")
        return True
    
    def verify_posture(self, device_id: str) -> Tuple[bool, float, List[str]]:
        """
        Verify device security posture.
        
        Args:
            device_id: Device identifier
            
        Returns:
            (is_compliant, trust_score, issues)
        """
        if device_id not in self.device_registry:
            return False, 0.0, ["Device not registered"]
        
        device = self.device_registry[device_id]
        attributes = device['attributes']
        issues = []
        
        # Check OS patch level
        if not attributes.get('os_patched', False):
            issues.append("Operating system not up to date")
        
        # Check antivirus status
        if not attributes.get('av_enabled', False):
            issues.append("Antivirus not enabled")
        
        if not attributes.get('av_updated', False):
            issues.append("Antivirus definitions outdated")
        
        # Check firewall
        if not attributes.get('firewall_enabled', False):
            issues.append("Firewall not enabled")
        
        # Check disk encryption
        if not attributes.get('disk_encrypted', False):
            issues.append("Disk encryption not enabled")
        
        # Check for suspicious processes
        if attributes.get('suspicious_processes', 0) > 0:
            issues.append(f"Suspicious processes detected: {attributes['suspicious_processes']}")
        
        # Calculate trust score
        trust_score = self._calculate_trust_score(attributes)
        device['trust_score'] = trust_score
        device['last_verified'] = time.time()
        
        is_compliant = len(issues) == 0 and trust_score >= 0.7
        
        return is_compliant, trust_score, issues
    
    def _calculate_trust_score(self, attributes: Dict[str, Any]) -> float:
        """Calculate device trust score (0.0 to 1.0)."""
        score = 0.0
        
        # OS patched (20%)
        if attributes.get('os_patched', False):
            score += 0.2
        
        # Antivirus (20%)
        if attributes.get('av_enabled', False):
            score += 0.1
        if attributes.get('av_updated', False):
            score += 0.1
        
        # Firewall (15%)
        if attributes.get('firewall_enabled', False):
            score += 0.15
        
        # Disk encryption (15%)
        if attributes.get('disk_encrypted', False):
            score += 0.15
        
        # No suspicious activity (30%)
        suspicious = attributes.get('suspicious_processes', 0)
        if suspicious == 0:
            score += 0.3
        elif suspicious <= 2:
            score += 0.15
        
        return min(score, 1.0)
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device information."""
        return self.device_registry.get(device_id)


class MTLSIdentityManager:
    """Mutual TLS identity management."""
    
    def __init__(self):
        self.identities: Dict[str, Dict[str, Any]] = {}
        self.certificates: Dict[str, str] = {}
        logger.info("mTLS identity manager initialized")
    
    def register_identity(self, identity_id: str, cert_fingerprint: str,
                         attributes: Dict[str, Any]) -> bool:
        """
        Register an identity with certificate.
        
        Args:
            identity_id: Unique identity identifier
            cert_fingerprint: Certificate fingerprint (SHA-256)
            attributes: Identity attributes (user, role, permissions)
            
        Returns:
            True if registration successful
        """
        self.identities[identity_id] = {
            'cert_fingerprint': cert_fingerprint,
            'attributes': attributes,
            'registered_at': time.time(),
            'last_authenticated': None,
            'auth_count': 0
        }
        
        self.certificates[cert_fingerprint] = identity_id
        
        logger.info(f"Identity registered: {identity_id}")
        return True
    
    def verify_certificate(self, cert_fingerprint: str) -> Tuple[bool, Optional[str]]:
        """
        Verify certificate and return identity.
        
        Args:
            cert_fingerprint: Certificate fingerprint
            
        Returns:
            (is_valid, identity_id)
        """
        if cert_fingerprint not in self.certificates:
            logger.warning(f"Unknown certificate: {cert_fingerprint[:16]}...")
            return False, None
        
        identity_id = self.certificates[cert_fingerprint]
        identity = self.identities[identity_id]
        
        # Update authentication tracking
        identity['last_authenticated'] = time.time()
        identity['auth_count'] += 1
        
        logger.debug(f"Certificate verified for identity: {identity_id}")
        return True, identity_id
    
    def get_identity_attributes(self, identity_id: str) -> Optional[Dict[str, Any]]:
        """Get identity attributes."""
        if identity_id not in self.identities:
            return None
        return self.identities[identity_id]['attributes']
    
    def revoke_certificate(self, cert_fingerprint: str) -> bool:
        """Revoke a certificate."""
        if cert_fingerprint not in self.certificates:
            return False
        
        identity_id = self.certificates[cert_fingerprint]
        del self.certificates[cert_fingerprint]
        del self.identities[identity_id]
        
        logger.info(f"Certificate revoked: {cert_fingerprint[:16]}...")
        return True


class ZeroTrustPolicyEngine:
    """Zero-trust policy engine for access control."""
    
    def __init__(self):
        self.device_posture = DevicePosture()
        self.mtls_manager = MTLSIdentityManager()
        self.policies: List[Dict[str, Any]] = []
        self.access_log: List[Dict[str, Any]] = []
        
        logger.info("Zero-trust policy engine initialized")
        self._load_default_policies()
    
    def _load_default_policies(self) -> None:
        """Load default zero-trust policies."""
        self.policies = [
            {
                'name': 'require_device_compliance',
                'description': 'Devices must meet security posture requirements',
                'condition': lambda ctx: ctx.get('device_compliant', False),
                'action': 'allow',
                'priority': 100
            },
            {
                'name': 'require_mtls',
                'description': 'Require mutual TLS authentication',
                'condition': lambda ctx: ctx.get('mtls_verified', False),
                'action': 'allow',
                'priority': 90
            },
            {
                'name': 'block_untrusted_devices',
                'description': 'Block devices with low trust scores',
                'condition': lambda ctx: ctx.get('trust_score', 0.0) < 0.5,
                'action': 'deny',
                'priority': 80
            },
            {
                'name': 'require_mfa_high_risk',
                'description': 'Require MFA for high-risk operations',
                'condition': lambda ctx: ctx.get('risk_level') == 'high' and not ctx.get('mfa_verified', False),
                'action': 'deny',
                'priority': 70
            },
            {
                'name': 'time_based_access',
                'description': 'Restrict access to business hours',
                'condition': lambda ctx: self._is_business_hours() if ctx.get('require_business_hours') else True,
                'action': 'allow',
                'priority': 60
            }
        ]
        
        logger.info(f"Loaded {len(self.policies)} default policies")
    
    def evaluate_access(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate access request against zero-trust policies.
        
        Args:
            request: Access request with context
            
        Returns:
            Decision dictionary
        """
        context = self._build_context(request)
        
        # Evaluate policies in priority order
        policies_evaluated = []
        decision = 'allow'  # Default allow (will be overridden by deny)
        reasons = []
        
        for policy in sorted(self.policies, key=lambda p: p['priority'], reverse=True):
            try:
                condition_met = policy['condition'](context)
                
                policies_evaluated.append({
                    'name': policy['name'],
                    'condition_met': condition_met,
                    'action': policy['action']
                })
                
                if condition_met:
                    if policy['action'] == 'deny':
                        decision = 'deny'
                        reasons.append(policy['description'])
                    elif policy['action'] == 'allow' and decision != 'deny':
                        reasons.append(policy['description'])
                
            except Exception as e:
                logger.error(f"Policy evaluation error ({policy['name']}): {e}")
        
        result = {
            'decision': decision,
            'reasons': reasons,
            'trust_level': self._calculate_trust_level(context),
            'policies_evaluated': policies_evaluated,
            'context': context,
            'timestamp': time.time()
        }
        
        # Log access decision
        self._log_access(request, result)
        
        return result
    
    def _build_context(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Build evaluation context from request."""
        context = request.copy()
        
        # Verify device posture
        device_id = request.get('device_id')
        if device_id:
            compliant, trust_score, issues = self.device_posture.verify_posture(device_id)
            context['device_compliant'] = compliant
            context['trust_score'] = trust_score
            context['posture_issues'] = issues
        else:
            context['device_compliant'] = False
            context['trust_score'] = 0.0
        
        # Verify mTLS
        cert_fingerprint = request.get('cert_fingerprint')
        if cert_fingerprint:
            valid, identity_id = self.mtls_manager.verify_certificate(cert_fingerprint)
            context['mtls_verified'] = valid
            context['identity_id'] = identity_id
            
            if identity_id:
                attrs = self.mtls_manager.get_identity_attributes(identity_id)
                context['identity_attributes'] = attrs
        else:
            context['mtls_verified'] = False
        
        return context
    
    def _calculate_trust_level(self, context: Dict[str, Any]) -> TrustLevel:
        """Calculate overall trust level."""
        trust_score = context.get('trust_score', 0.0)
        mtls_verified = context.get('mtls_verified', False)
        device_compliant = context.get('device_compliant', False)
        
        if mtls_verified and device_compliant and trust_score >= 0.9:
            return TrustLevel.VERIFIED
        elif mtls_verified and device_compliant and trust_score >= 0.7:
            return TrustLevel.HIGH
        elif mtls_verified or (device_compliant and trust_score >= 0.6):
            return TrustLevel.MEDIUM
        elif trust_score >= 0.3:
            return TrustLevel.LOW
        else:
            return TrustLevel.UNTRUSTED
    
    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours."""
        now = datetime.now()
        return 9 <= now.hour <= 17 and now.weekday() < 5  # Mon-Fri, 9AM-5PM
    
    def _log_access(self, request: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Log access decision."""
        log_entry = {
            'timestamp': time.time(),
            'device_id': request.get('device_id'),
            'identity_id': result['context'].get('identity_id'),
            'resource': request.get('resource'),
            'decision': result['decision'],
            'trust_level': result['trust_level'].name,
            'reasons': result['reasons']
        }
        
        self.access_log.append(log_entry)
        
        # Keep only last 10000 entries
        if len(self.access_log) > 10000:
            self.access_log = self.access_log[-10000:]
    
    def add_policy(self, policy: Dict[str, Any]) -> None:
        """Add a custom policy."""
        self.policies.append(policy)
        logger.info(f"Policy added: {policy['name']}")
    
    def get_access_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent access log entries."""
        return self.access_log[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get zero-trust statistics."""
        recent_log = self.access_log[-1000:]  # Last 1000 entries
        
        total = len(recent_log)
        if total == 0:
            return {
                'total_requests': 0,
                'allow_rate': 0.0,
                'deny_rate': 0.0,
                'avg_trust_score': 0.0
            }
        
        allowed = sum(1 for entry in recent_log if entry['decision'] == 'allow')
        denied = total - allowed
        
        return {
            'total_requests': total,
            'allowed': allowed,
            'denied': denied,
            'allow_rate': allowed / total,
            'deny_rate': denied / total,
            'registered_devices': len(self.device_posture.device_registry),
            'registered_identities': len(self.mtls_manager.identities),
            'active_policies': len(self.policies)
        }
