import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = structlog.get_logger(__name__)

def setup_tracing():
    """Setup OpenTelemetry Tracing."""
    try:
        provider = TracerProvider()
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        logger.info("tracing_initialized")
    except Exception as e:
        logger.error("tracing_initialization_failed", error=str(e))

class LangGraphTracer:
    """Mock callback handler for LangGraph / LangChain to create spans."""
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.tracer = trace.get_tracer(__name__)
        self._current_span = None
        
    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        self._current_span = self.tracer.start_span("llm_call")
        self._current_span.set_attribute("task_id", self.task_id)

    def on_llm_end(self, response, **kwargs):
        if self._current_span:
            self._current_span.end()
            self._current_span = None

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        self._current_span = self.tracer.start_span("tool_call")
        self._current_span.set_attribute("task_id", self.task_id)
        if "name" in serialized:
            self._current_span.set_attribute("tool.name", serialized["name"])

    def on_tool_end(self, output: str, **kwargs):
        if self._current_span:
            self._current_span.end()
            self._current_span = None
