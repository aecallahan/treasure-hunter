'''Outermost functions which initiate game playing'''
import json
import os
import pathlib
import shutil

from log_crawler import create_game_log_generator
from log_parser import parse_log
from game_player import GameStateObject

LOGGING = True

def play_game():
    '''Initiate game object and play a game'''
    current_path = os.getcwd()
    create_subdirectory()
    number_of_logs = 0
    game = GameStateObject()
    log_generator = create_game_log_generator()
    for log in log_generator:
        number_of_logs += 1
        file_writer = open(os.path.join(current_path, 'logs', 'log_parser_logs.log'), 'a')
        file_writer.write(
            f"\n\n---------------------parsing log: {number_of_logs}---------------------\n\n"
            )
        file_writer.close()
        # print('\n\n')
        # print(f"parsing log: {number_of_logs}")
        # print('\n\n')
        with open(os.path.join(current_path, 'logs', f'log{number_of_logs}.json'), 'w') \
          as output_file:
            json.dump(log, output_file, indent=4)
        parse_log(log, game)

def create_subdirectory():
    '''Create a 'logs' subdirectory to write logs to. Delete the directory first in case it
    already exists'''
    current_path = os.getcwd()
    logs_subdirectory_path = os.path.join(current_path, 'logs')
    try:
        shutil.rmtree(logs_subdirectory_path)
    except FileNotFoundError:
        pass
    pathlib.Path(logs_subdirectory_path).mkdir(exist_ok=True)
    # Create file to write log_parser logs to
    file_writer = open(os.path.join(logs_subdirectory_path, 'log_parser_logs.log'), 'w')
    file_writer.close()

if __name__ == "__main__":
    play_game()
