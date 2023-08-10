"""
Log utils for handling logs with stdout and Datadog

Operates with environment variables:

- DD_API_KEY: Datadog API Key
- DD_APP_KEY: Datadog APP Key
- DD_SITE: Datadog site. For example datadog.eu
- ENV: Environment the logging is done
- HOST_NAME: Name of the host instance
- SERVICE_NAME: Name of the service

"""
import os
import sys
import json
import logging
from loguru import logger

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.content_encoding import ContentEncoding


class DatadogHandler(logging.Handler):
    def __init__(self, api_key: str, app_key: str, site: str = "datadoghq.com"):
        super().__init__()
        self.api_key = api_key
        self.app_key = app_key
        self.site = site
        self.configuration = None
        self.api_client = ApiClient(self.configuration)
        self.logs = LogsApi(self.api_client)

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

    def emit(self, record):
        toJson = json.dumps(
            {
                "python-logging": {
                    "py-env": os.getenv("ENV"),
                    "py-message": record.getMessage(),
                    "py-status": record.levelname.lower(),
                    "py-logger": record.name,
                    "py-stacktrace": record.exc_info,
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
                        ddtags="env:{}".format(os.getenv("ENV")),
                        hostname=os.getenv("HOST_NAME"),
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
            site=os.getenv("DD_SITE"),
        )
    )
