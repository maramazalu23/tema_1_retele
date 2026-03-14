import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            self.data[key] = value
        return "OK - record add"

    def get(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            return f"DATA {self.data[key]}"

    def remove(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            del self.data[key]
        return "OK value deleted"

    def list_all(self):
        with self.lock:
            if not self.data:
                return "DATA|"
            items = [f"{key}={value}" for key, value in self.data.items()]
            return "DATA|" + ",".join(items)

    def count(self):
        with self.lock:
            return f"DATA {len(self.data)}"

    def clear(self):
        with self.lock:
            self.data.clear()
        return "all data deleted"

    def update(self, key, value):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            self.data[key] = value
        return "Data updated"

    def pop_value(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            value = self.data.pop(key)
        return f"DATA {value}"


state = State()


def build_response_packet(response_text):
    response_bytes = response_text.encode("utf-8")
    header = f"{len(response_bytes)} ".encode("utf-8")
    return header + response_bytes


def process_command(command):
    command = command.strip()
    if not command:
        return "ERROR empty command"

    parts = command.split()
    cmd = parts[0].upper()

    if cmd == "ADD":
        if len(parts) < 3:
            return "ERROR invalid command format"
        key = parts[1]
        value = " ".join(parts[2:])
        return state.add(key, value)

    if cmd == "GET":
        if len(parts) != 2:
            return "ERROR invalid command format"
        key = parts[1]
        return state.get(key)

    if cmd == "REMOVE":
        if len(parts) != 2:
            return "ERROR invalid command format"
        key = parts[1]
        return state.remove(key)

    if cmd == "LIST":
        if len(parts) != 1:
            return "ERROR invalid command format"
        return state.list_all()

    if cmd == "COUNT":
        if len(parts) != 1:
            return "ERROR invalid command format"
        return state.count()

    if cmd == "CLEAR":
        if len(parts) != 1:
            return "ERROR invalid command format"
        return state.clear()

    if cmd == "UPDATE":
        if len(parts) < 3:
            return "ERROR invalid command format"
        key = parts[1]
        value = " ".join(parts[2:])
        return state.update(key, value)

    if cmd == "POP":
        if len(parts) != 2:
            return "ERROR invalid command format"
        key = parts[1]
        return state.pop_value(key)

    if cmd == "QUIT":
        if len(parts) != 1:
            return "ERROR invalid command format"
        return "BYE"

    return "ERROR unknown command"


def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode("utf-8").strip()
                response = process_command(command)

                packet = build_response_packet(response)
                client_socket.sendall(packet)

                if command.upper() == "QUIT":
                    break

            except Exception as e:
                error_message = f"ERROR {str(e)}"
                packet = build_response_packet(error_message)
                client_socket.sendall(packet)
                break


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"[SERVER] Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()