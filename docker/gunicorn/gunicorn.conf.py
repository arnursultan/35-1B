workers     = 3

worker_class = "sync"

bind        = "0.0.0.0:8000"
timeout     = 120

accesslog   = "-"
errorlog    = "-"
loglevel    = "info"

max_requests = 1000
max_requests_jitter = 100