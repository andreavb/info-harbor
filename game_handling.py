import csv
import io
import os
import re

import chess.pgn


def concatenate_all_games(directory_path, output_file):
    try:
        with open(output_file, "w") as outfile:
            for filename in os.listdir(directory_path):
                if filename.endswith(".pgn"):
                    file_path = os.path.join(directory_path, filename)
                    with open(file_path, "r") as infile:
                        outfile.write(infile.read())
    except Exception as e:
        print(f"An error occurred: {e}")


def generate_games_csv(input_pgn_file, csv_file):
    # Open the PGN file and parse games
    with open(input_pgn_file, "r") as f:
        game_data = f.read()

    pgn = io.StringIO(game_data)

    # Extract and write data to CSV

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "event",
                "white_name",
                "black_name",
                "white_rating",
                "black_rating",
                "result",
                "eco",
            ]
        )

        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
        
            headers = game.headers
            event = headers.get("Event", "")
            white_name = headers.get("White", "")
            black_name = headers.get("Black", "")
            white_rating = headers.get("WhiteElo", "")
            black_rating = headers.get("BlackElo", "")
            result = headers.get("Result", "")
            eco = headers.get("ECO", "")
            datetime = headers.get("ÜTCTime", "")

            writer.writerow(
                [
                    event,
                    white_name,
                    black_name,
                    white_rating,
                    black_rating,
                    result,
                    eco,
                ]
            )


def is_game_relevant(str_pgn_game, player, color):
    pgn_game = io.StringIO(str_pgn_game)
    game = chess.pgn.read_game(pgn_game)

    if game is None:
        return False

    headers = game.headers
    white_name = headers.get("White", "")
    black_name = headers.get("Black", "")

    player_names = set(player.split(" "))

    if color == "white" and all(name in white_name for name in player_names):
        return True
    if color == "black" and all(name in black_name for name in player_names):
        return True
    if color == "all" and (
        all(name in white_name for name in player_names)
        or all(name in black_name for name in player_names)
    ):
        return True
    return False


def refine_games(player, refined_games_file):

    # first, we concatenate all games within a single file
    directory_path = "/tmp/games"
    all_games_file = player["id"] + "_all_games.pgn"

    concatenate_all_games(directory_path, all_games_file)

    # next, we select the relevant games from this huge guy
    # PROFIT

    # read input PGN file
    with open(all_games_file, "r") as input_file:
        all_games = input_file.read()

    # separate games
    games = re.split(r"\n(?=\[Event  *)", all_games)

    # filter relevant games
    relevant_games = list(
        filter(
            lambda game: is_game_relevant(
                game, player["name"], player["color"]
            ),
            games,
        )
    )

    # write output PGN file
    with open(refined_games_file, "w") as output_file:
        output_file.write("\n".join(relevant_games))

    # remove *_all_games.pgn file as no longer needed
    os.remove(all_games_file)

