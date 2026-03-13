import os
import sys
import subprocess
from telemetry import get_tracer, get_context_env

tracer = get_tracer(__name__)

class TrainerClient:
    """Mock trainer client representing Kubeflow's SDK."""

    def _validate_job(self, job_name: str):
        with tracer.start_as_current_span("TrainerClient.validate_job") as span:
            span.set_attribute("job.name", job_name)
            span.add_event("Validation successful")

    def _prepare_payload(self, job_name: str) -> dict:
        with tracer.start_as_current_span("TrainerClient.prepare_payload") as span:
            span.set_attribute("payload.type", "json")
            return {"job": job_name, "replicas": 3}

    def create_training_job(self, job_name: str):
        with tracer.start_as_current_span("TrainerClient.create_training_job") as span:
            span.set_attribute("job.name", job_name)
            span.set_attribute("component", "TrainerClient")
            
            trace_id = span.get_span_context().trace_id
            print(f"[{trace_id:032x}] TrainerClient: Submitting job {job_name}")

            self._validate_job(job_name)
            self._prepare_payload(job_name)

            # Pass telemetry context to worker
            env = os.environ.copy()
            telemetry_env = get_context_env()
            env.update(telemetry_env)

            span.add_event("Subprocess Start")
            
            # Execute worker as a subprocess
            worker_path = os.path.join(os.path.dirname(__file__), "worker.py")
            result = subprocess.run(
                [sys.executable, worker_path, job_name], 
                env=env, 
                capture_output=True, 
                text=True
            )
            
            span.set_attribute("subprocess.returncode", result.returncode)
            span.add_event("Subprocess End")
            
            print("--- Worker Output ---")
            print(f"{result.stdout.strip()}")
            if result.stderr:
                print(f"Worker Error:\n{result.stderr}")
            print("---------------------")
