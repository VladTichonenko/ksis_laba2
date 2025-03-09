import socket
import os
import struct
import time
import select

def checksum(data):
    sum = 0
    length = len(data)
    i = 0
    while length > 1:
        sum += (data[i] << 8) + (data[i + 1])
        sum = (sum & 0xFFFF) + (sum >> 16)
        i += 2
        length -= 2

    if length > 0:
        sum += data[i] << 8
        sum = (sum & 0xFFFF) + (sum >> 16)

    return ~sum & 0xFFFF


def create_icmp_packet(id):
    # Заголовок ICMP (type, code, checksum, id, sequence number)
    icmp_header = struct.pack("bbHHh", 8, 0, 0, id, 1)
    data = b'abcdefghijklmnopqrstuvwabcdefghi'
    checksum_val = checksum(icmp_header + data)

    # Перезапишем контрольную сумму в заголовке
    icmp_header = struct.pack("bbHHh", 8, 0, socket.htons(checksum_val), id, 1)
    return icmp_header + data


def receive_ping(sock, id, timeout):
    start_time = time.time()
    while True:
        readable = select.select([sock], [], [], timeout)
        if readable[0] == []:
            return None, None

        time_received = time.time()
        packet, addr = sock.recvfrom(1024)
        icmp_header = packet[20:28]

        type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)

        if packet_id == id:
            return addr, time_received - start_time

        if time_received - start_time > timeout:
            return None, None


def traceroute(destination):
    print(f"Трассировка маршрута до {destination}...")
    ttl = 1
    max_hops = 30
    timeout = 2
    try:
        host_ip = socket.gethostbyname(destination)
    except socket.gaierror:
        print("Не удалось разрешить имя хоста.")
        return

    print(f"Целевой IP: {host_ip}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    # Устанавливаем тайм-аут
    sock.settimeout(timeout)

    # Начинаем трассировку
    while ttl <= max_hops:
        # Устанавливаем TTL для каждого пакета
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

        # Создаем ICMP пакет
        packet_id = os.getpid() & 0xFFFF  # Генерация ID пакета
        packet = create_icmp_packet(packet_id)

        # Отправляем пакет
        sock.sendto(packet, (host_ip, 0))

        # Получаем ответ
        addr, time = receive_ping(sock, packet_id, timeout)

        if addr is None:
            print(f"{ttl}  *  Timeout")
        else:
            print(f"{ttl}  {addr[0]}  {time * 1000:.3f} ms")

        ttl += 1

    sock.close()


if __name__ == "__main__":
    target = input("Введите IP-адрес или доменное имя для трассировки: ")
    traceroute(target)
