
from logging import WARNING
from unittest import TestCase

from opentelemetry.sdk.metrics import MeterProvider

from opentelemetry.sdk.metrics.export import (
    InMemoryMetricExporter,
    PeriodicExportingMetricReader,
)

class TestMetricCardinalityLimit(TestCase):

    def setUp(self):
        self.exporter = InMemoryMetricExporter()
        self.reader = PeriodicExportingMetricReader(exporter=self.exporter, export_interval_millis=500)
        self.meter_provider = MeterProvider(metric_readers=[self.reader])
        self.meter = self.meter_provider.get_meter("test_meter")

    def test_metric_cardinality_limit(self):
        # Assuming a Counter type metric
        counter = self.meter.create_counter("cardinality_test_counter")

        # Generate and add more than 2000 unique labels
        for i in range(2100):
            label = {"key": f"value_{i}"}
            counter.add(1, label)

        # Simulate an export to get the metrics into the in-memory exporter
        self.reader.force_flush()

        # Retrieve the metrics from the in-memory exporter
        metric_data = self.exporter.metrics

        # Check if the length of the metric data doesn't exceed 2000
        self.assertTrue(len(metric_data) <= 2000)

        # Check if a warning or an error was logged
        with self.assertLogs(level=WARNING):
            counter.add(1, {"key": "value_2101"})
