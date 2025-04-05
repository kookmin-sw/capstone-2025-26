from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
import logging
from typing import Optional


# 34.66.130.204 or localhost
def init_telemetry(service_name: str, endpoint: str = "http://34.66.130.204:4317"):
    """Initialize OpenTelemetry with logging, metrics, and tracing"""
    resource = Resource.create({"service.name": service_name})
    
    # Logs
    log_provider = LoggerProvider(resource=resource)
    otlp_log_exporter = OTLPLogExporter(endpoint=endpoint, insecure=True)
    log_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
    set_logger_provider(log_provider)
    
    # Configure standard logging to use OTLP handler
    handler = LoggingHandler(level=logging.INFO, logger_provider=log_provider)
    logging.getLogger().addHandler(handler) 
    logging.getLogger().setLevel(logging.INFO) # Set root logger level
    logger = logging.getLogger(__name__) # Get logger after configuration
    LoggingInstrumentor().instrument(logger_provider=log_provider) # Use logger_provider argument
    
    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint, insecure=True)
    )
    metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(metric_provider)
    
    # Traces
    trace_provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(trace_provider)
    
    return logger

def instrument_django():
    """Instrument Django application with OpenTelemetry"""
    DjangoInstrumentor().instrument()

class RequestLoggingMiddleware:
    """Middleware to log all requests and responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)
    
    def __call__(self, request):
        # Log request
        self.logger.info(f"🔹 Request: {request.method} {request.get_full_path()}")
        
        # Get response
        response = self.get_response(request)
        
        # Log response
        self.logger.info(f"🔹 Response: {response.status_code} {request.get_full_path()}")
        
        return response
        