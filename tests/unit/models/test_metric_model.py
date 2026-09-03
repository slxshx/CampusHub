from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from campushub.models.metric import CreateMetric, UpdateMetric


def test_create_metric_with_valid_data():
    timestamp = datetime.now(timezone.utc)

    metric = CreateMetric(
        device_id=1,
        timestamp=timestamp,
        cpu_usage=42.5,
        ram_usage=63.2,
        storage_usage=37.8,
        temperature=51.4,
        uptime=86400,
    )

    assert metric.device_id == 1
    assert metric.timestamp == timestamp
    assert metric.cpu_usage == 42.5
    assert metric.ram_usage == 63.2
    assert metric.storage_usage == 37.8
    assert metric.temperature == 51.4
    assert metric.uptime == 86400


def test_create_metric_without_optional_metrics():
    metric = CreateMetric(
        device_id=1,
        timestamp=datetime.now(timezone.utc),
    )

    assert metric.cpu_usage is None
    assert metric.ram_usage is None
    assert metric.storage_usage is None
    assert metric.temperature is None
    assert metric.uptime is None


def test_create_metric_with_partial_metrics():
    metric = CreateMetric(
        device_id=1,
        timestamp=datetime.now(timezone.utc),
        cpu_usage=20.0,
        uptime=5000,
    )

    assert metric.cpu_usage == 20.0
    assert metric.uptime == 5000
    assert metric.ram_usage is None


@pytest.mark.parametrize(
    "test_data",
    [
        {
            "timestamp": datetime.now(timezone.utc),
        },
        {
            "device_id": 1,
        },
    ],
)
def test_create_metric_without_required_field_fails(test_data):
    with pytest.raises(ValidationError):
        CreateMetric(**test_data)


def test_update_metric_one_parameter():
    update_metric = UpdateMetric(
        cpu_usage=77.7
    )

    data = update_metric.model_dump(exclude_unset=True)

    assert data == {
        "cpu_usage": 77.7
    }


def test_update_metric_multiple_parameters():
    update_metric = UpdateMetric(
        cpu_usage=77.7,
        ram_usage=55.5,
        temperature=48.2,
    )

    data = update_metric.model_dump(exclude_unset=True)

    assert data == {
        "cpu_usage": 77.7,
        "ram_usage": 55.5,
        "temperature": 48.2,
    }


def test_update_metric_without_parameters():
    update_metric = UpdateMetric()

    data = update_metric.model_dump(exclude_unset=True)

    assert data == {}


def test_update_metric_explicit_none():
    update_metric = UpdateMetric(
        temperature=None
    )

    data = update_metric.model_dump(exclude_unset=True)

    assert data == {
        "temperature": None
    }
