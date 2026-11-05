import platform
import socket
import time

import psutil


def get_local_ip():
    """Zwraca adres IP komputera w sieci (lub 127.0.0.1, gdy nie da się go ustalić)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # nic nie jest wysyłane, służy tylko do ustalenia IP
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def get_temperature():
    """Zwraca najwyższą temperaturę w °C albo None, w przypadku gdy system jej nie udostępnia."""
    """Niestety Windows i macOS zwykle nie mają tej funkcji."""
    if not hasattr(psutil, "sensors_temperatures"):
        return None
    try:
        sensors = psutil.sensors_temperatures()
    except Exception:
        return None
    values = [entry.current for entries in sensors.values() for entry in entries]
    if not values:
        return None
    return round(max(values), 1)


def get_disks():
    """Zwraca listę dysków z całkowitym i zajętym miejscem (dane w GB)."""
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except OSError:
            continue  # np. pusta stacja CD/DVD
        disks.append({
            "name": part.mountpoint,
            "total_gb": round(usage.total / 1024**3, 1),
            "used_gb": round(usage.used / 1024**3, 1),
            "percent": usage.percent,
        })
    return disks


def get_processes(limit=50):
    """Zwraca pewien limit procesów zajmujących najwięcej pamięci."""
    """Cała lista tych procesów jest wyświetlana w kolejności malejącej."""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "memory_info"]):
        info = proc.info
        mem = info["memory_info"]
        processes.append({
            "pid": info["pid"],
            "name": info["name"] or "?",
            "memory_mb": round(mem.rss / 1024**2, 1) if mem else 0,
        })
    processes.sort(key=lambda p: p["memory_mb"], reverse=True)
    return processes[:limit]


def collect_stats():
    """Zbiera wszystkie dane o komputerze w jeden słownik."""
    ram = psutil.virtual_memory()
    return {
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "ip": get_local_ip(),
        "uptime_s": int(time.time() - psutil.boot_time()),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_cores": psutil.cpu_count(),
        "ram_total_gb": round(ram.total / 1024**3, 1),
        "ram_used_gb": round(ram.used / 1024**3, 1),
        "ram_percent": ram.percent,
        "temperature": get_temperature(),
        "disks": get_disks(),
        "processes": get_processes(),
    }