def get_metrics():
    return {
        "fill_rate": 98.9,
        "edge": 0.24,
        "latency": 22,
        "cpu": 53,
        "mem": 48
    }

def get_alerts():
    return [
        {"timestamp": "2025-05-22 17:00", "message": "Signal latency above 20ms"},
        {"timestamp": "2025-05-22 16:45", "message": "CPU usage at 53%"}
    ]

def get_model_feedback():
    return {
        "missed_trades": 2,
        "rejection_rate": 1.4,
        "entropy_tracked": 0.72,
        "avg_confidence": 94.6
    }

def get_cost_data():
    return {
        "month_to_date": 1832.17,
        "history": [1220, 1334, 1451, 1620, 1832]
    }
