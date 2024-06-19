"""This implementation of fuzzy string matching is intended to catch typos
And inform user 'did you mean...' and printout match candidate DB entries.

Settings Instructions:
If you want 'bbbbbbb' to suggest 'Titanic', ramp up ED_TOLERANCE_COEFF to
1.1. Note that this will include any movies len(movies) < len(query) * 1.
CHUNK_SZ is inspired by how Google search seems to work and should not be
lower than 3, the code doesn't protect against idx out-of-bounds.
If you want query 'a' to suggest 'Titanic', add MATCH_LEN_COEFF and set to 0,
then all the way down replace 'len(query) > CHUNK_SZ' with
'len(query) > len(movie) * MATCH_LEN_COEFF'. Adjust it 0.0 - 1.0 at will.
Examples with current settings:
tit     -> no such movie (designated too short to consider)
tita    -> Did you mean Titanic? (not suggesting 'Aladdin')
tatt    -> Did you mean Titanic? (not suggesting 'Aladdin')
tunnc   -> Did you mean Titanic? (not suggesting 'Aladdin')
iabic   -> Did you mean Titanic? (not suggesting 'Aladdin')
"""

import string

ED_TOLERANCE_COEFF = 0.50
LEN_TOLERANCE_COEFF = 1.40
START_IDX = 0
CHUNK_SZ = 3
RETAIN_ED = 0
INCREASE_ED = 1


def get_comparison_basis(query: str, movie: str):
    """Return a higher indexed movie string that qualifies for fuzzy matching.
    If none found, return the original string so that fuzzy matching will try,
    fail and say 'no such entry' in database. """
    for i in range(len(movie)):
        if CHUNK_SZ > len(movie[i:]):  # reaching the upper bound of movie
            return movie  # bail
        if (two_out_of_three_are_present_and_ordered(query, movie[i:]) and
                movie[i] not in string.whitespace):
            return movie[i:]  # return the slice fit for comparison


def two_out_of_three_are_present_and_ordered(query: str, movie: str):
    """My recursion logic relies on 66% being present and in proper indexed
    order. Even Google doesn't recognize 'dgXfather' as 'godfather', I need
    at least 'Xgofather' :) """
    upper_bound = 1
    query = query.lower()
    movie = movie.lower()
    for i in range(CHUNK_SZ):  # compare query idx 0 1, 1 2, 0 2 against movie
        if (query[i % 2] in movie[:CHUNK_SZ] and
                query[upper_bound] in movie[:CHUNK_SZ] and
                movie.index(query[i % 2]) < movie.index(query[upper_bound])):
            return True
        upper_bound = 2
    return False


def is_unlikely_match_at_zero_idx(query: str, movie: str):
    """See if 66% among query[0], query[1] query[2] are present >in order<
    in movie[:3]. If so, ret False. Else ret True, i.e. unlikely match. I'm
    aware of the 'magic number' presence, but I hope that the docstring is
    compensating"""
    query = query.lower()
    movie = movie.lower()
    if len(query) < CHUNK_SZ or len(movie) < CHUNK_SZ:
        return False
    query_chars_present = 0
    exact_matches = 0
    for i in range(CHUNK_SZ):
        if query[i] in movie[:CHUNK_SZ]:
            query_chars_present += 1
        if query[i] == movie[i]:
            exact_matches += 1
    if query_chars_present < 2:
        return True
    if exact_matches > 1:
        return False
    # at this point we know we have 66% present but are they in proper order
    return not two_out_of_three_are_present_and_ordered(query, movie)
    # if funct above rets True, ret not True, bc False + 'unlikely == 'likely'


def calc_ed(query: str, i: int, movie: str, j: int):
    """Calculate editing distance. I'm merely counting the edit candidates as
    I spot them, not performing any. Code comment: in this particular case, I
    believe the big 'else' block to be improving readability, so I'm choosing
    not to 'return' right before it if the condition was met, but rather
    letting the eye fall down to a singular 'return edits'. Recursion == hard
    """
    edits = 0
    query = query.lower()
    movie = movie.lower()
    if i == len(query) or j == len(movie):
        return RETAIN_ED  # base case 1, idx would go out of bounds
    if query[i] == movie[j]:
        edits += calc_ed(query, i + 1, movie, j + 1)
    else:
        if i + 1 == len(query) or j + 1 == len(movie):
            return INCREASE_ED  # base case 2, idx + 1 would go out of bounds
        elif query[i] == movie[j + 1]:  # insertion candidate
            edits += 1
            edits += calc_ed(query, i, movie, j + 1)
        elif query[i + 1] == movie[j]:  # deletion candidate
            edits += 1
            edits += calc_ed(query, i + 1, movie, j)
        elif query[i + 1] == movie[j + 1]:  # substitution candidate
            edits += 1
            edits += calc_ed(query, i + 1, movie, j + 1)
        else:  # move on to the next
            edits += 1
            edits += calc_ed(query, i + 1, movie, j + 1)
    return edits


def get_fuzzy_srch_candidates(query: str, movies: dict):
    """Return list of dicts which have qualified as candidates"""
    candidates = []
    for k, v in movies.items():
        mov_str_cp = k
        if is_unlikely_match_at_zero_idx(query, k):
            mov_str_cp = get_comparison_basis(query, k)
        editing_distance = calc_ed(query, START_IDX, mov_str_cp, START_IDX)
        if (CHUNK_SZ < len(query) <= len(mov_str_cp) * LEN_TOLERANCE_COEFF and
                editing_distance < len(query) * ED_TOLERANCE_COEFF):
            candidates.append({k: v})
    return candidates
