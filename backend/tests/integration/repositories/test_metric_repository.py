from campushub.models.metric import UpdateMetric
from campushub.repositories.metric_repository import MetricRepository


def test_create_metric(test_metric):
    assert test_metric.id is not None
    assert test_metric.cpu_usage == 25.5
    assert test_metric.ram_usage == 50.0
    assert test_metric.storage_usage == 75.0
    assert test_metric.temperature == 42.0
    assert test_metric.uptime == 12345


def test_get_all_metrics(test_metric):
    repository = MetricRepository()

    result = repository.get_all_metrics()

    assert isinstance(result, list)
    assert any(metric.id == test_metric.id for metric in result)


def test_get_metric_by_id(test_metric):
    repository = MetricRepository()

    result = repository.get_metric_by_id(test_metric.id)

    assert result is not None
    assert result.id == test_metric.id


def test_update_metric(test_metric):
    repository = MetricRepository()

    update_metric = UpdateMetric(
        cpu_usage=80.0,
        ram_usage=70.0,
        storage_usage=60.0,
        temperature=55.5,
        uptime=54321,
    )

    result = repository.update_metric(
        test_metric.id,
        update_metric,
    )

    assert result is True

    new_test_metric = repository.get_metric_by_id(test_metric.id)

    assert new_test_metric is not None
    assert new_test_metric.cpu_usage == 80.0
    assert new_test_metric.ram_usage == 70.0
    assert new_test_metric.storage_usage == 60.0
    assert new_test_metric.temperature == 55.5
    assert new_test_metric.uptime == 54321


def test_delete_metric(test_metric):
    repository = MetricRepository()

    result = repository.delete_metric(test_metric.id)

    assert result is True

    is_metric_deleted = repository.get_metric_by_id(test_metric.id)

    assert is_metric_deleted is None
