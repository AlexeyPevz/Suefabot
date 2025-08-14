from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Response
import time
from functools import wraps

# Метрики
match_created_total = Counter('suefabot_matches_created_total', 'Total number of matches created')
match_completed_total = Counter('suefabot_matches_completed_total', 'Total number of matches completed')
match_timeout_total = Counter('suefabot_matches_timeout_total', 'Total number of matches timed out')
active_matches = Gauge('suefabot_active_matches', 'Number of currently active matches')
user_registrations_total = Counter('suefabot_user_registrations_total', 'Total number of user registrations')
transactions_total = Counter('suefabot_transactions_total', 'Total number of transactions', ['type'])
commission_total = Counter('suefabot_commission_total', 'Total commission collected')
api_request_duration = Histogram('suefabot_api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
websocket_connections = Gauge('suefabot_websocket_connections', 'Number of active WebSocket connections')
lootbox_opened_total = Counter('suefabot_lootbox_opened_total', 'Total number of lootboxes opened', ['type'])


def track_request_duration(f):
    """Декоратор для отслеживания длительности запросов"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            from flask import request
            api_request_duration.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown'
            ).observe(duration)
    
    return decorated_function


def metrics_endpoint():
    """Endpoint для Prometheus"""
    return Response(generate_latest(), mimetype='text/plain')


def init_monitoring(app):
    """Инициализация мониторинга"""
    # Добавляем endpoint для метрик
    app.route('/metrics')(metrics_endpoint)
    
    # Добавляем декоратор ко всем endpoints
    for endpoint in app.url_map.iter_rules():
        if endpoint.rule != '/metrics':
            view_func = app.view_functions.get(endpoint.endpoint)
            if view_func:
                app.view_functions[endpoint.endpoint] = track_request_duration(view_func)