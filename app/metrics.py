from prometheus_client import Counter, Histogram, Gauge

num_requests = Counter("http_requests_total", "Total number of HTTP requests", ["method", "endpoint", "status_code"])
num_errors = Counter("http_request_errors_total", "Total number of HTTP request errors", ["method", "endpoint", "status_code"])
num_created_recipes = Counter("created_recipes_total", "Total number of created recipes",  ["source"])
request_latency = Histogram("http_request_latency_seconds", "HTTP request latency in seconds",  ["method", "endpoint"])
requests_in_progress = Gauge("http_requests_in_progress", "Number of HTTP requests in progress")
num_nutrition_analyses = Counter("nutrition_analyses_total","Total number of nutrition analyses",["source", "status"])