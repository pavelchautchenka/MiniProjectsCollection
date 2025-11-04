import socket, ssl
from deffi_helman import *
import threading


class SecureChatServer:
    def __init__(self, host='0.0.0.0', port=12345, certfile='cert.pem', keyfile='key.pem', g=5, p=23):
        self.host = host
        self.port = port
        self.g = g
        self.p = p
        self.clients = []
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"server started on {self.host} : {self.port}")

            try:
                while True:
                    conn, addr = server_socket.accept()
                    tls_connect = self.context.wrap_socket(conn, server_side=True)
                    threading.Thread(target=self.handle_new_client, args=(tls_connect, addr), daemon=True).start()
            except KeyboardInterrupt:
                print("Server stoped manually")

    def handle_new_client(self, conn, addr):
        try:
            client_id = conn.recv(1024).decode()
            print(f"New connection from {client_id} at {addr}")

            private_key, public_key = generate_keys(self.g, self.p)
            conn.send(str(public_key).encode())

            client_public = int(conn.recv(1024).decode())
            shared_key = compute_shared_secret(client_public, private_key, self.p)

            self.clients.append({'conn': conn, 'key': shared_key, 'id': client_id})

            threading.Thread(target=self.recieve_message, args=(conn, shared_key, client_id), daemon=True).start()
            self.send_messages(conn, shared_key)

        except Exception as e:
            print(f"Error with {addr}: {e}")

        finally:
            conn.close()

    def recieve_message(self, conn, shared_key, client_id):
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                decrypted = aes_decrypt(data, shared_key)
                print(f"\n{client_id}:{decrypted} \nMe: ", end ="")
            except Exception:
                break

    def send_messages(self, conn, shared_key):
        """Отправляем сообщения всем клиентам"""
        while True:
            msg = input('Me: ')
            for client in self.clients:
                try:
                    client['conn'].send(aes_encrypt(msg, client['key']).encode())
                except Exception:
                    continue

if __name__ == "__main__":
    server = SecureChatServer()
    server.start()