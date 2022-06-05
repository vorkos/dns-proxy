#!/usr/bin/env python3

import logging
import socket
import ssl
import os
from threading import Thread

BUF_SIZE = 1024
TLS_DNS_IP = os.getenv("TLS_DNS_IP", "1.1.1.1")
TLS_DNS_PORT = int(os.getenv("TLS_DNS_PORT", 853))
TLS_DNS = (TLS_DNS_IP, TLS_DNS_PORT)
PROXY_PORT = int(os.getenv("PROXY_PORT", 53))
PROXY = ('0.0.0.0', PROXY_PORT)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def send_tls_request(data, proto="tcp") -> bytes:
    """Send data to tls resolver
    """
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    context.check_hostname = True
    with socket.create_connection(TLS_DNS, timeout=2) as sock:
        with context.wrap_socket(sock, server_hostname=TLS_DNS_IP) as tls_sock:
            ssl_cert = str(tls_sock.getpeercert())
            logger.info(
                f"Certificate obtained from the DNS server: {ssl_cert}")
            if proto != "tcp":
                data = get_tcp_query(data)
            sent = tls_sock.send(data)
            if sent == 0:
                logger.error(f"Connection to {TLS_DNS_IP} broken")
            result = tls_sock.recv(BUF_SIZE)
            return result


def get_tcp_query(query):
    """Form TCP query from UDP one"""
    return b"\x00" + bytes(chr(len(query)), encoding='utf-8') + query


def get_udp_query(query):
    """Remove the TCP header."""
    return query[2:]


def udp_handler(data, addr, udp_sock):
    """Re-route request to the TLS resolver and return
    response back to the UDP client
    """
    response = send_tls_request(data, "udp")
    if not response:
        logger.error("Invalid DNS query.")
        return
    udp_answer = get_udp_query(response)
    udp_sock.sendto(udp_answer, addr)


def tcp_handler(data, tcp_conn):
    """Re-route request to the TLS resolver and return
    response back to the TCP client
    """
    response = send_tls_request(data)
    if not response:
        logger.error("Invalid DNS query.")
        tcp_conn.close()
        return
    tcp_conn.send(response)
    tcp_conn.close()


def tcp_listener():
    """Listen for new TCP connections and start handler on the new request
    """
    try:
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.bind(PROXY)
        logging.info(f"Listening for TCP requests on {PROXY_PORT} port")
        tcp_sock.listen()

        while True:
            tcp_conn = tcp_sock.accept()[0]
            tcp_data = tcp_conn.recv(1024)
            Thread(target=tcp_handler, args=(
                (tcp_data, tcp_conn))).start()
    except Exception as e:
        logger.error(str(e))
        tcp_sock.close()


def udp_listener():
    """Listen for new UDP connections DNS requests"""
    try:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(PROXY)
        logging.info(f"Listening for UDP requests on {PROXY_PORT} port")

        while True:
            data, addr = udp_sock.recvfrom(512)
            Thread(target=udp_handler, args=(data, addr, udp_sock)).start()
    except Exception as e:
        logging.error(str(e))
        udp_sock.close()


if __name__ == '__main__':
    Thread(target=tcp_listener).start()
    Thread(target=udp_listener).start()
