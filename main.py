import sys
import os

# Add the current directory to path if needed, so it can import telemetry
sys.path.insert(0, os.path.dirname(__file__))

from telemetry import setup_telemetry, get_tracer
from trainer_client import TrainerClient
from opentelemetry import trace
import time

def main():
    # Setup global telemetry for the SDK caller entrypoint
    setup_telemetry("kubeflow-sdk")
    tracer = get_tracer(__name__)
    
    with tracer.start_as_current_span("SDK.UserScript") as span:
        trace_id = span.get_span_context().trace_id
        print(f"[{trace_id:032x}] Main Script started.")
        span.add_event("Initialize TrainerClient")
        
        client = TrainerClient()
        
        print(f"[{trace_id:032x}] Calling create_training_job...")
        client.create_training_job("bert-fine-tuning-poc")
        
    print("Flushing SDK telemetry...")
    provider = trace.get_tracer_provider()
    provider.force_flush()
    # Sleep slightly to allow the batch exporter to finish HTTP calls
    time.sleep(1)

if __name__ == "__main__":
    main()
