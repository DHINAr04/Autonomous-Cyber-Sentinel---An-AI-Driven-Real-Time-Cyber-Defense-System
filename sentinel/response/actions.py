from typing import Dict, Any


class ActionHandler:
    def __init__(self) -> None:
        self._applied: Dict[str, Dict[str, Any]] = {}

    def isolate_container(self, target: str, params: Dict[str, Any]) -> str:
        rid = f"iso:{target}"
        self._applied[rid] = {"target": target, "params": params}
        return "simulated_isolation"

    def redirect_to_honeypot(self, target: str, params: Dict[str, Any]) -> str:
        rid = f"redir:{target}"
        self._applied[rid] = {"target": target, "params": params}
        return "simulated_redirect"

    def block_ip(self, target: str, params: Dict[str, Any]) -> str:
        rid = f"block:{target}"
        self._applied[rid] = {"target": target, "params": params}
        return "simulated_block"

    def rate_limit(self, target: str, params: Dict[str, Any]) -> str:
        rid = f"rl:{target}"
        self._applied[rid] = {"target": target, "params": params}
        return "simulated_rate_limit"

    def quarantine_file(self, target: str, params: Dict[str, Any]) -> str:
        rid = f"qf:{target}"
        self._applied[rid] = {"target": target, "params": params}
        return "simulated_quarantine"

    def revert(self, action_type: str, target: str) -> str:
        rid_prefix = {
            "isolate_container": "iso",
            "redirect_to_honeypot": "redir",
            "block_ip": "block",
            "rate_limit": "rl",
            "quarantine_file": "qf",
        }.get(action_type, "")
        rid = f"{rid_prefix}:{target}" if rid_prefix else target
        if rid in self._applied:
            self._applied.pop(rid, None)
            return "reverted"
        return "noop"