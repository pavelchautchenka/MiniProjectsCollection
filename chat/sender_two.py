import socket
import ssl

from deffi_helman import *
import threading

g = 5
p = 23
id = 'Pashka'
host = '192.168.1.24'  # замените на IP сервера
port = 12345


def handle_recieve(sock, shared_key):
    while True:

        data = sock.recv(1024).decode()
        if not data:
            break
        print('Server:', aes_decrypt(data, shared_key), "\n Me:")


def handle_send(sock, shared_key, id):
    while True:
        msg = input("Me:  ")
        encrypted = aes_encrypt(msg, shared_key)
        sock.send(encrypted.encode())


with socket.create_connection((host, port)) as s:


    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='cert.pem')
    context.check_hostname = False

    tls_context = context.wrap_socket(s, server_hostname=host)
    print('Connecting with TLS')
    tls_context.send(str(id).encode())

    server_public = int(tls_context.recv(1024).decode())
    private_key, public_key = generate_keys(g, p)

    tls_context.send(str(public_key).encode())
    shared_key = compute_shared_secret(server_public, private_key, p)
    threading.Thread(target=handle_recieve, args=(tls_context, shared_key), daemon=True).start()
    handle_send(tls_context, shared_key,id)
