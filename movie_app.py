import sys
import os
import random
import matplotlib.pyplot as plt
from storage.storage_json import StorageJson
from storage.storage_csv import StorageCsv
from utils.data_fetcher import fetch_data
from utils.fuzzy_string_matching import get_fuzzy_srch_candidates
from utils.utils import Utility

MATCH_COEFFICIENT = 0.7
FAKE_INT_MAX = 2147483648
HTML_TEMPL = os.path.join('templates', 'index_template.html')
HTML_INDEX = 'index.html'
CSS_PATH = os.path.join('css', 'style.css')
GRID_PLACEHOLDER = '__TEMPLATE_MOVIE_GRID__'
TITLE_PLACEHOLDER = '__TEMPLATE_TITLE__'
GOOGLE_PREFIX = 'https://www.google.com/search?q='
MY_TITLE = 'Watchlist'
WELCOME_HEADER = "********** My Movies Database **********"
PROMPT_FOR_NUM = 'Enter the number of the movie to'
PROMPT_FOR_TITLE = 'Enter the title of the movie to'
MAIN_MENU = """
Menu:
0. Exit
1. List movies
2. Add movie
3. Delete movie
4. Update movie
5. Stats
6. Random movie
7. Search movie
8. Movies sorted by rating
9. Movies sorted by year
10. Filter movies
11. Create ratings histogram
12. Generate webpage
"""
SORTING_MENU = """
0. not at all
1. by rating
2. by year
3. alphabetically
"""


class MovieApp:
    """User interface for a movie DB with CRUD and more."""
    def __init__(self, storage: (StorageJson, StorageCsv)):
        if not isinstance(storage, (StorageJson, StorageCsv)):
            raise TypeError("Error: Can't init MovieApp w/o valid type")
        self._storage = storage

    def _command_exit_program(self):
        """Has 'self' to fit the function dispatcher syntax.
        Utilizes it to forego style check fail."""
        if self:
            print("Bye!")
            sys.exit(0)

    def _command_list_movies(self):
        """Print out entries in storage in a pretty format"""
        movies = self._storage.list_movies()
        if not movies:
            print("Empty data, no movies found.")
            return
        print(f"{len(movies)} movies in total:")
        for i, (k, v) in enumerate(movies.items()):
            print(f"  {i + 1}. <{k}> ({v['year']}), rating: {v['rating']}")

    def _command_add_movie(self):
        """Rely on fetching from an API to add entry to storage"""
        while True:
            new_movie_title = input("Enter the title of the movie to add: ")
            if new_movie_title:
                break
            print("Error: Title may not be an empty string.")
        data = fetch_data(new_movie_title)
        if data is None:
            return
        title, year, rating, poster = data
        self._storage.add_movie(title, year, rating, poster)
        print(f"Movie {title} successfully added")

    def _command_delete_movie(self):
        """Remove entry from storage. To minimize the iterations of data
        imports per command exec, I'm delegating that to _fetch_lookup_matches
        which results in me always saying 'This is what I found', even when
        exact match. I like it that way, it's an extra interface step but
        nice and safe and transparent."""
        exact_title = self._obtain_match_for_action('delete')
        if not exact_title:
            return
        self._storage.delete_movie(exact_title)
        print(f"Movie <{exact_title}> successfully deleted!")

    def _command_update_movie(self):
        """Update movie to add 'notes'. To minimize the iterations of data
        imports per command exec, I'm delegating that to _fetch_lookup_matches
        which results in me always saying 'This is what I found', even when
        exact match. I like it that way, it's an extra interface step but
        nice and safe and transparent."""
        exact_title = self._obtain_match_for_action('update')
        if not exact_title:
            return
        self._storage.update_movie(exact_title)
        print(f"Movie <{exact_title}> successfully updated")

    def _command_movie_stats(self):
        """Print the avg && median rating, best && worst rated movies"""
        movies = self._storage.list_movies()
        mov_count = len(movies)
        if mov_count == 0:
            print("Empty data, no movies found.")
            return
        midpoint = mov_count // 2
        sorted_titles = sorted(movies, key=lambda movie:
                               (movies[movie]['rating'], movie), reverse=True)
        sum_of_ratings = 0
        for value in movies.values():
            sum_of_ratings += value['rating']
        if mov_count % 2 == 0:
            median_rating = (
                (movies.get(sorted_titles[midpoint])['rating'] +
                 movies.get(sorted_titles[midpoint - 1])['rating']) / 2
                )
        else:
            median_rating = movies.get(sorted_titles[midpoint])['rating']
        print(f"Average rating: {round(sum_of_ratings / mov_count, 1)}")
        print(f"Median rating: {round(median_rating, 1)}")
        print(f"Best movie: <{sorted_titles[0]}>, "
              f"{movies.get(sorted_titles[0])['rating']}")
        print(f"Worst movie: <{sorted_titles[-1]}>, "
              f"{movies.get(sorted_titles[-1])['rating']}")

    def _command_random_movie(self):
        """Print random movie"""
        movies = self._storage.list_movies()
        db_len = len(movies)
        if db_len == 0:
            return
        random_idx = random.randrange(0, db_len)
        for i, (k, v) in enumerate(movies.items()):
            if i == random_idx:
                print(f"Your movie for tonight: <{k}>, "
                      f"it's rated {v['rating']}")
                break

    def _command_search_movie(self):
        """Prompt for query, print matches or match candidates."""
        query = input("Enter part of (or entire) movie name:\n> ").strip()
        candidates = self._fetch_lookup_matches(query)
        if not candidates:
            print("\nMovie not part of this database.")
            return
        print(f"\nThis is what I've found for <{query}>:")
        for i, mov in enumerate(candidates):
            k, v = next(iter(mov.items()))
            print(f"  {i + 1}. <{k}> ({v['year']}), rating: {v['rating']}")

    @staticmethod
    def _print_after_sorting_by(criterion: str, movies: dict):
        """Sorts movies according to 'criterion', then prints sorted.
        An abstracted utility function for two similarly working functions."""
        sorted_titles = sorted(
            movies, key=lambda movie:
            (movies[movie][criterion], movie), reverse=True
        )
        for mov in sorted_titles:
            print(f"  <{mov}>: {movies[mov][criterion]}")

    def _command_movies_sorted_by_rating(self):
        """Reverse sort the movies in storage by rating and print them."""
        movies = self._storage.list_movies()
        self._print_after_sorting_by('rating', movies)

    def _command_movies_sorted_by_year(self):
        """Reverse sort the movies in storage by year and print them."""
        movies = self._storage.list_movies()
        self._print_after_sorting_by('year', movies)

    @staticmethod
    def _init_flt_val(value: (int, float), txt: str, d_type: type):
        """Initialize each filter value for cmd filter_movies.
        Called inside 'while True' and a 'try:' block."""
        if (isinstance(value, int) and value < 0 or
                isinstance(value, float) and value < 0.0):  # not set
            temp = input(f"Enter {txt}: ")
            if temp == '':  # if irrelevant to user
                if type is float:
                    value = 0.0
                else:
                    value = 0
            else:
                value = d_type(temp)
            return value

    def _command_filter_movies(self):
        """Only print the movies which match the filter criteria.
        The initialization to -1 facilitates repeat prompting only for those
        values which have not yet been accepted from user input as the loop
        keeps going defensively. Input of '' voids the filter."""
        movies = self._storage.list_movies()
        found_a_match = False
        min_rt = -1.0  # the value which signifies "not set yet"
        start_yr = -1
        end_yr = -1
        while True:
            try:
                min_rt = self._init_flt_val(min_rt, 'minimum_rating', float)
                if isinstance(min_rt, float) and min_rt < 0:  # bad
                    raise ValueError("Rating can't be negative")
                start_yr = self._init_flt_val(start_yr, 'start year', int)
                if isinstance(start_yr, int) and start_yr < 0:  # bad
                    raise ValueError("Start year can't be negative")
                end_yr = self._init_flt_val(end_yr, 'end year', int)
                if isinstance(end_yr, int) and end_yr < 0:  # bad
                    raise ValueError("End year can't be negative")
                break
            except ValueError as e:
                print(f"Error: {e}")
        print("****The following movies match your filter criteria:")
        for k, v in movies.items():
            if (v['rating'] >= min_rt and
               start_yr <= v['year'] <= end_yr):
                print(f"  <{k}> ({v['year']}), rating: {v['rating']}")
                found_a_match = True
        if not found_a_match:
            print("<None>")

    def _command_create_ratings_histogram(self):
        """Drop a file to subdir 'data' with a matplotlib-made histogram"""
        movies = self._storage.list_movies()
        ratings = list(rat.get('rating') for rat in movies.values())
        plt.hist(ratings, bins=20, range=(0, 10),
                 edgecolor='black', color='gold')
        plt.xlim(0, 10)
        plt.title('Ratings Histogram')
        plt.xlabel('Ratings')
        plt.ylabel('Number of movies')
        filename = input("Enter filename for the histogram: ").strip()
        if '.' in filename:  # prevent user-defined extensions
            filename = filename[:filename.index('.')]
        if not filename:
            filename = 'histogram_default_name'
        filename = os.path.join('static', filename + '.png')
        plt.savefig(filename)
        print(f"Histogram successfully created at {filename}")

    def _command_generate_webpage(self):
        """Use ./data/<file> to generate a webpage according to a template.
        Concat the html list elements according to user sorting criteria."""
        movies = self._storage.list_movies()
        criteria = {
            0: 'unsorted',
            1: 'rating',
            2: 'year',
            3: 'alphabetically'
        }
        menu_len = len(criteria)
        print("How would you like the movies to be sorted on the webpage?")
        while True:
            usr_choice = Utility.get_user_num_choice(SORTING_MENU, menu_len)
            if usr_choice < 0:
                continue
            break
        if 1 <= usr_choice <= 2:
            movies = {k: v for k, v in sorted(
                movies.items(), key=lambda movie:
                movie[1][criteria[usr_choice]], reverse=True)
            }
        if usr_choice == 3:
            movies = {k: movies[k] for k in sorted(movies)}
        my_html_str = ''
        for k, v in movies.items():
            img_el = (f'<a href="{GOOGLE_PREFIX}{k} {v['year']}" '
                      f'target="_blank"><img class="movie-poster" '
                      f'src="{v['poster']}"/></a>')
            if v['notes']:  # only include title= attr when there are Notes
                img_el = (f'<a href="{GOOGLE_PREFIX}{k} {v['year']}" '
                          f'target="_blank"><img class="movie-poster" '
                          f'src="{v['poster']}" title="{v['notes']}"/></a>')
            my_html_str += (
                f'<li><div class="movie">{img_el}<div class="movie-rating">'
                f'{v['rating']}</div><div class="movie-title">'
                f'{k}</div><div class="movie-year">{v['year']}'
                '</div></div></li>'
            )
        with open(HTML_TEMPL, "r") as fd:
            html_template = fd.read()
        html_template = html_template.replace(TITLE_PLACEHOLDER, MY_TITLE)
        html_template = html_template.replace("style.css", CSS_PATH)
        updated_html = html_template.replace(GRID_PLACEHOLDER, my_html_str)
        if not os.path.exists(HTML_INDEX):
            fd = os.open(HTML_INDEX, os.O_CREAT)
            os.close(fd)
        with open(HTML_INDEX, "w") as fd:
            fd.write(updated_html)
        print("Website was generated successfully.")

    def _obtain_match_for_action(self, action: str):
        """Offer match candidates choice to user and ensure exact match.
        Used by commands delete_movie and update_movie."""
        # get query
        while True:
            query = input(f"{PROMPT_FOR_TITLE} {action}:\n> ").strip()
            if query:
                break
            print("Error: Movie title may not be an empty string.")
        # match query to DB entries
        candidates = self._fetch_lookup_matches(query)
        if not candidates:
            print("\nMovie not part of this database.")
            return ''
        print(f"\nThis is what I've found for <{query}>:")
        for i, mov in enumerate(candidates):
            k, v = next(iter(mov.items()))
            print(f"  {i + 1}. <{k}> ({v.get('year')})")
        # prompt user for candidate selection (insist on choice)
        while True:
            try:
                choice = int(input(f"{PROMPT_FOR_NUM} {action}:\n> "))
                if choice not in range(1, len(candidates) + 1):
                    print("Error: no movie under that number, try again.")
                    continue
                break
            except ValueError:
                print("Error: choice must be integer.")
        exact_title_str = list(candidates[choice - 1].keys())[0]
        return exact_title_str

    def _fetch_lookup_matches(self, query: str):
        """Parent function of (a) partial && exact match scenarios, and
        (b) fuzzy_search if none found in (a). Returns a list of dictionaries
        or empty list if no matches. MATCH_COEFFICIENT const mandates min
        query len for (a). I've chosen to focus on deletions and substitutions
        as parameters of editing distance, i.e. I partially disregard
        insertions in that I accept 'if query in key' as a match here, which
        foregoes looking for candidates in fuzzy_matching utility."""
        candidates = []
        if not query:
            return candidates
        movies = self._storage.list_movies()
        # (a) partial && exact match scenarios
        for i, (k, v) in enumerate(movies.items()):
            if (query.lower() in k.lower()
                    and len(query) > len(k) * MATCH_COEFFICIENT):
                candidates.append({k: v})
        # (b) fuzzy string matching worth a shot
        if not candidates:
            candidates = get_fuzzy_srch_candidates(query, movies)
        return candidates

    def run(self):
        """Initialize dispatcher table once at start of runtime. Until exit,
        print interface menu for user and dispatch appropriate functions."""
        func_dict = {0: self._command_exit_program,
                     1: self._command_list_movies,
                     2: self._command_add_movie,
                     3: self._command_delete_movie,
                     4: self._command_update_movie,
                     5: self._command_movie_stats,
                     6: self._command_random_movie,
                     7: self._command_search_movie,
                     8: self._command_movies_sorted_by_rating,
                     9: self._command_movies_sorted_by_year,
                     10: self._command_filter_movies,
                     11: self._command_create_ratings_histogram,
                     12: self._command_generate_webpage
                     }
        menu_len = len(func_dict)
        print(WELCOME_HEADER)
        while True:
            usr_choice = Utility.get_user_num_choice(MAIN_MENU, menu_len)
            if usr_choice < 0:
                continue
            print()
            func_dict[usr_choice]()
            Utility.hold_up_for_enter()
