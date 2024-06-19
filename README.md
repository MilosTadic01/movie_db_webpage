# movie_db_webpage
Welcome to my project page!
## Introduction
This is an exercise in creating a command line user interface for movie database management and for generating webpages based on the data.

### Tags
`html` `css` `python` `api` `oop` `json` `csv` `fuzz`

### Project features
* webpage generation
* histogram generation
* API data fetching
* an implementation of fuzzy string matching


## Installation

To install this project, clone the repository and install the dependencies listed in requirements.txt. If on Windows, rely on `pip` rather than pip3.

```bash
  pip3 install -r requirements.txt
```

Furthermore, you'll need to register on [themoviedb.org](https://www.themoviedb.org/signup) in order to obtain an API key. Thereafter replace *your_api_key* in the following command to end up with a command containing something looking like `API_KEY='bb48af1shq2i1l'` and run the shell command:

```bash
  echo API_KEY='your_api_key' > .env
```

## Usage/Examples

The program relies on a command line argument specifying either a new or an existing DB filename. For existing files, it assumes json-like file contents for .json and csv-like file contents for .csv extensions. If no extension is specified, the program will assume .json extension. Program execution:

```bash
python3 main.py data.csv
```

Runtime printout:

```bash
********** My Movies Database **********

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

Enter choice (0-12):
> 
```

## Feedback

If you have any feedback, please reach out to me @MilosTadic01


## License

[CC0 1.0 Universal](https://choosealicense.com/licenses/cc0-1.0/)


