from .istorage import IStorage


class StorageCsv(IStorage):
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
            lines = fd.readlines()
        if not lines:
            return dict_of_dicts
        try:
            for i, line in enumerate(lines):
                if i == 0:
                    continue
                title, rating, year, poster, notes = line.split(',')
                notes = notes.strip()  # rm trailing \n from line end
                movie = {title: {'year': int(year),
                                 'rating': float(rating),
                                 'poster': poster,
                                 'notes': notes}
                         }
                dict_of_dicts.update(movie)
        except Exception as e:  # whichever the error, visualize it
            print(f"Error reading from csv: {e}")
        return dict_of_dicts

    def add_movie(self, title: str, year: str, rating: float, poster: str):
        """Adds a movie to the movie database.
        Loads the information from the CSV file, adds the movie,
        and saves it. The function doesn't validate input."""
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
        self._write_to_csv(movies)

    def delete_movie(self, title: str):
        """Deletes a movie from the movie database. Loads the information from
        the CSV file, deletes the movie, and saves it. The function doesn't
        validate the input. Exact title already proven to exist by caller."""
        movies = self.list_movies()
        movies.pop(title)
        self._write_to_csv(movies)

    def update_movie(self, title: str):
        """Updates a movie from the movie database with user-specified notes.
        Allows any input for 'notes', incl. empty string (default)."""
        movies = self.list_movies()
        movies[title]['notes'] = input("Enter movie notes:\n> ")
        self._write_to_csv(movies)

    def _write_to_csv(self, movies: dict):
        """Protocol for writing to .csv."""
        lines = "title,rating,year,poster,notes\n"
        for k, v in movies.items():
            lines += (f"{k},{v['rating']},{v['year']},"
                      f"{v['poster']},{v['notes']}\n")
        with open(self.file_path, "w") as fd:
            fd.write(lines)
