import socket

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


def receive_full_message(sock):
    try:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            return None

        decoded = data.decode("utf-8")
        first_space = decoded.find(" ")

        if first_space == -1:
            return "Invalid response format from server"

        length_str = decoded[:first_space]
        if not length_str.isdigit():
            return "Invalid response format from server"

        message_length = int(length_str)
        full_data = decoded[first_space + 1:]
        remaining = message_length - len(full_data.encode("utf-8"))

        while remaining > 0:
            chunk = sock.recv(BUFFER_SIZE)
            if not chunk:
                return None
            full_data += chunk.decode("utf-8")
            remaining -= len(chunk)

        return full_data

    except Exception as e:
        return f"Error: {e}"


def print_help():
    print("Available commands:")
    print("  ADD <key> <value>")
    print("  GET <key>")
    print("  REMOVE <key>")
    print("  LIST")
    print("  COUNT")
    print("  CLEAR")
    print("  UPDATE <key> <new_value>")
    print("  POP <key>")
    print("  QUIT")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected to server.")
        print_help()

        while True:
            command = input("client> ").strip()

            if not command:
                print("Please enter a command.")
                continue

            if command.lower() == "exit":
                command = "QUIT"

            s.sendall(command.encode("utf-8"))
            response = receive_full_message(s)
            print(f"Server response: {response}")

            if command.upper() == "QUIT":
                break


if __name__ == "__main__":
    main()