import socket

HOST = '192.168.1.21'  # Адрес сервера
PORT = 65432        # Порт сервера

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hi')
    data = s.recv(1024)

print('Ответ от сервера:', data.decode())
