#!/usr/bin/env python3
"""
secure_chat.py

Запуск:
  СЕРВЕР: python secure_chat.py --mode server --host 0.0.0.0 --port 12345
  КЛИЕНТ: python secure_chat.py --mode client --host 192.168.1.24 --port 12345

Зависимости:
  pip install cryptography

Этот скрипт:
 - Использует X25519 (ephemeral ECDH) для обмена секретом
 - Производит HKDF(SHA256) -> 32 байта AES key
 - Шифрует сообщения AES-GCM (12-байт nonce)
 - Добавляет 4-байтовый big-endian заголовок длины для надежной передачи
 - Обрабатывает отключения и KeyboardInterrupt
"""

import socket
import threading
import argparse
import struct
import os
import sys

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---------- helpers for framing ----------
def send_bytes(sock: socket.socket, data: bytes):
    length = struct.pack('!I', len(data))  # 4 bytes big-endian
    sock.sendall(length + data)

def recv_all(sock: socket.socket, n: int) -> bytes:
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed while receiving")
        buf += chunk
    return buf

def recv_message(sock: socket.socket) -> bytes:
    # read 4-byte length
    header = recv_all(sock, 4)
    (length,) = struct.unpack('!I', header)
    if length == 0:
        return b''
    return recv_all(sock, length)

# ---------- crypto ----------
def derive_aes_key(shared_secret: bytes, info: bytes = b'handshake data') -> bytes:
    # HKDF -> 32 byte key for AES-256
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=info,
    )
    return hkdf.derive(shared_secret)

def encrypt_message(aes_key: bytes, plaintext: str) -> bytes:
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)  # recommended 96-bit nonce for GCM
    ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), associated_data=None)
    return nonce + ct  # send nonce || ciphertext (ciphertext includes tag)

def decrypt_message(aes_key: bytes, payload: bytes) -> str:
    if len(payload) < 13:
        raise ValueError("Payload too short")
    nonce = payload[:12]
    ct = payload[12:]
    aesgcm = AESGCM(aes_key)
    pt = aesgcm.decrypt(nonce, ct, associated_data=None)
    return pt.decode('utf-8')

# ---------- protocol for key exchange ----------
# We'll send public keys as raw 32-byte values (X25519 public bytes)
def perform_key_exchange_as_server(conn: socket.socket) -> bytes:
    # server generates ephemeral key, sends public, receives peer public, computes shared
    private = X25519PrivateKey.generate()
    public = private.public_key().public_bytes()
    # send server public
    send_bytes(conn, public)
    # receive client public
    peer_pub_bytes = recv_message(conn)
    peer_public = X25519PublicKey.from_public_bytes(peer_pub_bytes)
    shared = private.exchange(peer_public)
    return shared

def perform_key_exchange_as_client(sock: socket.socket) -> bytes:
    # client receives server public, sends client public, computes shared
    server_pub_bytes = recv_message(sock)
    server_public = X25519PublicKey.from_public_bytes(server_pub_bytes)
    private = X25519PrivateKey.generate()
    public = private.public_key().public_bytes()
    send_bytes(sock, public)
    shared = private.exchange(server_public)
    return shared

# ---------- IO threads ----------
def receiver_thread(sock: socket.socket, aes_key: bytes, name_remote='Peer'):
    try:
        while True:
            try:
                payload = recv_message(sock)
            except ConnectionError:
                print("\nConnection closed by remote.")
                break
            if not payload:
                print("\nReceived empty payload, closing.")
                break
            try:
                msg = decrypt_message(aes_key, payload)
            except Exception as e:
                print(f"\n[!] Failed to decrypt message: {e}")
                continue
            # print with newline handling so user's input isn't destroyed
            print(f"\n{name_remote}: {msg}\nMe: ", end='', flush=True)
    except KeyboardInterrupt:
        pass

def sender_loop(sock: socket.socket, aes_key: bytes):
    try:
        while True:
            msg = input("Me: ")
            if msg.lower() in ('/quit', '/exit'):
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                sock.close()
                print("Bye.")
                break
            payload = encrypt_message(aes_key, msg)
            send_bytes(sock, payload)
    except (BrokenPipeError, ConnectionError):
        print("\nConnection lost.")
    except KeyboardInterrupt:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        sock.close()
        print("\nInterrupted. Exiting.")

# ---------- server & client ----------
def run_server(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        print(f"Listening on {host}:{port} ...")
        conn, addr = s.accept()
        with conn:
            print("Connection from", addr)
            try:
                shared = perform_key_exchange_as_server(conn)
            except Exception as e:
                print("Key exchange failed:", e)
                return
            aes_key = derive_aes_key(shared)
            print("Secure channel established. Type messages. /quit to exit.")
            t = threading.Thread(target=receiver_thread, args=(conn, aes_key, f"{addr}"), daemon=True)
            t.start()
            sender_loop(conn, aes_key)

def run_client(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to {host}:{port} ...")
        s.connect((host, port))
        try:
            shared = perform_key_exchange_as_client(s)
        except Exception as e:
            print("Key exchange failed:", e)
            return
        aes_key = derive_aes_key(shared)
        print("Secure channel established. Type messages. /quit to exit.")
        t = threading.Thread(target=receiver_thread, args=(s, aes_key, "Server"), daemon=True)
        t.start()
        sender_loop(s, aes_key)

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('server', 'client'), required=True)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=12345)
    args = parser.parse_args()

    try:
        if args.mode == 'server':
            run_server(args.host, args.port)
        else:
            run_client(args.host, args.port)
    except KeyboardInterrupt:
        print("\nExiting by user.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    main()
