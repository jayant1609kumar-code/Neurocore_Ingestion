def evaluate_alert(alert):
    subject = (alert.subject or "").lower()
    message = (alert.message or "").lower()
    text = f"{subject} {message}"

    # ICMP / Unreachable Logic
    if "unreachable" in text or "icmp" in text or "nodata" in text:
        return {"action": "verify_connectivity", "payload": {"method": "ping", "count": 4}}

    # Service Logic
    if "service" in text and ("stopped" in text or "not running" in text):
        return {"action": "restart_service", "payload": {"service": "Spooler"}}

    # Resource Logic
    if "cpu" in text or "load" in text:
        return {"action": "kill_high_cpu_proc", "payload": {"threshold": 90}}

    if "disk" in text or "space" in text:
        return {"action": "cleanup_logs", "payload": {"days": 7}}

    return None