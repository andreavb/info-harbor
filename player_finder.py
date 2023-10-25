import sys

import chess.pgn

from chess_results import download_all_pgns, parse_main_page
from game_handling import generate_games_csv, refine_games

def collect_player_data():
    player = {'id': '',
              'name': '',
              'color': ''
            }

    player['id']  = input("What is the FIDE ID? ")
    player['name'] = input("What is the player name? ")
    player['color'] = input("Which color you want to prepare against (white/black)?  ")
    return player


def player_finder(player):

    # some house keeping
    tournaments_filepath = "current_tournaments.txt"
    final_games_file = player['id'] + "_" + player['color'] + ".pgn"
    csv_file = final_games_file.replace('pgn', 'csv')
    elasticsearch_index_name = csv_file.replace('.csv', '').lower()

    # step 1: parse main CR page, search for player, return file with tournaments played
    parse_main_page(player['id'], tournaments_filepath)

    # step 2: from the list of tournaments played, search those with downloadable games
    download_all_pgns(tournaments_filepath)

    # step 3: select only relevant games and concat them in a single file
    refine_games(player, final_games_file)

    # step 4: generate CSV file to be used within Elastic Stack
    generate_games_csv(final_games_file, csv_file)


def main():

    if len(sys.argv) != 4:
        player = collect_player_data()
    else:
        player = {'id': sys.argv[1],
              'name': sys.argv[2],
              'color': sys.argv[3]
            }

    player_finder(player)


if __name__ == "__main__":
    main()

