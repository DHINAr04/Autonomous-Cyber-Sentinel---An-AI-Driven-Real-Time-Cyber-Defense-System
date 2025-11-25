import os
from typing import Any, Dict, Optional

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

try:
    import yaml
except Exception:
    yaml = None

_settings: Dict[str, Any] = {}

def _load() -> None:
    if load_dotenv is not None:
        try:
            load_dotenv()
        except Exception:
            pass
    path = os.path.join(os.getcwd(), "settings.yml")
    if yaml is not None and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                if isinstance(data, dict):
                    _settings.update(data)
        except Exception:
            pass

_load()

def _get_setting(key: str, default: Any) -> Any:
    return _settings.get(key, default)

def bus_mode() -> str:
    val = os.getenv("BUS")
    if val is None:
        val = str(_get_setting("bus", "memory"))
    return str(val).strip().lower()

def redis_url() -> str:
    val = os.getenv("REDIS_URL")
    if val is None:
        val = str(_get_setting("redis_url", "redis://localhost:6379/0"))
    return str(val)

def sentinel_db() -> str:
    val = os.getenv("SENTINEL_DB")
    if val is None:
        val = str(_get_setting("sentinel_db", "sqlite:///sentinel.db"))
    return str(val)

def live_capture_enabled() -> bool:
    val = os.getenv("LIVE_CAPTURE")
    if val is not None:
        return str(val) == "1"
    v = _get_setting("live_capture", False)
    return bool(v)

def capture_iface() -> Optional[str]:
    val = os.getenv("CAPTURE_IFACE")
    if val is not None:
        return str(val)
    v = _get_setting("capture_iface", None)
    return None if v is None else str(v)

def vt_api_key() -> Optional[str]:
    val = os.getenv("VT_API_KEY")
    if val is not None and val != "":
        return str(val)
    v = _get_setting("vt_api_key", "")
    return None if v == "" or v is None else str(v)

def abuseipdb_api_key() -> Optional[str]:
    val = os.getenv("ABUSEIPDB_API_KEY")
    if val is not None and val != "":
        return str(val)
    v = _get_setting("abuseipdb_api_key", "")
    return None if v == "" or v is None else str(v)

def otx_api_key() -> Optional[str]:
    val = os.getenv("OTX_API_KEY")
    if val is not None and val != "":
        return str(val)
    v = _get_setting("otx_api_key", "")
    return None if v == "" or v is None else str(v)

def model_path() -> Optional[str]:
    val = os.getenv("MODEL_PATH")
    if val is not None and val != "":
        return str(val)
    v = _get_setting("model_path", "")
    return None if v == "" or v is None else str(v)

def severity_thresholds() -> Dict[str, float]:
    cfg = _get_setting("severity_thresholds", {})
    hi = float(cfg.get("high", 0.8)) if isinstance(cfg, dict) else 0.8
    mid = float(cfg.get("medium", 0.5)) if isinstance(cfg, dict) else 0.5
    lo = float(cfg.get("low", 0.0)) if isinstance(cfg, dict) else 0.0
    return {"high": hi, "medium": mid, "low": lo}

def score_weights() -> Dict[str, float]:
    cfg = _get_setting("score_weights", {})
    b = float(cfg.get("bytes", 0.6)) if isinstance(cfg, dict) else 0.6
    p = float(cfg.get("pkts", 0.3)) if isinstance(cfg, dict) else 0.3
    iat = float(cfg.get("iat_inv", 0.1)) if isinstance(cfg, dict) else 0.1
    return {"bytes": b, "pkts": p, "iat_inv": iat}

def offline_mode() -> bool:
    val = os.getenv("OFFLINE_MODE")
    if val is not None:
        return str(val) == "1"
    v = _get_setting("offline_mode", False)
    return bool(v)

def decision_matrix() -> Dict[str, Dict[str, Dict[str, str]]]:
    dm = _get_setting("decision_matrix", {})
    if isinstance(dm, dict) and dm:
        return dm
    return {
        "low": {
            "risk": {"high": "redirect_to_honeypot", "medium": "log_only", "low": "log_only"},
            "confidence": {"high": "redirect_to_honeypot", "medium": "log_only", "low": "log_only"},
        },
        "medium": {
            "risk": {"high": "isolate_container", "medium": "redirect_to_honeypot", "low": "log_only"},
            "confidence": {"high": "isolate_container", "medium": "redirect_to_honeypot", "low": "log_only"},
        },
        "high": {
            "risk": {"high": "isolate_container", "medium": "block_ip", "low": "rate_limit"},
            "confidence": {"high": "isolate_container", "medium": "block_ip", "low": "rate_limit"},
        },
    }