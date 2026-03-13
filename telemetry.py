import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.propagate import inject, extract
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

def setup_telemetry(service_name: str):
    """Initializes OpenTelemetry tracing with OTLP exporter to Jaeger."""
    resource = Resource(attributes={
        "service.name": service_name
    })

    provider = TracerProvider(resource=resource)
    
    # Configure OTLP Exporter - Default Jaeger OTLP port is 4318 for HTTP
    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

def get_tracer(module_name: str):
    """Gets a tracer instance for the specified module."""
    return trace.get_tracer(module_name)

def get_context_env() -> dict:
    """Injects the current trace context into an environment dictionary."""
    env = {}
    TraceContextTextMapPropagator().inject(carrier=env)
    return env

def extract_context_from_env(env_dict: dict):
    """Extracts trace context from an environment dictionary."""
    return TraceContextTextMapPropagator().extract(carrier=env_dict)
