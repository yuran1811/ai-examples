from os import getenv
from dotenv import load_dotenv
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from threading import Thread, Event

load_dotenv()

HOST = getenv("HOST") or "127.0.0.1"
PORT = int(getenv("PORT")) or 1811
MAX_BUF_SIZE = int(getenv("MAX_BUF_SIZE")) or 1024

ENCODING = "utf8"


class Client:
    def __init__(self, host=HOST, port=PORT):
        self.active = False
        self.exit_signal = Event()

        self.conn = socket(AF_INET, SOCK_STREAM)
        self.connect_to_server(host, port)

    def connect_to_server(self, host: str, port: int):
        try:
            self.conn.connect((host, port))
        except Exception as e:
            print(f"[ERR] - failed to conn to the server: {e}")

    def shutdown_connection(self):
        try:
            self.conn.shutdown(SHUT_RDWR)
        except Exception as e:
            print(f"[ERR] - shutdown connection: {e}")
        finally:
            self.conn.close()

    def send_msg(self, msg: str):
        try:
            self.conn.send(msg.encode(ENCODING))
        except Exception as e:
            print(f"[ERR] - failed to send msg: {e}")

    def recv_msg(self, exit_signal: Event):
        try:
            while not exit_signal.is_set() or (self.active == False):
                global data
                data = self.conn.recv(MAX_BUF_SIZE)
                if not data:
                    self.shutdown_connection()
                    break

                self.active = True
                print(data.decode(ENCODING))
        except Exception as e:
            print(f"[ERR] - failed to receive msg: {e}")
        except KeyboardInterrupt:
            print("[INTERRUPTED] - detect ctrl+c from recv msg")
            exit_signal.set()

    def run(self):
        try:
            Thread(target=self.recv_msg, args=(self.exit_signal,), daemon=True).start()

            while not self.exit_signal.is_set():
                msg = input()
                if msg == "[terminated]":
                    break

                self.active = True
                self.send_msg(msg)
        except Exception as e:
            print(e)
            self.exit_signal.set()
        except KeyboardInterrupt:
            print("[INTERRUPTED] - detect ctrl+c")
            self.exit_signal.set()
        finally:
            self.shutdown_connection()


if __name__ == "__main__":
    Client().run()
