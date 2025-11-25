from sentinel.detection.model import ModelRunner


def test_model_runner_heuristic_score_range():
    mr = ModelRunner()
    feats = {"bytes": 5000.0, "pkts": 50.0, "iat_avg": 0.5}
    r = mr.score(feats)
    assert 0.0 <= r["score"] <= 1.0
    assert r["severity"] in {"low", "medium", "high"}
    assert 0.1 <= r["confidence"] <= 1.0