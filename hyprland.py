import os
import socket
import threading

# λ socat -U - UNIX-CONNECT:$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock | while read -r line; do echo "$line"; done

listeners = []

# Define your handlers
def handle(event_line):
    for listener in listeners:
        listener(event_line.strip())

def main():
    # Get the socket path from environment variables
    hypr_socket_path = os.path.join(
        os.getenv("XDG_RUNTIME_DIR", ""),
        "hypr",
        os.getenv("HYPRLAND_INSTANCE_SIGNATURE", ""),
        ".socket2.sock"
    )

    # Ensure the socket path exists
    if not os.path.exists(hypr_socket_path):
        raise FileNotFoundError(f"Socket not found at {hypr_socket_path}")

    # Connect to the UNIX socket
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(hypr_socket_path)
        with sock.makefile('r') as f:  # Read socket as a file-like object
            for line in f:
                handle(line.strip())  # Pass each line to the handler

def add_listener(func):
    listeners.append(func)

thread = threading.Thread(target=main, args=())
thread.start()