"""
Log utils for handling logs with stdout and Datadog

Operates with environment variables:

- DD_API_KEY: Datadog API Key
- DD_APP_KEY: Datadog APP Key
- DD_SITE: Datadog site. For example datadog.eu
- ENV: Environment the logging is done
- HOST_NAME: Name of the host instance
- SERVICE_NAME: Name of the service

If using a docker container, additional env variables can be provided

- DOCKER_CONTAINER_NAME: Name of docker container
- DOCKER_IMAGE_NAME: Name of docker image used

"""
import os
import sys
import json
import logging
import platform
from loguru import logger
import functools
import time

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.content_encoding import ContentEncoding


def logger_wraps(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            start = time.time()
            if entry:
                logger_.log(
                    level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs
                )
            result = func(*args, **kwargs)
            end = time.time()
            logger_.log(level, "Function '{}' executed in {:f} s", name, end - start)

            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)

            return result

        return wrapped

    return wrapper


class DatadogHandler(logging.Handler):
    def __init__(self, api_key: str, app_key: str, site: str = "datadoghq.com"):
        super().__init__()
        self.api_key = api_key
        self.app_key = app_key
        self.site = site
        self.configuration = None
        self.api_client = ApiClient(self.configuration)
        self.logs = LogsApi(self.api_client)
        self.datadog_tags = None

    @property
    def configuration(self):
        if self._configuration is None:
            configuration = Configuration()
            configuration.api_key["apiKeyAuth"] = self.api_key
            configuration.api_key["appKeyAuth"] = self.app_key
            configuration.server_variables["site"] = self.site

            self._configuration = configuration

        return self._configuration

    @configuration.setter
    def configuration(self, configuration: Configuration):
        self._configuration = configuration

    @property
    def datadog_tags(self):
        if self._datadog_tags is None:
            ddtags = [f"env:{os.getenv('ENV')}"]

            if os.getenv("DOCKER_CONTAINER_NAME"):
                ddtags.append(f"container_name:{os.getenv('DOCKER_CONTAINER_NAME')}")

            if os.getenv("DOCKER_IMAGE_NAME"):
                ddtags.append(f"image_name:{os.getenv('DOCKER_IMAGE_NAME')}")

            self._datadog_tags = ddtags

        return self._datadog_tags

    @datadog_tags.setter
    def datadog_tags(self, ddtags: list[str]):
        self._datadog_tags = ddtags

    def emit(self, record):
        toJson = json.dumps(
            {
                "python-logging": {
                    "py-env": os.getenv("ENV"),
                    "py-message": record.getMessage(),
                    "py-status": record.levelname.lower(),
                    "py-logger": record.name,
                    "py-stacktrace": str(record.exc_info),
                    "py-exception": record.exc_text,
                    "py-line": record.lineno,
                    "py-file": record.filename,
                    "py-function": record.funcName,
                    "py-level": record.levelno,
                    "py-path": record.pathname,
                    "py-thread": record.thread,
                    "py-threadName": record.threadName,
                    "py-process": record.process,
                    "py-processName": record.processName,
                    "py-args": record.args,
                    "py-msecs": record.msecs,
                    "py-relativeCreated": record.relativeCreated,
                    "py-created": record.created,
                    "py-module": record.module,
                }
            }
        )

        # Send the log to Datadog using the Logs API
        try:
            body = HTTPLog(
                [
                    HTTPLogItem(
                        ddsource="Python",
                        ddtags=",".join(self.datadog_tags),
                        hostname=os.getenv("HOST_NAME", platform.uname()[1]),
                        message=toJson,
                        service=os.getenv("SERVICE_NAME"),
                        status=record.levelname.lower(),
                    ),
                ]
            )

            self.logs.submit_log(content_encoding=ContentEncoding.DEFLATE, body=body)

        except Exception as exc:
            print(f"Error sending log to Datadog: {exc}")


logger.remove()
logger.add(sys.stdout)

if os.getenv("DD_API_KEY") and os.getenv("DD_APP_KEY"):
    logger.add(
        DatadogHandler(
            api_key=os.getenv("DD_API_KEY"),
            app_key=os.getenv("DD_APP_KEY"),
            site=os.getenv("DD_SITE", "us5.datadoghq.com"),
        )
    )
