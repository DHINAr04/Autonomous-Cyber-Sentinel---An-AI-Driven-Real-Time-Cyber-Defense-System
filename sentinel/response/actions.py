"""Response action handlers with production and simulation modes."""
import os
import subprocess
import logging
from typing import Dict, Any, Optional
from enum import Enum


class ActionMode(Enum):
    """Action execution mode."""
    SIMULATION = "simulation"  # Safe simulation mode (default)
    PRODUCTION = "production"   # Real actions (requires explicit enable)


class ActionHandler:
    """Handles autonomous response actions with safety guards."""
    
    def __init__(self, mode: str = "simulation") -> None:
        """
        Initialize action handler.
        
        Args:
            mode: "simulation" or "production"
        """
        self._applied: Dict[str, Dict[str, Any]] = {}
        self.mode = ActionMode(mode)
        self.logger = logging.getLogger(__name__)
        
        # Safety: Whitelist of IPs that should NEVER be blocked
        self.whitelist = self._load_whitelist()
        
        # Safety: Require explicit production mode enable
        if self.mode == ActionMode.PRODUCTION:
            if not os.getenv('ENABLE_PRODUCTION_ACTIONS') == 'true':
                self.logger.warning(
                    "Production mode requested but not enabled. "
                    "Set ENABLE_PRODUCTION_ACTIONS=true to enable real actions."
                )
                self.mode = ActionMode.SIMULATION
    
    def _load_whitelist(self) -> set:
        """Load IP whitelist from environment or config."""
        whitelist_str = os.getenv('IP_WHITELIST', '127.0.0.1,localhost,::1')
        return set(whitelist_str.split(','))
    
    def _is_whitelisted(self, target: str) -> bool:
        """Check if target is whitelisted."""
        # Extract IP from target string
        ip = target.split(':')[0] if ':' in target else target
        return ip in self.whitelist
    
    def _check_safety(self, target: str, action_type: str) -> tuple[bool, str]:
        """
        Safety checks before executing action.
        
        Returns:
            (is_safe, reason)
        """
        # Check whitelist
        if self._is_whitelisted(target):
            return False, f"Target {target} is whitelisted"
        
        # Check if target is localhost/internal
        if target.startswith('127.') or target.startswith('localhost'):
            return False, "Cannot block localhost"
        
        # Check if target is private network (be cautious)
        if target.startswith('192.168.') or target.startswith('10.'):
            self.logger.warning(f"Action on private network IP: {target}")
        
        return True, "Safety checks passed"

    def isolate_container(self, target: str, params: Dict[str, Any]) -> str:
        """
        Isolate a Docker container from the network.
        
        Args:
            target: Container ID or name
            params: Additional parameters (reason, duration, etc.)
        
        Returns:
            Result string
        """
        rid = f"iso:{target}"
        self._applied[rid] = {"target": target, "params": params, "action": "isolate_container"}
        
        if self.mode == ActionMode.SIMULATION:
            self.logger.info(f"[SIMULATION] Would isolate container: {target}")
            return "simulated_isolation"
        
        # Production mode - real Docker isolation
        try:
            # Disconnect container from all networks
            result = subprocess.run(
                ['docker', 'network', 'disconnect', 'bridge', target],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"[PRODUCTION] Isolated container: {target}")
                return "isolated"
            else:
                self.logger.error(f"Failed to isolate container: {result.stderr}")
                return f"failed: {result.stderr}"
        except Exception as e:
            self.logger.error(f"Error isolating container: {e}")
            return f"error: {str(e)}"

    def redirect_to_honeypot(self, target: str, params: Dict[str, Any]) -> str:
        """Redirect traffic to honeypot."""
        rid = f"redir:{target}"
        self._applied[rid] = {"target": target, "params": params, "action": "redirect_to_honeypot"}
        
        if self.mode == ActionMode.SIMULATION:
            self.logger.info(f"[SIMULATION] Would redirect {target} to honeypot")
            return "simulated_redirect"
        
        # Production mode - real iptables redirect
        honeypot_ip = params.get('honeypot_ip', '10.0.0.100')
        try:
            # Add iptables rule to redirect traffic
            result = subprocess.run(
                ['iptables', '-t', 'nat', '-A', 'PREROUTING', 
                 '-s', target, '-j', 'DNAT', '--to-destination', honeypot_ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"[PRODUCTION] Redirected {target} to honeypot {honeypot_ip}")
                return "redirected"
            else:
                return f"failed: {result.stderr}"
        except Exception as e:
            self.logger.error(f"Error redirecting to honeypot: {e}")
            return f"error: {str(e)}"

    def block_ip(self, target: str, params: Dict[str, Any]) -> str:
        """
        Block an IP address using iptables.
        
        Args:
            target: IP address to block
            params: Additional parameters
        
        Returns:
            Result string
        """
        # Safety check
        is_safe, reason = self._check_safety(target, 'block_ip')
        if not is_safe:
            self.logger.warning(f"Blocked action on {target}: {reason}")
            return f"blocked_by_safety: {reason}"
        
        rid = f"block:{target}"
        self._applied[rid] = {"target": target, "params": params, "action": "block_ip"}
        
        if self.mode == ActionMode.SIMULATION:
            self.logger.info(f"[SIMULATION] Would block IP: {target}")
            return "simulated_block"
        
        # Production mode - real iptables block
        try:
            # Add iptables rule to drop packets
            result = subprocess.run(
                ['iptables', '-A', 'INPUT', '-s', target, '-j', 'DROP'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"[PRODUCTION] Blocked IP: {target}")
                return "blocked"
            else:
                self.logger.error(f"Failed to block IP: {result.stderr}")
                return f"failed: {result.stderr}"
        except Exception as e:
            self.logger.error(f"Error blocking IP: {e}")
            return f"error: {str(e)}"

    def rate_limit(self, target: str, params: Dict[str, Any]) -> str:
        """Apply rate limiting to an IP address."""
        rid = f"rl:{target}"
        self._applied[rid] = {"target": target, "params": params, "action": "rate_limit"}
        
        rate = params.get('rate', '10/second')
        
        if self.mode == ActionMode.SIMULATION:
            self.logger.info(f"[SIMULATION] Would rate limit {target} to {rate}")
            return "simulated_rate_limit"
        
        # Production mode - real iptables rate limiting
        try:
            # Add iptables rule for rate limiting
            result = subprocess.run(
                ['iptables', '-A', 'INPUT', '-s', target, 
                 '-m', 'limit', '--limit', rate, '-j', 'ACCEPT'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"[PRODUCTION] Rate limited {target} to {rate}")
                return "rate_limited"
            else:
                return f"failed: {result.stderr}"
        except Exception as e:
            self.logger.error(f"Error applying rate limit: {e}")
            return f"error: {str(e)}"

    def quarantine_file(self, target: str, params: Dict[str, Any]) -> str:
        """Quarantine a suspicious file."""
        rid = f"qf:{target}"
        self._applied[rid] = {"target": target, "params": params, "action": "quarantine_file"}
        
        if self.mode == ActionMode.SIMULATION:
            self.logger.info(f"[SIMULATION] Would quarantine file: {target}")
            return "simulated_quarantine"
        
        # Production mode - move file to quarantine directory
        try:
            quarantine_dir = params.get('quarantine_dir', '/var/quarantine')
            os.makedirs(quarantine_dir, exist_ok=True)
            
            # Move file to quarantine
            import shutil
            quarantine_path = os.path.join(quarantine_dir, os.path.basename(target))
            shutil.move(target, quarantine_path)
            
            self.logger.info(f"[PRODUCTION] Quarantined file: {target} -> {quarantine_path}")
            return "quarantined"
        except Exception as e:
            self.logger.error(f"Error quarantining file: {e}")
            return f"error: {str(e)}"

    def revert(self, action_type: str, target: str) -> str:
        """
        Revert a previously applied action.
        
        Args:
            action_type: Type of action to revert
            target: Target of the action
        
        Returns:
            Result string
        """
        rid_prefix = {
            "isolate_container": "iso",
            "redirect_to_honeypot": "redir",
            "block_ip": "block",
            "rate_limit": "rl",
            "quarantine_file": "qf",
        }.get(action_type, "")
        
        rid = f"{rid_prefix}:{target}" if rid_prefix else target
        
        if rid not in self._applied:
            return "noop"
        
        action_info = self._applied[rid]
        
        if self.mode == ActionMode.SIMULATION:
            self.logger.info(f"[SIMULATION] Would revert {action_type} on {target}")
            self._applied.pop(rid, None)
            return "reverted"
        
        # Production mode - actually revert the action
        try:
            if action_type == "isolate_container":
                # Reconnect container to network
                subprocess.run(
                    ['docker', 'network', 'connect', 'bridge', target],
                    capture_output=True,
                    timeout=10
                )
            elif action_type == "block_ip":
                # Remove iptables block rule
                subprocess.run(
                    ['iptables', '-D', 'INPUT', '-s', target, '-j', 'DROP'],
                    capture_output=True,
                    timeout=10
                )
            elif action_type == "redirect_to_honeypot":
                # Remove iptables redirect rule
                honeypot_ip = action_info['params'].get('honeypot_ip', '10.0.0.100')
                subprocess.run(
                    ['iptables', '-t', 'nat', '-D', 'PREROUTING',
                     '-s', target, '-j', 'DNAT', '--to-destination', honeypot_ip],
                    capture_output=True,
                    timeout=10
                )
            
            self._applied.pop(rid, None)
            self.logger.info(f"[PRODUCTION] Reverted {action_type} on {target}")
            return "reverted"
        except Exception as e:
            self.logger.error(f"Error reverting action: {e}")
            return f"error: {str(e)}"
    
    def get_active_actions(self) -> Dict[str, Dict[str, Any]]:
        """Get all currently active actions."""
        return self._applied.copy()
    
    def get_mode(self) -> str:
        """Get current action mode."""
        return self.mode.value