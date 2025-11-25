import os
import time
import hashlib
from typing import Dict, Any, Optional
import requests
from sentinel.common.config import vt_api_key, abuseipdb_api_key, otx_api_key, redis_url, offline_mode
from .cache import TTLCache, RedisTTLCache, Cache


def _make_cache() -> Cache:
    url = redis_url()
    try:
        return RedisTTLCache(url)
    except Exception:
        return TTLCache()


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:12]


class VirusTotalClient:
    def __init__(self, cache: Cache) -> None:
        self.api_key = vt_api_key()
        self.cache = cache

    def ip_report(self, ip: str) -> Dict[str, Any]:
        key = f"vt:{ip}"
        cached = self.cache.get(key)
        if cached:
            return cached
        if offline_mode() or not self.api_key:
            val = int(_hash(ip), 16) % 101
            data = {"source": "vt", "ip": ip, "reputation": val, "mocked": True}
            self.cache.set(key, data, 300.0)
            return data
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        headers = {"x-apikey": self.api_key}
        r = requests.get(url, headers=headers, timeout=5)
        rep = r.json().get("data", {}).get("attributes", {}).get("reputation", 0)
        data = {"source": "vt", "ip": ip, "reputation": rep}
        self.cache.set(key, data, 300.0)
        time.sleep(1.0)
        return data


class AbuseIPDBClient:
    def __init__(self, cache: Cache) -> None:
        self.api_key = abuseipdb_api_key()
        self.cache = cache

    def ip_check(self, ip: str) -> Dict[str, Any]:
        key = f"abuse:{ip}"
        cached = self.cache.get(key)
        if cached:
            return cached
        if offline_mode() or not self.api_key:
            val = int(_hash(ip), 16) % 101
            data = {"source": "abuseipdb", "ip": ip, "abuse_score": val, "mocked": True}
            self.cache.set(key, data, 300.0)
            return data
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": self.api_key, "Accept": "application/json"}
        params = {"ipAddress": ip, "maxAgeInDays": 90}
        r = requests.get(url, headers=headers, params=params, timeout=5)
        score = r.json().get("data", {}).get("abuseConfidenceScore", 0)
        data = {"source": "abuseipdb", "ip": ip, "abuse_score": score}
        self.cache.set(key, data, 300.0)
        time.sleep(1.0)
        return data


class OTXClient:
    def __init__(self, cache: Cache) -> None:
        self.api_key = otx_api_key()
        self.cache = cache

    def ip_info(self, ip: str) -> Dict[str, Any]:
        key = f"otx:{ip}"
        cached = self.cache.get(key)
        if cached:
            return cached
        if offline_mode() or not self.api_key:
            pulse_count = int(_hash(ip), 16) % 5
            data = {"source": "otx", "ip": ip, "pulses": pulse_count, "mocked": True}
            self.cache.set(key, data, 300.0)
            time.sleep(0.1)
            return data
        headers = {"X-OTX-API-KEY": self.api_key}
        url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
        try:
            r = requests.get(url, headers=headers, timeout=5)
            pulse_count = len(r.json().get("pulse_info", {}).get("pulses", []))
        except Exception:
            pulse_count = 0
        data = {"source": "otx", "ip": ip, "pulses": pulse_count}
        self.cache.set(key, data, 300.0)
        time.sleep(0.5)
        return data


class IPQualityScoreClient:
    """Free IP reputation check (no API key needed for basic checks)"""
    def __init__(self, cache: Cache) -> None:
        self.cache = cache

    def ip_check(self, ip: str) -> Dict[str, Any]:
        key = f"ipqs:{ip}"
        cached = self.cache.get(key)
        if cached:
            return cached
        
        if offline_mode():
            fraud_score = int(_hash(ip), 16) % 100
            data = {"source": "ipqualityscore", "ip": ip, "fraud_score": fraud_score, "mocked": True}
            self.cache.set(key, data, 300.0)
            return data
        
        # Free API endpoint (limited)
        url = f"https://www.ipqualityscore.com/api/json/ip/free/{ip}"
        try:
            r = requests.get(url, timeout=5)
            result = r.json()
            fraud_score = result.get("fraud_score", 0)
            data = {"source": "ipqualityscore", "ip": ip, "fraud_score": fraud_score}
        except Exception:
            fraud_score = 0
            data = {"source": "ipqualityscore", "ip": ip, "fraud_score": fraud_score, "error": True}
        
        self.cache.set(key, data, 300.0)
        time.sleep(1.0)
        return data


class ThreatCrowdClient:
    """Free threat intelligence aggregator"""
    def __init__(self, cache: Cache) -> None:
        self.cache = cache

    def ip_report(self, ip: str) -> Dict[str, Any]:
        key = f"threatcrowd:{ip}"
        cached = self.cache.get(key)
        if cached:
            return cached
        
        if offline_mode():
            votes = int(_hash(ip), 16) % 10
            data = {"source": "threatcrowd", "ip": ip, "votes": votes, "mocked": True}
            self.cache.set(key, data, 300.0)
            return data
        
        url = f"https://www.threatcrowd.org/searchApi/v2/ip/report/?ip={ip}"
        try:
            r = requests.get(url, timeout=5)
            result = r.json()
            votes = result.get("votes", 0)
            data = {"source": "threatcrowd", "ip": ip, "votes": votes, "references": len(result.get("references", []))}
        except Exception:
            data = {"source": "threatcrowd", "ip": ip, "votes": 0, "error": True}
        
        self.cache.set(key, data, 300.0)
        time.sleep(1.0)
        return data


class GreyNoiseClient:
    """Free internet scanner detection"""
    def __init__(self, cache: Cache) -> None:
        self.cache = cache

    def ip_check(self, ip: str) -> Dict[str, Any]:
        key = f"greynoise:{ip}"
        cached = self.cache.get(key)
        if cached:
            return cached
        
        if offline_mode():
            is_scanner = int(_hash(ip), 16) % 2 == 0
            data = {"source": "greynoise", "ip": ip, "is_scanner": is_scanner, "mocked": True}
            self.cache.set(key, data, 300.0)
            return data
        
        # Community API (free, no key needed)
        url = f"https://api.greynoise.io/v3/community/{ip}"
        try:
            r = requests.get(url, timeout=5)
            result = r.json()
            data = {
                "source": "greynoise",
                "ip": ip,
                "noise": result.get("noise", False),
                "riot": result.get("riot", False),
                "classification": result.get("classification", "unknown")
            }
        except Exception:
            data = {"source": "greynoise", "ip": ip, "error": True}
        
        self.cache.set(key, data, 300.0)
        time.sleep(1.0)
        return data