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
