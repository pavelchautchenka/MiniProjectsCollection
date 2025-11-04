import socket, ssl
from deffi_helman import *
import threading

g = 5
p = 23
clients = []


def handle_new_client(conn, addr):
    try:

        client_id = str(conn.recv(1024).decode())

        print('new connection from', client_id, addr)
        private_key, public_key = generate_keys(g, p)
        conn.send(str(public_key).encode())

        client_public = int(conn.recv(1024).decode())
        shared_key = compute_shared_secret(client_public, private_key, p)
        clients.append({'conn': conn, 'key': shared_key})

        threading.Thread(target=handle_receive, args=(conn, shared_key, client_id), daemon=True).start()
        handle_send(conn, shared_key)
    except Exception as e:
        print(f"Error with {addr}: {e} ")
    finally:
        conn.close()


def handle_receive(conn, shared_key, client_id):
    while True:
        try:
            data = conn.recv(1024).decode()

            if not data:
                break
            print(f"\n", client_id, ':', aes_decrypt(data, shared_key), "\n", 'Me: ', end="")
        except Exception:
            break


def handle_send(conn, shared_key):
    while True:
        msg = input('Me:')
        for client in clients:
            try:
                client['conn'].send(aes_encrypt(msg,client['key']).encode())

            except Exception:
               break


context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 12345))
    s.listen(5)
    print("whaiting client")

    while True:
        try:
            conn, addr = s.accept()
            tls_conn = context.wrap_socket(conn, server_side=True)
            threading.Thread(target=handle_new_client, args=(tls_conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("You close your server")
