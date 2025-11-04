import socket
import ssl

from deffi_helman import *
import threading

class SecureChatSender:
    def __init__(self,host='192.168.1.24', port=12345, certfile='cert.pem', keyfile='key.pem', g=5, p=23, id="Igor"):
        self.host = host
        self.port = port
        self.g = g
        self.p = p
        self.id = "igor"
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        self.context.check_hostname = False

    def create_coonection_to_server(self):
        with socket.create_connection((self.host, self.port)) as sender_socket:
            print("Connecting with server ")
            tls_context = self.context.wrap_socket(sender_socket, server_hostname=self.host)
            print('Connecting with TLS')
            tls_context.send(str(self.id).encode())
            print('id sent')
            server_public = int(tls_context.recv(1024).decode())
            private_key, public_key = generate_keys(self.g, self.p)

            tls_context.send(str(public_key).encode())
            shared_key = compute_shared_secret(server_public, private_key, p)
            try:


