import os
import importlib
import pytest

from sentinel.common import config
from sentinel.common.event_bus import BusFactory, InMemoryEventBus, RedisEventBus


def _reload_config() -> None:
    importlib.reload(config)


def test_defaults(monkeypatch):
    for k in ["BUS", "REDIS_URL", "SENTINEL_DB", "LIVE_CAPTURE", "CAPTURE_IFACE"]:
        monkeypatch.delenv(k, raising=False)
    _reload_config()
    assert config.bus_mode() == "memory"
    assert config.redis_url().startswith("redis://")
    assert config.sentinel_db().startswith("sqlite:///")
    assert config.live_capture_enabled() is False
    assert config.capture_iface() is None


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("BUS", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")
    monkeypatch.setenv("SENTINEL_DB", "sqlite:///test.db")
    monkeypatch.setenv("LIVE_CAPTURE", "1")
    monkeypatch.setenv("CAPTURE_IFACE", "eth0")
    _reload_config()
    assert config.bus_mode() == "redis"
    assert config.redis_url() == "redis://localhost:6379/1"
    assert config.sentinel_db() == "sqlite:///test.db"
    assert config.live_capture_enabled() is True
    assert config.capture_iface() == "eth0"


def test_bus_factory_memory(monkeypatch):
    monkeypatch.setenv("BUS", "memory")
    bus = BusFactory.from_env()
    assert isinstance(bus, InMemoryEventBus)


def test_bus_factory_redis(monkeypatch):
    monkeypatch.setenv("BUS", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    bus = BusFactory.from_env()
    assert isinstance(bus, (RedisEventBus, InMemoryEventBus))