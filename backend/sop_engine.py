def evaluate_alert(alert):
    text = f"{alert.subject} {alert.message}".lower()

    if "cpu" in text:
        return {"action": "cpu_kill_top", "payload": {}}

    if "disk" in text or "filesystem" in text:
        return {"action": "cleanup_temp", "payload": {}}

    if "memory" in text or "ram" in text:
        return {"action": "restart_service", "payload": {"service": "Spooler"}}

    if "service" in text and "stopped" in text:
        return {"action": "restart_service", "payload": {"service": "Spooler"}}

    if "agent" in text and "unreachable" in text:
        return None

    return None