import subprocess
import re

import utils

def get_default_sink():
    out = subprocess.check_output(['pactl', 'get-default-sink'])
    return out.strip()

def get_default_sink_volume():
    out = subprocess.check_output(['pactl',
                                   'get-sink-volume',
                                   get_default_sink()]).decode()
    return re.findall('([0-9]+)%', out)[0]

def set_default_sink_volume(volume):
    subprocess.run(['pactl',
                    'set-sink-volume',
                    get_default_sink(),
                    f'{volume}%'])

listeners = []
def add_listener(listener):
    listeners.append(listener)

def handler(line):
    for listener in listeners:
        listener(line)

def start_listener():
    cmd = [
        'sh',
        '-c',
        'pactl subscribe | grep --line-buffered "sink"'
    ]
    utils.handle_subprocess_subscription(cmd, handler)

start_listener()