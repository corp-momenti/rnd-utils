## rnd-utils

Common utilities for general usage.

### Installation

```sh
$ poetry install
```

## Logger

Logger is implemented using loguru, adding datadog handler if environment variables exist for connection.

To use logger, do the following

```py
from rnd_utils.logger import logger

logger.info("This is info level log")
```

### Datadog Loggings

To send logs to datadog, using the logger, appropriate environment variables need to be set.

3 Main environment variables are as follows.
- DD_API_KEY: Datadog API Key
- DD_APP_KEY: Datadog APP Key
- DD_SITE: Datadog site. For example datadog.eu

Other environment variables can be set additionally for more context.
Please view `logger.py` module docs for more information.

### Function Logger Wraps

`logger_wraps` is a Python decorator that facilitates logging for function entry and exit, along with execution time measurement. This decorator is particularly useful for adding structured logging to your functions, helping you to monitor and debug their behavior more effectively.

### Features

- Logs function entry with arguments and keyword arguments (optional).
- Logs function exit with the returned result (optional).
- Measures and logs the execution time of the wrapped function.
- Allows customization of the log level for both entry and exit logs.

### usage

```py
@logger_wraps(entry=True, exit=True, level="DEBUG")
def my_function(arg1, arg2, kwarg1=None):
    # Your function code here
    return result

```

## File Utils

Functions related to file operations.

### Usage

```py
from rnd_utils import file_utils
```

### Features

- Save Temporary file and receive temp file name for further operations
- Download file with a URL and save as temporary file
- Hash bytes content to md5
- Encode file to url safe base-64 encoded