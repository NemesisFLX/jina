import time

import pytest

from jina import Client, Flow
from tests.integration.instrumentation import (
    ExecutorTestWithTracing,
    get_services,
    get_trace_ids,
    get_traces,
    partition_spans_by_kind,
)


@pytest.mark.skip
def test_http_gateway_instrumentation(otlp_collector):
    f = Flow(
        protocol='grpc',
        opentelemetry_tracing=True,
        span_exporter_host='localhost',
        span_exporter_port=4317,
    ).add(
        uses=ExecutorTestWithTracing,
        opentelemetry_tracing=True,
        span_exporter_host='localhost',
        span_exporter_port=4317,
    )

    with f:
        # f.post(
        #     f'/index',
        #     {'data': [{'text': 'text_input'}]},
        # )
        # give some time for the tracing and metrics exporters to finish exporting.
        # the client is slow to export the data
        time.sleep(8)

    services = get_services()
    expected_services = ['executor0/rep-0', 'gateway/rep-0', 'HTTPClient']
    assert len(services) == 3
    assert set(services).issubset(expected_services)

    client_traces = get_traces('HTTPClient')
    (server_spans, client_spans, internal_spans) = partition_spans_by_kind(
        client_traces
    )
    assert len(server_spans) == 5
    assert len(client_spans) == 5
    assert len(internal_spans) == 4

    trace_ids = get_trace_ids(client_traces)
    assert len(trace_ids) == 1
