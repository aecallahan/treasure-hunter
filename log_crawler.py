'''
Watches generated log files and dispatches them to game player
'''
import json
import os
import tailer

from game_player import GameStateObject
from log_parser import parse_log

# works for windows
filePath = os.path.join("..", "..", "..", "AppData", "LocalLow", "Wizards Of The Coast", "MTGA", \
    "Player.log")


def play_game_from_logs():
    '''Create game object and call game player for each new log seen'''
    game = GameStateObject()
    number_of_logs = 0
    for line in tailer.follow(open(filePath)):
        if line.startswith('{ "transactionId"'):
            number_of_logs += 1
            print(f"number of logs: {number_of_logs}")
            log = json.loads(line)
            parse_log(log, game)

def get_newest_log() -> list:
    '''Retrieves the last 10 lines from the log file'''
    return tailer.tail(open(filePath), 10)

if __name__ == "__main__":
    play_game_from_logs()
