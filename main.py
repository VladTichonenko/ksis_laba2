# import socket
# from scapy.layers.inet import IP, ICMP
# from scapy.sendrecv import sr1
#
#
#
# def traceroute(destination):
#     """Функция трассировки маршрута с использованием scapy."""
#     print(f"Трассировка маршрута до {destination}...")
#     ttl = 1
#     max_hops = 30  # Максимальное количество хопов
#     timeout = 2  # Таймаут для каждого пакета
#
#     # Преобразуем доменное имя в IP-адрес
#     try:
#         host_ip = socket.gethostbyname(destination)
#     except socket.gaierror:
#         print("Не удалось разрешить имя хоста.")
#         return
#
#     print(f"Целевой IP: {host_ip}")










import socket
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import sr1
import time


def traceroute(destination):
    """Функция трассировки маршрута с использованием scapy."""
    print(f"Трассировка маршрута до {destination}...")
    ttl = 1
    max_hops = 30
    timeout = 2
    retries = 3

    try:
        host_ip = socket.gethostbyname(destination)
    except socket.gaierror:
        print("Не удалось разрешить имя хоста.")
        return

    print(f"Целевой IP: {host_ip}")

    while ttl <= max_hops:
        # Добавляем повторные попытки на случай таймаута
        reply = None
        for _ in range(retries):
            packet = IP(dst=host_ip, ttl=ttl) / ICMP()
            reply = sr1(packet, timeout=timeout, verbose=False)

            if reply is not None:
                break

        if reply is None:
            print(f"{ttl}  *  Timeout")
        else:
            try:
                host_name = socket.gethostbyaddr(reply.src)[0]
            except socket.herror:
                host_name = reply.src

            print(f"{ttl}  {host_name} ({reply.src})  {reply.time * 1000:.3f} ms")

        ttl += 1


if __name__ == "__main__":
    target = input("Введите IP-адрес или доменное имя для трассировки: ")
    traceroute(target)
