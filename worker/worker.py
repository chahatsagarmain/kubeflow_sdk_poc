import os
import sys
import time

# Add root directory to sys.path to allow importing kubeflow modules
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from kubeflow.common.telemetry import setup_telemetry, get_tracer, extract_context_from_env
from opentelemetry import trace

# Setup telemetry for worker subprocess
setup_telemetry("kubeflow-worker")
tracer = get_tracer(__name__)

def download_dataset(job_name: str):
    with tracer.start_as_current_span("Worker.download_dataset") as span:
        span.set_attribute("dataset.source", "s3://mock-bucket/data")
        time.sleep(0.5)

def train_model(job_name: str):
    with tracer.start_as_current_span("Worker.train_model") as span:
        span.set_attribute("model.type", "bert")
        span.add_event("Epoch 1/1 started")
        time.sleep(1.0)
        span.add_event("Epoch 1/1 completed")
        span.set_attribute("model.loss", 0.23)

def export_model(job_name: str):
    with tracer.start_as_current_span("Worker.export_model") as span:
        span.set_attribute("export.format", "saved_model")
        time.sleep(0.5)

def run_training_workload(job_name: str):
    # Extract context passed via environment variables from parent process
    context = extract_context_from_env(os.environ)

    # Attach this span to the extracted context (parent span)
    with tracer.start_as_current_span(
        "Worker.execute_training",
        context=context,
        kind=trace.SpanKind.INTERNAL
    ) as span:
        span.set_attribute("job.name", job_name)
        span.set_attribute("worker.pid", os.getpid())
        span.add_event("Training started")
        
        trace_id = span.get_span_context().trace_id
        print(f"[{trace_id:032x}] Worker executing for job: {job_name} ...")
        
        # Simulate local execution model workload
        download_dataset(job_name)
        train_model(job_name)
        export_model(job_name)
        
        span.add_event("Training completed")
        print(f"[{trace_id:032x}] Worker completed execution.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        job_name = sys.argv[1]
    else:
        job_name = "unknown_job"
        
    run_training_workload(job_name)
    
    # Force flush telemetry data before subprocess exit to prevent drops
    provider = trace.get_tracer_provider()
    provider.force_flush()
