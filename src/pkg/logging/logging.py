from logging import getLogger, StreamHandler, FileHandler
import sys
from fastapi import FastAPI, Request, Response
import structlog
from structlog.types import EventDict, Processor
from uvicorn.protocols.utils import get_path_with_query_string
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from ddtrace.contrib.asgi.middleware import TraceMiddleware
from time import perf_counter_ns
from inspect import getframeinfo, stack


__FILE_PATH = './logs/all.log'
__is_setup = False


class FileNameRenderer(object):
    def __init__(self, stack_depth):
        self._stack_depth = stack_depth

    def __call__(self, logger, name, event_dict):
        caller = getframeinfo(stack()[self._stack_depth][0])
        event_dict["file_name"] = f"{caller.filename}:{caller.lineno}"
        return event_dict


def __rename_event_key(_, __, event_dict: EventDict) -> EventDict:
    event_dict["message"] = event_dict.pop("event")
    return event_dict

def __drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    event_dict.pop("color_message", None)
    return event_dict

def setup_logging(log_level: str = "INFO"):
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=False)
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        FileNameRenderer(stack_depth=5),
        structlog.stdlib.ExtraAdder(),
        __drop_color_message_key,
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]
    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )    
    file_log_renderer = structlog.processors.KeyValueRenderer()
    file_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors
        + [
            __rename_event_key,
            structlog.processors.format_exc_info
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            file_log_renderer,
        ],
    )
    console_log_renderer = structlog.dev.ConsoleRenderer()
    console_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            console_log_renderer,
        ],
    )
    root_logger = getLogger()
    console_handler = StreamHandler()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    file_handler = FileHandler(__FILE_PATH)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(log_level.upper())
    for _log in ["uvicorn", "uvicorn.error"]:
        getLogger(_log).handlers.clear()
        getLogger(_log).propagate = True
    for _log in ["uvicorn.access", "asyncio", "ddtrace.internal.telemetry.writer"]:
        getLogger(_log).handlers.clear()
        getLogger(_log).propagate = False    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        root_logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )
    sys.excepthook = handle_exception

def get_logger(name: str = 'main.logger', log_level: str = "INFO") -> structlog.stdlib.BoundLogger:
    if not __is_setup:
        setup_logging(log_level)
    logger = structlog.stdlib.get_logger(name)
    return logger

def handle_app_logs_to_custom_logger(app: FastAPI, custom_logger: structlog.stdlib.BoundLogger):
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next) -> Response:
        structlog.contextvars.clear_contextvars()
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        start_time = perf_counter_ns()
        response = Response(status_code=500)
        try:
            response = await call_next(request)
        except Exception:
            structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
            raise
        finally:
            process_time = perf_counter_ns() - start_time
            status_code = response.status_code
            url = get_path_with_query_string(request.scope)
            client_host = request.client.host
            client_port = request.client.port
            http_method = request.method
            http_version = request.scope["http_version"]
            if str(request.url) not in ['http://127.0.0.1:8000/graph/_dash-update-component', 'http://127.0.0.1:8000/reader/_dash-update-component']:
                if status_code >= 400:
                    custom_logger.error(
                        f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
                        http={
                            "url": str(request.url),
                            "status_code": status_code,
                            "method": http_method,
                            "request_id": request_id,
                            "version": http_version,
                        },
                        network={"client": {"ip": client_host, "port": client_port}},
                        duration=process_time,
                    )
                else:
                    custom_logger.debug(
                        f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
                        http={
                            "url": str(request.url),
                            "status_code": status_code,
                            "method": http_method,
                            "request_id": request_id,
                            "version": http_version,
                        },
                        network={"client": {"ip": client_host, "port": client_port}},
                        duration=process_time,
                    )
            response.headers["X-Process-Time"] = str(process_time / 10 ** 9)
            return response
    app.add_middleware(CorrelationIdMiddleware)
    tracing_middleware = next(
        (m for m in app.user_middleware if m.cls == TraceMiddleware), None
    )
    if tracing_middleware is not None:
        app.user_middleware = [m for m in app.user_middleware if m.cls != TraceMiddleware]
        structlog.stdlib.get_logger("api.datadog_patch").info(
            "Patching Datadog tracing middleware to be the outermost middleware..."
        )
        app.user_middleware.insert(0, tracing_middleware)
        app.middleware_stack = app.build_middleware_stack()