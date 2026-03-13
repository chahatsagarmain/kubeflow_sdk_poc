# OpenTelemetry PoC for Kubeflow SDK

This Proof of Concept (PoC) demonstrates how to integrate distributed tracing into the Kubeflow SDK using OpenTelemetry, including context propagation across a subprocess.

## Structure
- `telemetry.py`: Centralized telemetry configuration containing tracer setup, OTLP exporters, and context injection/extraction utilities (mocking what would be in `kubeflow/common/telemetry/`).
- `trainer_client.py`: Mock of the SDK `TrainerClient` that initiates a span and calls a subprocess.
- `worker.py`: A script representing an external execution or subprocess that receives the trace context via environment variables.
- `main.py`: Entrypoint tying it together.

## Running

1. **Start Jaeger**
   ```bash
   cd poc
   docker-compose up -d
   ```

2. **Install Dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```
   *(or use regular `pip`)*

3. **Run the Demo**
   ```bash
   python main.py
   ```

4. **Observe the Trace**
   Navigate to [http://localhost:16686](http://localhost:16686) in your browser. Search for the `kubeflow-sdk` service to see the distributed trace covering `main.py` -> `trainer_client.py` -> `worker.py`.
