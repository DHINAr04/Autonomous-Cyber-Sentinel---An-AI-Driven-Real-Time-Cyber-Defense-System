from sentinel.detection.features import FlowStats, FeatureExtractor


def test_flowstats_updates():
    fs = FlowStats()
    fs.update(500, ts=1.0)
    fs.update(500, ts=2.0)
    f = fs.features()
    assert f["bytes"] == 1000.0
    assert f["pkts"] == 2.0
    assert f["iat_avg"] == 1.0


def test_feature_extractor_flow_reset():
    fe = FeatureExtractor()
    fe.step("1.1.1.1", "2.2.2.2", "tcp", 1200, ts=1.0)
    fe.step("1.1.1.1", "2.2.2.2", "tcp", 800, ts=2.0)
    stats = fe.get("1.1.1.1", "2.2.2.2", "tcp")
    assert stats is not None
    fe.reset("1.1.1.1", "2.2.2.2", "tcp")
    assert fe.get("1.1.1.1", "2.2.2.2", "tcp") is None