import logging
import os

LOG = logging.getLogger(__name__)
LOG.setLevel("CRITICAL")

DEFAULT_HOST = os.environ.get("ANSRV_GEO_HOST", "127.0.0.1")
DEFAULT_PORT = os.environ.get("ANSRV_GEO_PORT", 50051)

LOG.debug("Default service host name set to %s", DEFAULT_HOST)
LOG.debug("Default service port set to %d", DEFAULT_PORT)
