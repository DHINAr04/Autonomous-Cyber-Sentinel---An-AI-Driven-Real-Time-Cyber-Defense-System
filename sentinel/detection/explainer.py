"""Explainable AI module for threat detection transparency."""
import logging
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class ThreatExplainer:
    """Provides human-readable explanations for threat detection decisions."""
    
    def __init__(self):
        self.feature_names = [
            "bytes", "pkts", "iat_avg", "iat_std", "iat_max", "iat_min"
        ]
        self.feature_descriptions = {
            "bytes": "Total bytes transferred",
            "pkts": "Number of packets",
            "iat_avg": "Average inter-arrival time",
            "iat_std": "Inter-arrival time std deviation",
            "iat_max": "Maximum inter-arrival time",
            "iat_min": "Minimum inter-arrival time"
        }
        
    def explain_detection(
        self,
        alert: Dict[str, Any],
        features: Dict[str, float],
        model_score: float,
        ti_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a threat detection.
        
        Args:
            alert: Alert dictionary
            features: Feature values used for detection
            model_score: ML model confidence score
            ti_results: Threat intelligence results
            
        Returns:
            Explanation dictionary with reasons, confidence breakdown, and recommendations
        """
        explanation = {
            "alert_id": alert.get("id", "unknown"),
            "severity": alert.get("severity", "unknown"),
            "confidence": model_score,
            "top_reasons": [],
            "feature_analysis": {},
            "threat_intelligence": {},
            "confidence_breakdown": {},
            "recommendations": []
        }
        
        # Analyze features
        explanation["feature_analysis"] = self._analyze_features(features)
        explanation["top_reasons"] = self._get_top_reasons(features, model_score)
        
        # Analyze threat intelligence
        if ti_results:
            explanation["threat_intelligence"] = self._analyze_ti(ti_results)
            explanation["top_reasons"].extend(self._get_ti_reasons(ti_results))
        
        # Confidence breakdown
        explanation["confidence_breakdown"] = self._calculate_confidence_breakdown(
            model_score, ti_results
        )
        
        # Generate recommendations
        explanation["recommendations"] = self._generate_recommendations(
            alert, features, ti_results
        )
        
        return explanation
    
    def _analyze_features(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Analyze individual features and their contribution."""
        analysis = {}
        
        # Define thresholds for suspicious behavior
        thresholds = {
            "bytes": {"high": 100000, "low": 100},
            "pkts": {"high": 1000, "low": 10},
            "iat_avg": {"high": 1.0, "low": 0.001},
            "iat_std": {"high": 0.5, "low": 0.0}
        }
        
        for feature, value in features.items():
            if feature not in self.feature_descriptions:
                continue
                
            status = "normal"
            reason = ""
            
            if feature in thresholds:
                if value > thresholds[feature]["high"]:
                    status = "suspicious_high"
                    reason = f"Unusually high {self.feature_descriptions[feature]}"
                elif value < thresholds[feature]["low"]:
                    status = "suspicious_low"
                    reason = f"Unusually low {self.feature_descriptions[feature]}"
            
            analysis[feature] = {
                "value": value,
                "description": self.feature_descriptions[feature],
                "status": status,
                "reason": reason
            }
        
        return analysis
    
    def _get_top_reasons(self, features: Dict[str, float], score: float) -> List[str]:
        """Extract top reasons for threat classification."""
        reasons = []
        
        # High packet count
        if features.get("pkts", 0) > 500:
            reasons.append(f"High packet count: {int(features['pkts'])} packets (possible DDoS)")
        
        # Large data transfer
        if features.get("bytes", 0) > 50000:
            reasons.append(f"Large data transfer: {int(features['bytes'])} bytes (possible exfiltration)")
        
        # Rapid connections
        if features.get("iat_avg", 1.0) < 0.01:
            reasons.append(f"Rapid connections: {features['iat_avg']:.4f}s average (possible scanning)")
        
        # High variability
        if features.get("iat_std", 0) > 0.3:
            reasons.append(f"Irregular timing: high variability (possible evasion technique)")
        
        # Model confidence
        if score > 0.9:
            reasons.append(f"ML model high confidence: {score:.2%}")
        elif score > 0.7:
            reasons.append(f"ML model moderate confidence: {score:.2%}")
        
        return reasons[:5]  # Top 5 reasons
    
    def _analyze_ti(self, ti_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze threat intelligence results."""
        ti_analysis = {
            "sources_checked": 0,
            "malicious_verdicts": 0,
            "reputation_score": 0.0,
            "findings": []
        }
        
        if not ti_results:
            return ti_analysis
        
        # Count sources and verdicts
        for source, result in ti_results.items():
            ti_analysis["sources_checked"] += 1
            
            if isinstance(result, dict):
                # Check for malicious indicators
                if result.get("malicious", False):
                    ti_analysis["malicious_verdicts"] += 1
                    ti_analysis["findings"].append(f"{source}: Flagged as malicious")
                
                # Extract reputation
                if "reputation" in result:
                    rep = result["reputation"]
                    if isinstance(rep, (int, float)):
                        ti_analysis["reputation_score"] += rep
                
                # Extract abuse score
                if "abuse_score" in result:
                    score = result["abuse_score"]
                    if score > 50:
                        ti_analysis["findings"].append(f"{source}: High abuse score ({score})")
        
        # Calculate average reputation
        if ti_analysis["sources_checked"] > 0:
            ti_analysis["reputation_score"] /= ti_analysis["sources_checked"]
        
        return ti_analysis
    
    def _get_ti_reasons(self, ti_results: Dict[str, Any]) -> List[str]:
        """Extract reasons from threat intelligence."""
        reasons = []
        
        for source, result in ti_results.items():
            if not isinstance(result, dict):
                continue
            
            # VirusTotal
            if source == "virustotal" and result.get("malicious"):
                reasons.append(f"VirusTotal: Known malicious IP")
            
            # AbuseIPDB
            if source == "abuseipdb":
                score = result.get("abuse_score", 0)
                if score > 75:
                    reasons.append(f"AbuseIPDB: High abuse score ({score}/100)")
            
            # OTX
            if source == "otx":
                pulses = result.get("pulses", 0)
                if pulses > 0:
                    reasons.append(f"AlienVault OTX: Found in {pulses} threat pulse(s)")
            
            # IPQualityScore
            if source == "ipqualityscore":
                if result.get("fraud_score", 0) > 75:
                    reasons.append(f"IPQualityScore: High fraud score")
            
            # GreyNoise
            if source == "greynoise":
                if result.get("classification") == "malicious":
                    reasons.append(f"GreyNoise: Known malicious scanner")
        
        return reasons
    
    def _calculate_confidence_breakdown(
        self,
        model_score: float,
        ti_results: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate confidence from different sources."""
        breakdown = {
            "ml_model": model_score,
            "threat_intelligence": 0.0,
            "behavioral": 0.0,
            "overall": model_score
        }
        
        if ti_results:
            # Calculate TI confidence
            malicious_count = sum(
                1 for r in ti_results.values()
                if isinstance(r, dict) and r.get("malicious", False)
            )
            total_sources = len(ti_results)
            
            if total_sources > 0:
                ti_confidence = malicious_count / total_sources
                breakdown["threat_intelligence"] = ti_confidence
                
                # Weighted overall confidence
                breakdown["overall"] = (
                    0.6 * model_score +
                    0.4 * ti_confidence
                )
        
        return breakdown
    
    def _generate_recommendations(
        self,
        alert: Dict[str, Any],
        features: Dict[str, float],
        ti_results: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        severity = alert.get("severity", "low")
        
        # Severity-based recommendations
        if severity == "high":
            recommendations.append("IMMEDIATE ACTION: Isolate affected systems")
            recommendations.append("Block source IP at firewall")
            recommendations.append("Initiate incident response procedure")
        elif severity == "medium":
            recommendations.append("Monitor source IP closely")
            recommendations.append("Consider rate limiting")
            recommendations.append("Review logs for related activity")
        else:
            recommendations.append("Continue monitoring")
            recommendations.append("Add to watchlist")
        
        # Feature-based recommendations
        if features.get("pkts", 0) > 1000:
            recommendations.append("Possible DDoS: Enable rate limiting")
        
        if features.get("bytes", 0) > 100000:
            recommendations.append("Large transfer detected: Check for data exfiltration")
        
        # TI-based recommendations
        if ti_results:
            malicious_sources = [
                source for source, result in ti_results.items()
                if isinstance(result, dict) and result.get("malicious", False)
            ]
            if len(malicious_sources) >= 2:
                recommendations.append(f"Multiple TI sources confirm threat: {', '.join(malicious_sources)}")
        
        return recommendations
    
    def generate_summary(self, explanation: Dict[str, Any]) -> str:
        """Generate human-readable summary."""
        summary_parts = [
            f"Alert {explanation['alert_id']} - Severity: {explanation['severity'].upper()}",
            f"Confidence: {explanation['confidence']:.1%}",
            "",
            "Top Reasons:"
        ]
        
        for i, reason in enumerate(explanation['top_reasons'][:3], 1):
            summary_parts.append(f"  {i}. {reason}")
        
        summary_parts.append("")
        summary_parts.append("Recommendations:")
        for i, rec in enumerate(explanation['recommendations'][:3], 1):
            summary_parts.append(f"  {i}. {rec}")
        
        return "\n".join(summary_parts)
