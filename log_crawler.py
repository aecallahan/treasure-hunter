'''
Watches generated log files and dispatches them to game player
'''
import json
import os
from pathlib import Path
import tailer


def create_game_log_generator():
    '''Log generator to yield subsequent logs from MTGA'''
    # works for windows
    file_path = os.path.join(Path.home(), "AppData", "LocalLow", "Wizards Of The Coast",
        "MTGA", "Player.log")
    for line in tailer.follow(open(file_path)):
        if line.startswith('{ "transactionId"'):
            yield json.loads(line)

def get_newest_log() -> list:
    '''Retrieves the last 10 lines from the log file'''
        # works for windows
    file_path = os.path.join(Path.home(), "AppData", "LocalLow", "Wizards Of The Coast",
        "MTGA", "Player.log")
    return tailer.tail(open(file_path), 10)
