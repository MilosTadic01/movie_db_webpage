import json
from .istorage import IStorage


class StorageJson(IStorage):
    """A subclass of an abstract class, meant to handle json file format."""
    def __init__(self, file_path_arg):
        self._file_path = file_path_arg

    @property
    def file_path(self):
        """I originally thought I might also need to set it, but it no longer
        seems to be the case. Still, I'm leaving the @property for now."""
        return self._file_path

    def list_movies(self):
        """Returns a dictionary of dictionaries that contains the movies
        information in the database. The function loads the information
        from a JSON file and returns the data."""
        with open(self.file_path, "r") as fd:
            dict_of_dicts = {}  # security measure in case of empty file
            raw_str = fd.read()
        if not raw_str:
            return dict_of_dicts
        try:
            dict_of_dicts = json.loads(raw_str)
        except Exception as e:  # whatever err json raises I want it
            print(f"Error reading from json: {e}")
        return dict_of_dicts

    def add_movie(self, title: str, year: str, rating: float, poster: str):
        """Adds a movie to the movie database.
        Loads the information from the JSON file, adds the movie,
        and saves it. The function doesn't validate input. To avoid loading
        DB in StorageApp, I had to have the 2 messages here"""
        movies = self.list_movies()
        if title in movies.keys():
            print(f"Movie {title} already exists!")
            return
        movie = {title: {"year": year,
                         "rating": rating,
                         "poster": poster,
                         "notes": ''}
                 }
        movies.update(movie)
        self._write_to_json(movies)
        print(f"Movie {title} successfully added")

    def delete_movie(self, title: str):
        """Deletes a movie from the movie database. Loads the information from
        the JSON file, deletes the movie, and saves it. The function doesn't
        validate the input. Exact title already proven to exist by caller."""
        movies = self.list_movies()
        movies.pop(title)
        self._write_to_json(movies)

    def update_movie(self, title: str):
        """Updates a movie from the movie database with user-specified notes.
        Allows any input for 'notes', incl. empty string (default)."""
        movies = self.list_movies()
        movies[title]['notes'] = input("Enter movie notes:\n> ")
        self._write_to_json(movies)

    def _write_to_json(self, movies: dict):
        """Protocol for writing to .json."""
        movies_as_str = json.dumps(movies)
        with open(self.file_path, "w") as fd:
            fd.write(movies_as_str)
