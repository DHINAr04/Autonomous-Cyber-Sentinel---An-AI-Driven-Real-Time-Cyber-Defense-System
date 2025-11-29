"""Behavioral baselining for adaptive threat detection."""
import logging
import time
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class BehaviorBaseline:
    """Learn and track normal behavior patterns for entities."""
    
    def __init__(self, learning_window: int = 3600, history_size: int = 1000):
        """
        Initialize behavioral baseline tracker.
        
        Args:
            learning_window: Time window in seconds for baseline learning
            history_size: Number of historical events to keep per entity
        """
        self.learning_window = learning_window
        self.history_size = history_size
        
        # Entity baselines: entity_id -> baseline_profile
        self.baselines: Dict[str, Dict[str, Any]] = {}
        
        # Historical data: entity_id -> deque of events
        self.history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        
        # Learning status
        self.learning_complete: Dict[str, bool] = {}
        self.first_seen: Dict[str, float] = {}
        
        logger.info(f"Initialized BehaviorBaseline with {learning_window}s learning window")
    
    def update(self, entity_id: str, event: Dict[str, Any]) -> None:
        """
        Update behavioral baseline with new event.
        
        Args:
            entity_id: Unique identifier for entity (e.g., IP address)
            event: Event dictionary with traffic characteristics
        """
        # Track first seen time
        if entity_id not in self.first_seen:
            self.first_seen[entity_id] = time.time()
            logger.debug(f"New entity detected: {entity_id}")
        
        # Add to history
        self.history[entity_id].append(event)
        
        # Check if learning period is complete
        if not self.learning_complete.get(entity_id, False):
            elapsed = time.time() - self.first_seen[entity_id]
            if elapsed >= self.learning_window:
                self._build_baseline(entity_id)
                self.learning_complete[entity_id] = True
                logger.info(f"Baseline learning complete for {entity_id}")
    
    def _build_baseline(self, entity_id: str) -> None:
        """Build baseline profile from historical data."""
        events = list(self.history[entity_id])
        
        if not events:
            return
        
        # Extract features from events
        bytes_list = [e.get("size", 0) for e in events]
        timestamps = [e.get("ts", 0) for e in events]
        protocols = [e.get("proto", "") for e in events]
        ports = [e.get("dport", 0) for e in events]
        
        # Calculate statistics
        baseline = {
            "entity_id": entity_id,
            "sample_size": len(events),
            "time_range": {
                "start": min(timestamps) if timestamps else 0,
                "end": max(timestamps) if timestamps else 0
            },
            "bytes": {
                "mean": statistics.mean(bytes_list) if bytes_list else 0,
                "median": statistics.median(bytes_list) if bytes_list else 0,
                "stdev": statistics.stdev(bytes_list) if len(bytes_list) > 1 else 0,
                "min": min(bytes_list) if bytes_list else 0,
                "max": max(bytes_list) if bytes_list else 0
            },
            "protocols": self._calculate_distribution(protocols),
            "ports": self._calculate_distribution(ports),
            "activity_hours": self._calculate_activity_hours(timestamps),
            "connection_rate": self._calculate_connection_rate(timestamps)
        }
        
        self.baselines[entity_id] = baseline
        logger.debug(f"Built baseline for {entity_id}: {baseline}")
    
    def _calculate_distribution(self, values: List[Any]) -> Dict[Any, float]:
        """Calculate distribution of values."""
        if not values:
            return {}
        
        total = len(values)
        counts = defaultdict(int)
        
        for value in values:
            counts[value] += 1
        
        return {k: v / total for k, v in counts.items()}
    
    def _calculate_activity_hours(self, timestamps: List[float]) -> List[int]:
        """Calculate typical activity hours."""
        if not timestamps:
            return []
        
        from datetime import datetime
        hours = [datetime.fromtimestamp(ts).hour for ts in timestamps]
        
        # Find hours with activity
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        # Return hours with significant activity (>10% of total)
        threshold = len(hours) * 0.1
        return sorted([h for h, count in hour_counts.items() if count > threshold])
    
    def _calculate_connection_rate(self, timestamps: List[float]) -> float:
        """Calculate average connections per minute."""
        if len(timestamps) < 2:
            return 0.0
        
        time_span = max(timestamps) - min(timestamps)
        if time_span == 0:
            return 0.0
        
        return (len(timestamps) / time_span) * 60  # connections per minute
    
    def detect_anomaly(self, entity_id: str, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect if event deviates from baseline behavior.
        
        Args:
            entity_id: Entity identifier
            event: Current event to check
            
        Returns:
            Anomaly report if detected, None otherwise
        """
        # Check if baseline exists and learning is complete
        if entity_id not in self.baselines or not self.learning_complete.get(entity_id, False):
            return None
        
        baseline = self.baselines[entity_id]
        anomalies = []
        deviation_score = 0.0
        
        # Check byte size deviation
        event_bytes = event.get("size", 0)
        baseline_bytes = baseline["bytes"]
        
        if baseline_bytes["stdev"] > 0:
            z_score = abs(event_bytes - baseline_bytes["mean"]) / baseline_bytes["stdev"]
            if z_score > 3:  # 3 standard deviations
                anomalies.append(f"Unusual data size: {event_bytes} bytes (z-score: {z_score:.2f})")
                deviation_score += z_score / 10
        
        # Check protocol deviation
        event_proto = event.get("proto", "")
        if event_proto and event_proto not in baseline["protocols"]:
            anomalies.append(f"Unusual protocol: {event_proto}")
            deviation_score += 0.3
        elif event_proto:
            expected_freq = baseline["protocols"].get(event_proto, 0)
            if expected_freq < 0.05:  # Less than 5% of normal traffic
                anomalies.append(f"Rare protocol usage: {event_proto}")
                deviation_score += 0.2
        
        # Check port deviation
        event_port = event.get("dport", 0)
        if event_port and event_port not in baseline["ports"]:
            anomalies.append(f"Unusual destination port: {event_port}")
            deviation_score += 0.2
        
        # Check activity time
        from datetime import datetime
        event_hour = datetime.fromtimestamp(event.get("ts", time.time())).hour
        if baseline["activity_hours"] and event_hour not in baseline["activity_hours"]:
            anomalies.append(f"Activity outside normal hours: {event_hour}:00")
            deviation_score += 0.3
        
        # Check connection rate
        recent_events = list(self.history[entity_id])[-10:]  # Last 10 events
        if len(recent_events) >= 2:
            recent_timestamps = [e.get("ts", 0) for e in recent_events]
            recent_rate = self._calculate_connection_rate(recent_timestamps)
            baseline_rate = baseline["connection_rate"]
            
            if baseline_rate > 0 and recent_rate > baseline_rate * 3:
                anomalies.append(f"High connection rate: {recent_rate:.1f}/min (baseline: {baseline_rate:.1f}/min)")
                deviation_score += 0.4
        
        # Return anomaly report if significant deviation
        if anomalies and deviation_score > 0.5:
            return {
                "entity_id": entity_id,
                "anomalies": anomalies,
                "deviation_score": min(deviation_score, 1.0),
                "severity": self._calculate_severity(deviation_score),
                "baseline_summary": {
                    "typical_bytes": baseline_bytes["mean"],
                    "typical_protocols": list(baseline["protocols"].keys()),
                    "typical_hours": baseline["activity_hours"],
                    "typical_rate": baseline["connection_rate"]
                }
            }
        
        return None
    
    def _calculate_severity(self, deviation_score: float) -> str:
        """Calculate severity based on deviation score."""
        if deviation_score >= 0.8:
            return "high"
        elif deviation_score >= 0.5:
            return "medium"
        else:
            return "low"
    
    def get_baseline(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get baseline profile for entity."""
        return self.baselines.get(entity_id)
    
    def is_learning(self, entity_id: str) -> bool:
        """Check if entity is still in learning phase."""
        if entity_id not in self.first_seen:
            return True
        
        elapsed = time.time() - self.first_seen[entity_id]
        return elapsed < self.learning_window
    
    def get_stats(self) -> Dict[str, Any]:
        """Get behavioral baseline statistics."""
        return {
            "total_entities": len(self.baselines),
            "learning_entities": sum(1 for e in self.first_seen if self.is_learning(e)),
            "baseline_complete": sum(1 for v in self.learning_complete.values() if v),
            "total_events": sum(len(h) for h in self.history.values())
        }
