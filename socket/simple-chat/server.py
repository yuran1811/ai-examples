from os import getenv
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread, Event
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR

load_dotenv()

HOST = getenv("HOST") or "127.0.0.1"
PORT = int(getenv("PORT")) or 1811
MAX_BUF_SIZE = int(getenv("MAX_BUF_SIZE")) or 1024

SERVER_BACKLOG = 3
SERVER_TIMEOUT = 24

ENCODING = "utf8"


def print_log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d|%H:%M:%S')}] {msg}")


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.exit_signal = Event()

        self.clients: dict[socket, tuple] = {}

        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((host, port))
        # self.server.settimeout(SERVER_TIMEOUT)

        self.server.listen(SERVER_BACKLOG)
        print_log(f"[INFO] - server started on {host}:{port}\n")

    def shutdown_connection(self, conn: socket):
        try:
            print_log(f"\t[INFO] - shutting down conn from {self.clients[conn]}...")
            conn.shutdown(SHUT_RDWR)
        except Exception as e:
            print_log(f"\t[ERR] - shutdown conn: {e}")
        finally:
            conn.close()
            print_log(f"\t[INFO] - {self.clients[conn]} disconnected")

            del self.clients[conn]

    def shutdown_server(self):
        try:
            print_log("[INFO] - shutting down server...")
            self.server.shutdown(SHUT_RDWR)
        except Exception as e:
            print_log(f"[ERR] - shutdown server: {e}")
        finally:
            self.server.close()
            print_log("[INFO] - server stopped")

    def stop(self):
        self.exit_signal.set()
        for conn in self.clients:
            self.shutdown_connection(conn)

    def broadcast(self, msg, prefix=""):
        print("broadcasting...")
        for conn in self.clients:
            self.send_msg(conn, prefix + msg)

    def send_msg(self, conn: socket, msg: str):
        try:
            conn.send(msg.encode(ENCODING))
        except Exception as e:
            print_log(f"\t [ERR] - failed to send msg to {self.clients[conn]}: {e}")

    def recv_msg(self, conn: socket, addr: tuple, exit_signal: Event):
        try:
            while not exit_signal.is_set():
                data = conn.recv(MAX_BUF_SIZE)
                if not data or data == "[terminated]".encode(ENCODING):
                    self.shutdown_connection(conn)
                    break

                self.broadcast(data.decode(ENCODING), f"{addr}: ")
        except Exception as e:
            print_log(f"\t[ERR] - failed to recv msg from {addr}: {e}")
        except KeyboardInterrupt:
            print_log("[INTERRUPTED] - detect ctrl+c from recv msg")
            self.stop()

    def run(self):
        try:
            while not self.exit_signal.is_set():
                conn, addr = self.server.accept()
                self.clients[conn] = addr

                print_log(f"[INFO] - {addr} connected")

                Thread(
                    target=self.recv_msg, args=(conn, addr, self.exit_signal)
                ).start()
        except Exception as e:
            print_log(e)
            self.stop()
        except KeyboardInterrupt:
            print_log("[INTERRUPTED] - detect ctrl+c")
            self.stop()
        finally:
            self.shutdown_server()


if __name__ == "__main__":
    Server().run()
