import socket

HOST = '192.168.1.21'  # Локальный хост
PORT = 65432        # Порт (должен быть одинаковым у клиента и сервера)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Сервер слушает...")
    conn, addr = s.accept()
    with conn:
        print(f"Подключено: {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print("Получено сообщение:", data.decode())
            conn.sendall(b"acepted")  # Ответ клиенту
