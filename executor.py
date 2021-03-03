from log_crawler import create_game_log_generator
from log_parser import parse_log
from game_player import GameStateObject


def play_game():
    game = GameStateObject()
    log_generator = create_game_log_generator()
    for log in log_generator:
        parse_log(log, game)

if __name__ == "__main__":
    play_game()
