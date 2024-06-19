"""
Dear evaluator, I've originally done the Movie Project phase 1 on the regular
student track, which is quite a bit different from the phase 1 project on the
advanced track, which I'm currently on, especially pertaining to bonuses. I've
only done the bonuses after my core assignment was evaluated, so I'm including
those bonuses in my current submission. The Fuzzy String Matching was fun and
challenging, I've put it to work on delete_movie, update_movie and srch_movie.
The API seems to have its own fuzzy string matching, so I'm
just printing out the candidates that the API proposes when adding movies (2.)

The OMDb API no longer seems to offer the posters to free accounts, so I had
to go looking for a different one. In the end after spending several days with
this, I didn't find it meaningful for my learning to interact with two APIs,
so I didn't implement IMDB links and country flags which are not provided by
'themoviedb' API. Instead, I focused my final polish on tinkering with html
and CSS and I did include hyperlinks to images, but merely as google results.

Thanks for reading!
"""

import os
import argparse
from storage.storage_json import StorageJson
from storage.storage_csv import StorageCsv
from movie_app import MovieApp

DATA_SUBDIR = "data"
CLI_HELP_MSG = "work on a movie db specified by <filename>"


def obtain_db_filepath():
    """Guides user through error message and help hint interaction towards
    specifying a DB filename. If path not extant, starts a new database."""
    parser = argparse.ArgumentParser(prog='main.py',
                                     description='MovieApp: DB manipulation')
    parser.add_argument("filename", help=CLI_HELP_MSG)
    args = parser.parse_args()
    if not args.filename:
        raise ValueError("Filename can't be an empty string.")
    if '.' not in args.filename:  # then default to .json
        data_file_path = os.path.join(DATA_SUBDIR, args.filename + '.json')
    else:
        if args.filename[-5:] != ".json" and args.filename[-4:] != ".csv":
            raise TypeError("Bad extension, must be .json or .csv or no ext")
        if ((args.filename[-5:] == ".json" and len(args.filename) < 6)
                or (len(args.filename) < 5)):
            raise ValueError("No <filename> found, ext only doesn't suffice")
        data_file_path = os.path.join(DATA_SUBDIR, args.filename)
    if not os.path.exists(data_file_path):
        fd = os.open(data_file_path, os.O_CREAT)
        os.close(fd)
        print(f"<{args.filename}> not found, starting a new database...")
    else:
        print(f"Starting MovieApp at ./{data_file_path}")
    return data_file_path


def main():
    """Expects CL argument specifying a DB filename, creates either a
    StorageJson or StorageCsv object, then runs MovieApp for it."""
    try:
        db_filepath = obtain_db_filepath()
    except Exception as e:  # the general Exception made sense because exiting
        print(f"Error: {e}")
        exit(1)
    if db_filepath[-5:] == ".json":
        storage = StorageJson(db_filepath)
    else:
        storage = StorageCsv(db_filepath)
    movie_app = MovieApp(storage)
    movie_app.run()


if __name__ == "__main__":
    main()
