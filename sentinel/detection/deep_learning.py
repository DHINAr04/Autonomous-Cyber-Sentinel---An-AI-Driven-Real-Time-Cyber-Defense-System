"""Deep learning models for advanced threat detection."""
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import deque

logger = logging.getLogger(__name__)


class LSTMThreatDetector:
    """LSTM-based sequential threat detection for multi-stage attacks."""
    
    def __init__(self, sequence_length: int = 10, hidden_size: int = 64):
        """
        Initialize LSTM threat detector.
        
        Args:
            sequence_length: Number of packets to consider in sequence
            hidden_size: LSTM hidden layer size
        """
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.model = None
        self.scaler = None
        self.sequence_buffer: Dict[str, deque] = {}
        
        logger.info(f"Initializing LSTM detector (seq_len={sequence_length}, hidden={hidden_size})")
        self._build_model()
    
    def _build_model(self) -> None:
        """Build LSTM model architecture."""
        try:
            import tensorflow as tf
            from tensorflow import keras
            from tensorflow.keras import layers
            
            # Simple LSTM architecture for threat detection
            self.model = keras.Sequential([
                layers.Input(shape=(self.sequence_length, 6)),  # 6 features
                layers.LSTM(self.hidden_size, return_sequences=True),
                layers.Dropout(0.2),
                layers.LSTM(32),
                layers.Dropout(0.2),
                layers.Dense(16, activation='relu'),
                layers.Dense(1, activation='sigmoid')  # Binary classification
            ])
            
            self.model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy', 'precision', 'recall']
            )
            
            logger.info("LSTM model built successfully")
            
        except ImportError:
            logger.warning("TensorFlow not available, using fallback detection")
            self.model = None
    
    def update_sequence(self, flow_id: str, features: Dict[str, float]) -> None:
        """
        Update sequence buffer for a flow.
        
        Args:
            flow_id: Unique flow identifier (src_ip:dst_ip:proto)
            features: Feature dictionary
        """
        if flow_id not in self.sequence_buffer:
            self.sequence_buffer[flow_id] = deque(maxlen=self.sequence_length)
        
        # Extract feature vector
        feature_vector = [
            features.get('bytes', 0),
            features.get('pkts', 0),
            features.get('iat_avg', 0),
            features.get('iat_std', 0),
            features.get('iat_max', 0),
            features.get('iat_min', 0)
        ]
        
        self.sequence_buffer[flow_id].append(feature_vector)
    
    def detect_sequential_threat(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """
        Detect threats in sequential traffic patterns.
        
        Args:
            flow_id: Flow identifier
            
        Returns:
            Detection result with score and pattern type
        """
        if flow_id not in self.sequence_buffer:
            return None
        
        sequence = list(self.sequence_buffer[flow_id])
        
        # Need full sequence for detection
        if len(sequence) < self.sequence_length:
            return None
        
        # Use LSTM model if available
        if self.model is not None:
            return self._lstm_detection(sequence)
        else:
            return self._fallback_detection(sequence)
    
    def _lstm_detection(self, sequence: List[List[float]]) -> Dict[str, Any]:
        """LSTM-based detection."""
        try:
            import numpy as np
            
            # Prepare input
            X = np.array(sequence).reshape(1, self.sequence_length, 6)
            
            # Normalize
            if self.scaler is None:
                from sklearn.preprocessing import StandardScaler
                self.scaler = StandardScaler()
                X_flat = X.reshape(-1, 6)
                self.scaler.fit(X_flat)
            
            X_normalized = self.scaler.transform(X.reshape(-1, 6)).reshape(1, self.sequence_length, 6)
            
            # Predict
            score = float(self.model.predict(X_normalized, verbose=0)[0][0])
            
            # Analyze pattern
            pattern_type = self._analyze_pattern(sequence)
            
            return {
                'score': score,
                'pattern_type': pattern_type,
                'confidence': score,
                'method': 'lstm',
                'sequence_length': len(sequence)
            }
            
        except Exception as e:
            logger.error(f"LSTM detection error: {e}")
            return self._fallback_detection(sequence)
    
    def _fallback_detection(self, sequence: List[List[float]]) -> Dict[str, Any]:
        """Fallback detection using statistical analysis."""
        # Analyze sequence patterns
        bytes_seq = [s[0] for s in sequence]
        pkts_seq = [s[1] for s in sequence]
        iat_seq = [s[2] for s in sequence]
        
        # Detect anomalies
        score = 0.0
        pattern_type = "normal"
        
        # Check for rapid escalation (APT behavior)
        if self._is_escalating(bytes_seq):
            score += 0.3
            pattern_type = "escalation"
        
        # Check for beaconing (C2 communication)
        if self._is_beaconing(iat_seq):
            score += 0.4
            pattern_type = "beaconing"
        
        # Check for port scanning
        if self._is_scanning(pkts_seq):
            score += 0.3
            pattern_type = "scanning"
        
        return {
            'score': min(score, 1.0),
            'pattern_type': pattern_type,
            'confidence': 0.7,
            'method': 'statistical',
            'sequence_length': len(sequence)
        }
    
    def _analyze_pattern(self, sequence: List[List[float]]) -> str:
        """Analyze sequence for specific attack patterns."""
        bytes_seq = [s[0] for s in sequence]
        iat_seq = [s[2] for s in sequence]
        
        if self._is_beaconing(iat_seq):
            return "beaconing"
        elif self._is_escalating(bytes_seq):
            return "escalation"
        elif self._is_scanning([s[1] for s in sequence]):
            return "scanning"
        else:
            return "unknown"
    
    def _is_escalating(self, values: List[float]) -> bool:
        """Check if values show escalating pattern."""
        if len(values) < 3:
            return False
        
        increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
        return increases / len(values) > 0.7
    
    def _is_beaconing(self, iat_values: List[float]) -> bool:
        """Check for regular beaconing pattern (C2 communication)."""
        if len(iat_values) < 5:
            return False
        
        # Calculate coefficient of variation
        mean_iat = np.mean(iat_values)
        std_iat = np.std(iat_values)
        
        if mean_iat == 0:
            return False
        
        cv = std_iat / mean_iat
        
        # Low coefficient of variation indicates regular intervals
        return cv < 0.3
    
    def _is_scanning(self, pkt_counts: List[float]) -> bool:
        """Check for scanning pattern."""
        if len(pkt_counts) < 3:
            return False
        
        # Many small packet bursts indicate scanning
        small_bursts = sum(1 for p in pkt_counts if p < 10)
        return small_bursts / len(pkt_counts) > 0.7


class TransformerAnomalyDetector:
    """Transformer-based anomaly detection for complex patterns."""
    
    def __init__(self, d_model: int = 64, nhead: int = 4, num_layers: int = 2):
        """
        Initialize Transformer detector.
        
        Args:
            d_model: Model dimension
            nhead: Number of attention heads
            num_layers: Number of transformer layers
        """
        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        self.model = None
        
        logger.info(f"Initializing Transformer detector (d_model={d_model}, heads={nhead})")
        self._build_model()
    
    def _build_model(self) -> None:
        """Build Transformer model."""
        try:
            import torch
            import torch.nn as nn
            
            class TransformerDetector(nn.Module):
                def __init__(self, d_model, nhead, num_layers):
                    super().__init__()
                    self.embedding = nn.Linear(6, d_model)
                    encoder_layer = nn.TransformerEncoderLayer(
                        d_model=d_model,
                        nhead=nhead,
                        dim_feedforward=d_model * 4,
                        dropout=0.1
                    )
                    self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
                    self.classifier = nn.Linear(d_model, 1)
                    self.sigmoid = nn.Sigmoid()
                
                def forward(self, x):
                    x = self.embedding(x)
                    x = self.transformer(x)
                    x = x.mean(dim=0)  # Global average pooling
                    x = self.classifier(x)
                    return self.sigmoid(x)
            
            self.model = TransformerDetector(self.d_model, self.nhead, self.num_layers)
            logger.info("Transformer model built successfully")
            
        except ImportError:
            logger.warning("PyTorch not available, using fallback")
            self.model = None
    
    def detect_anomaly(self, sequence: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Detect anomalies using self-attention mechanism.
        
        Args:
            sequence: List of feature dictionaries
            
        Returns:
            Detection result
        """
        if self.model is not None:
            return self._transformer_detection(sequence)
        else:
            return self._attention_fallback(sequence)
    
    def _transformer_detection(self, sequence: List[Dict[str, float]]) -> Dict[str, Any]:
        """Transformer-based detection."""
        try:
            import torch
            
            # Convert to tensor
            features = [[
                s.get('bytes', 0),
                s.get('pkts', 0),
                s.get('iat_avg', 0),
                s.get('iat_std', 0),
                s.get('iat_max', 0),
                s.get('iat_min', 0)
            ] for s in sequence]
            
            X = torch.tensor(features, dtype=torch.float32)
            
            # Predict
            with torch.no_grad():
                score = float(self.model(X))
            
            return {
                'score': score,
                'method': 'transformer',
                'attention_weights': None,  # Could extract attention weights
                'confidence': score
            }
            
        except Exception as e:
            logger.error(f"Transformer detection error: {e}")
            return self._attention_fallback(sequence)
    
    def _attention_fallback(self, sequence: List[Dict[str, float]]) -> Dict[str, Any]:
        """Fallback using simple attention mechanism."""
        if not sequence:
            return {'score': 0.0, 'method': 'fallback', 'confidence': 0.0}
        
        # Calculate attention scores based on deviation from mean
        features = ['bytes', 'pkts', 'iat_avg']
        attention_scores = []
        
        for feature in features:
            values = [s.get(feature, 0) for s in sequence]
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            if std_val > 0:
                # Normalized deviations
                deviations = [(v - mean_val) / std_val for v in values]
                attention_scores.extend(deviations)
        
        # Anomaly score based on attention
        if attention_scores:
            anomaly_score = min(np.mean(np.abs(attention_scores)) / 3, 1.0)
        else:
            anomaly_score = 0.0
        
        return {
            'score': anomaly_score,
            'method': 'attention_fallback',
            'confidence': 0.6
        }


class DeepLearningEnsemble:
    """Ensemble of deep learning models for robust detection."""
    
    def __init__(self):
        self.lstm_detector = LSTMThreatDetector()
        self.transformer_detector = TransformerAnomalyDetector()
        logger.info("Deep learning ensemble initialized")
    
    def detect(self, flow_id: str, features: Dict[str, float], 
               sequence: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Ensemble detection combining LSTM and Transformer.
        
        Args:
            flow_id: Flow identifier
            features: Current features
            sequence: Historical sequence
            
        Returns:
            Combined detection result
        """
        # Update LSTM sequence
        self.lstm_detector.update_sequence(flow_id, features)
        
        # Get LSTM detection
        lstm_result = self.lstm_detector.detect_sequential_threat(flow_id)
        
        # Get Transformer detection
        transformer_result = self.transformer_detector.detect_anomaly(sequence)
        
        # Ensemble voting
        if lstm_result and transformer_result:
            ensemble_score = (
                0.6 * lstm_result['score'] +
                0.4 * transformer_result['score']
            )
            
            return {
                'score': ensemble_score,
                'lstm_score': lstm_result['score'],
                'transformer_score': transformer_result['score'],
                'pattern_type': lstm_result.get('pattern_type', 'unknown'),
                'method': 'ensemble',
                'confidence': (lstm_result['confidence'] + transformer_result['confidence']) / 2
            }
        elif lstm_result:
            return lstm_result
        elif transformer_result:
            return transformer_result
        else:
            return {'score': 0.0, 'method': 'none', 'confidence': 0.0}
