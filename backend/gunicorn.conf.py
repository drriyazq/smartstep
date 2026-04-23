"""Gunicorn production config for SmartStep backend.

Launched by the systemd unit at /etc/systemd/system/smartstep-backend.service
(see docs/publishing/smartstep-backend.service for the canonical file).
"""
import multiprocessing

# Bind to localhost only — Nginx proxies /smartstep-admin/ to this.
bind = "127.0.0.1:8007"

# Worker count: 2 × CPU + 1 is the documented default.
# On a small VPS 2–3 workers is usually plenty.
workers = min(3, multiprocessing.cpu_count() * 2 + 1)
worker_class = "sync"
threads = 2

# Requests per worker before recycling — helps with slow memory leaks
max_requests = 1000
max_requests_jitter = 100

# Timeouts
timeout = 30
graceful_timeout = 30
keepalive = 5

# Logging — systemd journals capture stdout/stderr
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)ss'

# Security hardening
limit_request_line = 4096
limit_request_fields = 100
