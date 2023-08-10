## rnd-utils

Common utilities for general usage.

### Installation

```sh
$ poetry install
```

### Logger

Logger is implemented using loguru, adding datadog handler if environment variables exist for connection.

To use logger, do the following

```py
from rnd_utils.logger import logger

logger.info("This is info level log")
```

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
