import os
import pickle
import time
from sentinel.detection.model import ModelRunner


class DummyModel:
    """A tiny model object with predict_proba compatible API for ModelRunner.

    predict_proba expects an array-like X and returns probabilities for class 0 and 1.
    We'll return a high probability for the positive class when bytes or pkts are large.
    """

    def predict_proba(self, X):
        # X is a numpy array shape (n, 3) -> [bytes, pkts, iat_avg]
        out = []
        for row in X:
            b = float(row[0])
            p = float(row[1])
            score = min(1.0, (b / 20000.0) * 0.7 + (p / 200.0) * 0.3)
            out.append([1.0 - score, score])
        return out


def test_modelrunner_loads_joblib_model(tmp_path, monkeypatch):
    model_file = tmp_path / "dummy_model.joblib"
    # create and dump DummyModel using pickle (joblib optional)
    dm = DummyModel()
    with open(model_file, "wb") as f:
        pickle.dump(dm, f)

    # set MODEL_PATH env so ModelRunner will load it
    monkeypatch.setenv("MODEL_PATH", str(model_file))

    mr = ModelRunner()
    # craft features that should produce a meaningful score
    feats = {"bytes": 15000.0, "pkts": 100.0, "iat_avg": 0.05}
    out = mr.score(feats)
    assert isinstance(out, dict)
    assert "score" in out and "severity" in out and "confidence" in out
    assert 0.0 <= out["score"] <= 1.0