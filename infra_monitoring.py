def get_metrics():
    return {
        "fill_rate": 99.2,
        "edge": 0.26,
        "latency": 21,
        "cpu": 55,
        "mem": 43
    }

def get_alerts():
    return [{"timestamp": "2025-05-22 16:00", "message": "All systems green"}]

def get_model_feedback():
    return {
        "missed_trades": 3,
        "rejection_rate": 1.2,
        "entropy_tracked": 0.83,
        "avg_confidence": 95.7
    }

def get_cost_data():
    return {
        "month_to_date": 1783.00,
        "history": [1300, 1400, 1500, 1650, 1783]
    }
