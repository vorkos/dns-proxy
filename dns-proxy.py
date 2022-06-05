#!/usr/bin/env python3

import logging
import socket
import ssl
import os
from threading import Thread

BUF_SIZE = 1024
TLS_DNS = os.getenv("TLS_DNS", "1.1.1.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", 53))
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def send_tls_request(data, hostname: str, port: int = 853) -> bytes:
    """ Send data to tls host
    """
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    context.check_hostname = True
    with socket.create_connection((hostname, port), timeout=2) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
            logger.info(
                f"Certificate obtained from the DNS server: {str(tls_sock.getpeercert())}")
            sent = tls_sock.send(data)
            if sent == 0:
                logger.error(f"Connection to {hostname} broken")
            result = tls_sock.recv(BUF_SIZE)
            return result


# def get_tcp_query(query):
#     """Form TCP query from UDP one
#     """
#     return b"\x00" + bytes(chr(len(query)), encoding='utf-8') + query

# def get_udp_query(query):
#     """Remove the TCP header.
#     """
#     return query[2:]


def tcp_handler(data, connection):
    """
    """
    answer = send_tls_request(data, TLS_DNS)
    if not answer:
        logger.error("Invalid DNS query.")
        connection.close()
        return
    connection.send(answer)
    connection.close()


def tcp_listner():
    """ Lisen for new TCP connections and start handler on the new request
    """
    try:
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.bind(('0.0.0.0', PROXY_PORT))
        tcp_sock.listen()
        while True:
            tcp_conn = tcp_sock.accept()[0]
            tcp_data = tcp_conn.recv(1024)
            tcp_proc = Thread(target=tcp_handler, args=(
                (tcp_data, tcp_conn)))
            tcp_proc.daemon = True
            tcp_proc.start()
    except KeyboardInterrupt:
        logger.info("User interuption")
        tcp_sock.close()
    except Exception as e:
        logger.error(str(e))
        tcp_sock.close()


if __name__ == '__main__':
    Thread(target=tcp_listner).start()
