# state.py

import threading

JOBS = {}
JOBS_LOCK = threading.Lock()

STATUS_RUNNING = "running"
STATUS_DONE = "done"
STATUS_ERROR = "error"