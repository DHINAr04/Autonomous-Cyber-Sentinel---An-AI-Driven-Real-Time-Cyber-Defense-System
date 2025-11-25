import os
from typing import Dict, Any, Optional
from sentinel.common.config import model_path, score_weights, severity_thresholds

try:
    import joblib as joblib_loader
except Exception:
    joblib_loader = None


class ModelRunner:
    def __init__(self) -> None:
        self._model = None
        path = model_path()
        if path and joblib_loader is not None and os.path.exists(path):
            try:
                self._model = joblib_loader.load(path)
            except Exception:
                self._model = None

        # If joblib isn't available but a model path exists, try Python's pickle as a fallback.
        if self._model is None:
            try:
                if path and os.path.exists(path):
                    import pickle

                    with open(path, "rb") as f:
                        self._model = pickle.load(f)
            except Exception:
                # keep model as None if pickle load fails
                self._model = self._model
        self._weights = score_weights()
        self._thr = severity_thresholds()

    def _heuristic_score(self, feats: Dict[str, float]) -> float:
        b = float(feats.get("bytes", 0.0))
        p = float(feats.get("pkts", 0.0))
        iat_avg = float(feats.get("iat_avg", 0.0))
        b_norm = min(1.0, b / 20000.0)
        p_norm = min(1.0, p / 200.0)
        iat_inv = 0.0 if iat_avg <= 0.0 else min(1.0, 1.0 / max(0.001, iat_avg))
        w = self._weights
        s = (w["bytes"] * b_norm) + (w["pkts"] * p_norm) + (w["iat_inv"] * iat_inv)
        return float(max(0.0, min(1.0, s)))

    def score(self, feats: Dict[str, float]) -> Dict[str, Any]:
        if self._model is not None:
            try:
                import numpy as np
                x = np.array([[feats.get("bytes", 0.0), feats.get("pkts", 0.0), feats.get("iat_avg", 0.0)]], dtype=float)
                if hasattr(self._model, "predict_proba"):
                    proba = self._model.predict_proba(x)[0]
                    sc = float(proba[-1])
                elif hasattr(self._model, "decision_function"):
                    val = float(self._model.decision_function(x)[0])
                    sc = 1.0 / (1.0 + pow(2.718281828, -val))
                else:
                    sc = self._heuristic_score(feats)
            except Exception:
                sc = self._heuristic_score(feats)
        else:
            sc = self._heuristic_score(feats)
        hi = self._thr["high"]
        mid = self._thr["medium"]
        sev = "high" if sc >= hi else ("medium" if sc >= mid else "low")
        conf = float(max(0.1, min(1.0, sc)))
        return {"score": sc, "severity": sev, "confidence": conf}