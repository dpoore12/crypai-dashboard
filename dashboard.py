import os
import time
import gc
import random
import signal
import threading
import psutil
import boto3
import atexit
import streamlit as st
from infra_monitoring import get_metrics, get_alerts, get_model_feedback, get_cost_data

st.set_page_config(page_title="CRYP-AI Monitoring Dashboard", layout="wide")
st.title("📊 CRYP-AI v3.6 Monitoring Dashboard")

MIN_REFRESH = 30
COST_BUDGET = float(os.getenv("COST_BUDGET", 2700))
REFRESH_INTERVAL = max(MIN_REFRESH, int(os.getenv("REFRESH_INTERVAL", 300)))
JITTER = random.uniform(0.9, 1.1)
MAX_MEMORY = 512  # in MB
INSTANCE_ID = os.getenv("INSTANCE_ID")

if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0
st.session_state.refresh_count += 1

def watchdog():
    while True:
        if time.time() - st.session_state.get('last_success', 0) > 600:
            os.kill(os.getpid(), signal.SIGKILL)
        time.sleep(60)

threading.Thread(target=watchdog, daemon=True).start()

if psutil.Process().memory_info().rss > MAX_MEMORY * 1024**2:
    st.error("CRITICAL: Memory usage exceeded limit — initiating shutdown")
    os.kill(os.getpid(), signal.SIGTERM)
    st.stop()

LATENCY_BUDGET_HARD = 30  # ms
LATENCY_BUDGET_WARN = 25  # ms

if metrics['latency'] > LATENCY_BUDGET_HARD:
    st.error(f"CRITICAL: Signal→Order latency {metrics['latency']}ms exceeds hard limit of {LATENCY_BUDGET_HARD}ms")
    os.kill(os.getpid(), signal.SIGTERM)
    st.stop()
elif metrics['latency'] > LATENCY_BUDGET_WARN:
    st.warning(f"WARNING: Signal→Order latency {metrics['latency']}ms approaching limit ({LATENCY_BUDGET_HARD}ms)")

def cleanup():
    if st.session_state.get('metrics'):
        print("Uploading final metrics before shutdown...")
atexit.register(cleanup)

try:
    metrics = get_metrics()
    alerts = get_alerts()
    feedback = get_model_feedback()
    cost_data = get_cost_data()
    st.session_state.last_success = time.time()
    st.session_state.metrics = metrics
except Exception as e:
    st.error(f"Error fetching monitoring data: {e}")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Avg Fill Rate", f"{metrics['fill_rate']}%")
    st.metric("Edge %", f"{metrics['edge']}%")
with col2:
    st.metric("Signal→Order Latency", f"{metrics['latency']} ms")
    st.metric("CPU", f"{metrics['cpu']}%")
    st.metric("Mem", f"{metrics['mem']}%")
with col3:
    st.metric("Cost Burn", f"${cost_data['month_to_date']}/${COST_BUDGET}")
    st.metric("Model Conf.", f"{feedback['avg_confidence']}%")

st.subheader("⚠️ Alerts")
for alert in alerts:
    st.error(f"{alert['timestamp']} — {alert['message']}")

st.subheader("🧠 Model Feedback")
st.metric("Missed Trades", feedback['missed_trades'])
st.metric("Rejection Rate", feedback['rejection_rate'])
st.metric("Entropy Tracked", str(feedback['entropy_tracked']))

st.subheader("📉 Cost Tracking")
st.line_chart(cost_data['history'])

gc.collect()

if time.time() - st.session_state.get('last_success', 0) > 900:
    st.error("CRITICAL: Unresponsive for 15 mins — terminating instance")
    if INSTANCE_ID and st.session_state.get('confirmed_termination', True):
        boto3.client('ec2').terminate_instances(InstanceIds=[INSTANCE_ID])
    os.kill(os.getpid(), signal.SIGTERM)
    st.stop()

try:
    time.sleep(REFRESH_INTERVAL * JITTER)
except Exception as e:
    st.warning(f"Refresh delayed: {str(e)}")
finally:
    if st._is_running_with_streamlit:
        st.rerun()
