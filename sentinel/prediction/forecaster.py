"""AI-powered threat prediction and forecasting."""
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import time

logger = logging.getLogger(__name__)


class ThreatForecaster:
    """Predict future attacks using time series analysis."""
    
    def __init__(self, history_window: int = 7 * 24):  # 7 days of hourly data
        """
        Initialize threat forecaster.
        
        Args:
            history_window: Number of time periods to keep in history
        """
        self.history_window = history_window
        self.threat_history: deque = deque(maxlen=history_window)
        self.model = None
        
        logger.info(f"Threat forecaster initialized (window={history_window}h)")
        self._init_model()
    
    def _init_model(self) -> None:
        """Initialize forecasting model."""
        try:
            from prophet import Prophet
            self.model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False
            )
            logger.info("Prophet model initialized")
        except ImportError:
            logger.warning("Prophet not available, using statistical fallback")
            self.model = None
    
    def update_history(self, timestamp: float, threat_count: int, 
                       threat_types: Dict[str, int]) -> None:
        """
        Update threat history with new data point.
        
        Args:
            timestamp: Unix timestamp
            threat_count: Number of threats detected
            threat_types: Dictionary of threat type -> count
        """
        self.threat_history.append({
            'timestamp': timestamp,
            'threat_count': threat_count,
            'threat_types': threat_types,
            'hour': datetime.fromtimestamp(timestamp).hour,
            'day_of_week': datetime.fromtimestamp(timestamp).weekday()
        })
    
    def predict_attack_likelihood(self, time_window: str = '24h') -> Dict[str, Any]:
        """
        Predict probability of attack in specified time window.
        
        Args:
            time_window: Time window for prediction (e.g., '24h', '1w')
            
        Returns:
            Prediction dictionary with probability and recommendations
        """
        if len(self.threat_history) < 24:  # Need at least 24 hours of data
            return {
                'attack_probability': 0.5,
                'confidence': 'low',
                'reason': 'Insufficient historical data',
                'likely_attack_types': [],
                'recommended_actions': ['Continue monitoring', 'Collect more data']
            }
        
        # Extract features
        features = self.extract_predictive_features()
        
        # Make prediction
        if self.model is not None:
            prediction = self._prophet_forecast(features, time_window)
        else:
            prediction = self._statistical_forecast(features, time_window)
        
        # Add recommendations
        prediction['recommended_actions'] = self._generate_recommendations(prediction)
        
        return prediction
    
    def extract_predictive_features(self) -> Dict[str, Any]:
        """Extract features for prediction."""
        if not self.threat_history:
            return {}
        
        recent_data = list(self.threat_history)
        
        # Time-based features
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        # Threat count statistics
        threat_counts = [d['threat_count'] for d in recent_data]
        
        # Trend analysis
        if len(threat_counts) >= 2:
            recent_trend = np.mean(threat_counts[-24:]) if len(threat_counts) >= 24 else np.mean(threat_counts)
            historical_avg = np.mean(threat_counts)
            trend_direction = 'increasing' if recent_trend > historical_avg else 'decreasing'
        else:
            trend_direction = 'stable'
            recent_trend = 0
            historical_avg = 0
        
        # Peak hours analysis
        hourly_counts = {}
        for d in recent_data:
            hour = d['hour']
            hourly_counts[hour] = hourly_counts.get(hour, 0) + d['threat_count']
        
        peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hours = [h for h, _ in peak_hours]
        
        # Threat type distribution
        threat_type_totals = {}
        for d in recent_data:
            for threat_type, count in d['threat_types'].items():
                threat_type_totals[threat_type] = threat_type_totals.get(threat_type, 0) + count
        
        return {
            'current_hour': current_hour,
            'current_day': current_day,
            'trend_direction': trend_direction,
            'recent_avg': recent_trend,
            'historical_avg': historical_avg,
            'peak_hours': peak_hours,
            'threat_type_distribution': threat_type_totals,
            'data_points': len(recent_data)
        }
    
    def _prophet_forecast(self, features: Dict[str, Any], time_window: str) -> Dict[str, Any]:
        """Forecast using Prophet model."""
        try:
            import pandas as pd
            
            # Prepare data for Prophet
            df = pd.DataFrame([
                {
                    'ds': datetime.fromtimestamp(d['timestamp']),
                    'y': d['threat_count']
                }
                for d in self.threat_history
            ])
            
            # Fit model
            self.model.fit(df)
            
            # Make forecast
            hours = int(time_window.replace('h', '').replace('d', '')) if 'h' in time_window else 24
            future = self.model.make_future_dataframe(periods=hours, freq='H')
            forecast = self.model.predict(future)
            
            # Get prediction for time window
            future_predictions = forecast.tail(hours)
            predicted_threats = future_predictions['yhat'].sum()
            
            # Calculate probability
            historical_avg = features['historical_avg'] * hours
            attack_probability = min(predicted_threats / (historical_avg + 1), 1.0)
            
            # Identify likely attack types
            likely_types = self._predict_attack_types(features)
            
            return {
                'attack_probability': attack_probability,
                'confidence': 'high',
                'predicted_threats': int(predicted_threats),
                'likely_attack_types': likely_types,
                'forecast_window': time_window,
                'method': 'prophet'
            }
            
        except Exception as e:
            logger.error(f"Prophet forecast failed: {e}")
            return self._statistical_forecast(features, time_window)
    
    def _statistical_forecast(self, features: Dict[str, Any], time_window: str) -> Dict[str, Any]:
        """Fallback statistical forecast."""
        current_hour = features['current_hour']
        peak_hours = features['peak_hours']
        trend = features['trend_direction']
        
        # Base probability
        base_prob = 0.3
        
        # Adjust for peak hours
        if current_hour in peak_hours:
            base_prob += 0.2
        
        # Adjust for trend
        if trend == 'increasing':
            base_prob += 0.3
        elif trend == 'decreasing':
            base_prob -= 0.1
        
        # Adjust for historical patterns
        if features['recent_avg'] > features['historical_avg'] * 1.5:
            base_prob += 0.2
        
        attack_probability = min(max(base_prob, 0.0), 1.0)
        
        # Predict likely attack types
        likely_types = self._predict_attack_types(features)
        
        return {
            'attack_probability': attack_probability,
            'confidence': 'medium',
            'likely_attack_types': likely_types,
            'forecast_window': time_window,
            'method': 'statistical'
        }
    
    def _predict_attack_types(self, features: Dict[str, Any]) -> List[str]:
        """Predict most likely attack types."""
        threat_dist = features.get('threat_type_distribution', {})
        
        if not threat_dist:
            return ['Unknown']
        
        # Sort by frequency
        sorted_types = sorted(threat_dist.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 3
        return [t for t, _ in sorted_types[:3]]
    
    def _generate_recommendations(self, prediction: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on prediction."""
        recommendations = []
        
        probability = prediction['attack_probability']
        likely_types = prediction.get('likely_attack_types', [])
        
        if probability > 0.7:
            recommendations.append("HIGH ALERT: Increase monitoring and alerting")
            recommendations.append("Notify security team of elevated threat level")
            recommendations.append("Review and update firewall rules")
            recommendations.append("Enable additional logging")
        elif probability > 0.5:
            recommendations.append("MODERATE ALERT: Increase monitoring")
            recommendations.append("Review recent security events")
            recommendations.append("Verify backup systems are operational")
        else:
            recommendations.append("Continue normal monitoring")
            recommendations.append("Maintain current security posture")
        
        # Type-specific recommendations
        if 'DDoS' in likely_types or 'ddos' in str(likely_types).lower():
            recommendations.append("Prepare DDoS mitigation: Enable rate limiting")
        
        if 'Phishing' in likely_types or 'phishing' in str(likely_types).lower():
            recommendations.append("Alert users about potential phishing campaigns")
        
        if 'Malware' in likely_types or 'malware' in str(likely_types).lower():
            recommendations.append("Update antivirus definitions")
            recommendations.append("Scan critical systems")
        
        return recommendations
    
    def get_threat_trends(self, period: str = '7d') -> Dict[str, Any]:
        """Get threat trends over specified period."""
        if not self.threat_history:
            return {'trend': 'unknown', 'data_points': 0}
        
        recent_data = list(self.threat_history)
        
        # Calculate trend
        threat_counts = [d['threat_count'] for d in recent_data]
        
        if len(threat_counts) < 2:
            return {'trend': 'insufficient_data', 'data_points': len(threat_counts)}
        
        # Linear regression for trend
        x = np.arange(len(threat_counts))
        y = np.array(threat_counts)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.1:
            trend = 'increasing'
        elif slope < -0.1:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'slope': float(slope),
            'current_avg': float(np.mean(threat_counts[-24:])) if len(threat_counts) >= 24 else float(np.mean(threat_counts)),
            'historical_avg': float(np.mean(threat_counts)),
            'data_points': len(threat_counts)
        }
    
    def export_forecast_report(self, filepath: str = 'threat_forecast.json') -> None:
        """Export forecast report to file."""
        import json
        
        prediction = self.predict_attack_likelihood('24h')
        trends = self.get_threat_trends('7d')
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'prediction': prediction,
            'trends': trends,
            'history_size': len(self.threat_history)
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Forecast report exported to {filepath}")
