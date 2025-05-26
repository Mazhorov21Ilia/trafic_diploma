import psutil
import time
from scapy.all import sniff, IP, TCP, UDP, ICMP
import socket
from config_m import load_config

def collect_network_metrics(config):
    io_counters = psutil.net_io_counters()
    connections = psutil.net_connections()

    incoming_traffic = io_counters.bytes_recv
    outgoing_traffic = io_counters.bytes_sent
    active_tcp = sum(1 for conn in connections if conn.status == "ESTABLISHED" and conn.type == socket.SOCK_STREAM)
    active_udp = sum(1 for conn in connections if conn.status == "ESTABLISHED" and conn.type == socket.SOCK_DGRAM)

    packet_info = sniff(timeout=config.get("packet_analysis_duration_seconds", 5), prn=lambda x: x.summary())

    protocols_used = set()
    external_ips = set()

    for pkt in packet_info:
        if IP in pkt:
            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            external_ips.add(src_ip)
            external_ips.add(dst_ip)

            if TCP in pkt:
                protocols_used.add("TCP")
            elif UDP in pkt:
                protocols_used.add("UDP")
            elif ICMP in pkt:
                protocols_used.add("ICMP")

    external_ips = list(external_ips)[:config.get("max_external_ips_to_store", 20)]
    protocols_used = list(protocols_used)

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "incoming_traffic": incoming_traffic,
        "outgoing_traffic": outgoing_traffic,
        "active_tcp_connections": active_tcp,
        "active_udp_connections": active_udp,
        "external_ips": external_ips,
        "protocols_used": protocols_used
    }