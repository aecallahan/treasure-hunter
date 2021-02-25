'''
Watches generated log files and dispatches them to game player
'''
import json
import os
import tailer

from game_player import GameStateObject, take_game_action

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
            take_game_action(log, game)

if __name__ == "__main__":
    play_game_from_logs()
