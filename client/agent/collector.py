import psutil
import time
from scapy.all import sniff, IP, TCP, UDP, ICMP
from collections import deque
import socket

packet_buffer = deque(maxlen=10000)
last_cleanup_time = time.time()

def packet_handler(pkt):
    global packet_buffer, last_cleanup_time
    
    current_time = time.time()
    
    while packet_buffer and current_time - packet_buffer[0].time > 15:
        packet_buffer.popleft()
    
    if IP in pkt:
        packet_buffer.append(pkt)

def start_background_sniffer():
    bpf_filter = "tcp or udp or icmp"
    
    sniff(
        prn=packet_handler,
        store=False,
        filter=bpf_filter
    )

def analyze_ip_traffic():
    ip_stats = {}
    
    for pkt in packet_buffer:
        if IP in pkt:
            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            pkt_size = len(pkt)
            
            if src_ip not in ip_stats:
                ip_stats[src_ip] = {"sent": 0, "received": 0}
            ip_stats[src_ip]["sent"] += pkt_size
            
            if dst_ip not in ip_stats:
                ip_stats[dst_ip] = {"sent": 0, "received": 0}
            ip_stats[dst_ip]["received"] += pkt_size
    
    return ip_stats

def collect_network_metrics(config):
    global last_cleanup_time
    
    current_time = time.time()
    
    if current_time - last_cleanup_time > 5:
        while packet_buffer and current_time - packet_buffer[0].time > 15:
            packet_buffer.popleft()
        last_cleanup_time = current_time

    io_counters = psutil.net_io_counters()
    connections = psutil.net_connections()

    metrics = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "device_id": config.get("device_id", "unknown_device"),
        "incoming_traffic": io_counters.bytes_recv,
        "outgoing_traffic": io_counters.bytes_sent,
        "active_tcp_connections": sum(1 for conn in connections if conn.status == "ESTABLISHED" and conn.type == socket.SOCK_STREAM),
        "active_udp_connections": sum(1 for conn in connections if conn.type == socket.SOCK_DGRAM),
    }
    
    metrics["ip_traffic"] = analyze_ip_traffic()
    
    return metrics


print()