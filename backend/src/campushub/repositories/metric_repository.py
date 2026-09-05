from campushub.models.metric import Metric, CreateMetric, UpdateMetric
from ..repositories.base_repository import BaseRepository

class MetricRepository(BaseRepository):
    def get_all_metrics(self) -> list[Metric]:
        return self.get_all(Metric, Metric.TABLE_NAME)

    def get_metric_by_id(self, entity_id: int) -> Metric | None:
        return self.get_by_id(entity_id, Metric, Metric.TABLE_NAME)

    def create_metric(self, create_metric: CreateMetric) -> Metric | None:
        return self.create(create_metric, Metric, Metric.TABLE_NAME)

    def update_metric(self, entity_id: int, update_metric: UpdateMetric) -> bool:
        return self.update(entity_id, update_metric, Metric.TABLE_NAME)

    def delete_metric(self, entity_id: int) -> bool:
        return self.delete_by_id(entity_id, Metric.TABLE_NAME)






