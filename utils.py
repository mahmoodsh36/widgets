import subprocess
import threading

def handle_command(command, handler):
    # start the subprocess
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # process the output line by line
    for line in process.stdout:
        handler(line.strip())

def handle_subprocess_subscription(command, handler):
    output_thread = threading.Thread(target=handle_command, args=(command, handler))
    output_thread.start()