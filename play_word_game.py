from string import ascii_lowercase
from matching import MatchReport

"""
This script partially automates playing a popular (as of Jan, 2022) online word game.
In the game, the player tries to guess a five-letter secret word. Each guess may (or may not) reveal some information
about which letters appear in the secret word, and in which position(s).
"""


def play_game():
    candidates = get_all_five_letter_words()
    guesses = 0
    match_report = MatchReport()
    while True:
        print("There are {} possible words remaining.".format(len(candidates)))
        if len(candidates) == 0:
            # The secret word is not in the dictionary!
            print("No remaining words left!")
            break
        elif len(candidates) == 1:
            print("The solution must be {}. Done in {} guesses".format(candidates[0], guesses + 1))
            break
        elif len(candidates) <= 10:
            print("They are: {}".format(",".join(candidates)))

        next_guess = generate_next_guess(candidates, match_report)
        print("The next guess should be {}".format(next_guess))
        guesses += 1

        results = get_results_from_user(next_guess)
        if sum(1 for letter in results if letter == 'g') == 5:
            print("Done in {} guesses".format(guesses))
            break
        match_report = MatchReport(next_guess, results)
        candidates = narrow_word_list(candidates, match_report)


def get_all_five_letter_words():
    with open('word-list.txt') as file:
        return [s for s in file.read().splitlines() if len(s) == 5]


def generate_next_guess(candidates, match_report):
    letter_probabilities = get_letter_probabilities(candidates, match_report)
    best_score = 0
    best_word = None
    for word in candidates:
        word_letters = set(word)
        letter_scores = [letter_probabilities[letter] for letter in word_letters]
        word_score = sum(letter_scores)
        if not best_word or word_score > best_score:
            best_score = word_score
            best_word = word
    return best_word


_instructions_given = False


def get_results_from_user(last_word):
    # This will crash if the user gives bad input.  That's fine.
    global _instructions_given
    if not _instructions_given:
        print("Please enter the results given, as a five-character string.")
        print("Use a 'g' to represent a green square, 'y' for a yellow, and '_' (underscore) for non-matching.")
        _instructions_given = True

    user_input = input("Enter results for {}:".format(last_word))
    assert sum([1 for letter in user_input if letter in ['g', 'y', '_']]) == 5
    assert len(user_input) == 5
    return user_input


def narrow_word_list(candidates, match_report):
    # It's probably possible to be smarter about regexes here to do this search more efficiently. However, the code
    # would be harder to understand, and efficiency isn't very important here anyhow.

    # It's probably also possible to be smarter about how we pick the next guess. Perhaps we could guess at the
    # "expected entropy reduction" of each possible guess, and then use the one with the best rank. But, that's way too
    # much work for a word game fad that'll probably disappear in a few weeks.

    # Step 1: Only include words that fit with our known exact matches.
    exact_match_spec = get_relevant_letters_per_position(match_report.exact)
    candidates = [word for word in candidates if word_contains_exact_matches(word, exact_match_spec)]

    # Step 2: Only include words that fit with our known partial matches.
    partial_match_spec = get_relevant_letters_per_position(match_report.partial)
    candidates = [word for word in candidates if word_contains_partial_matches(word, partial_match_spec)]

    # Step 3: Only include words that do not contain any known nonmatching letters.
    for letter in match_report.nonmatch:
        candidates = [word for word in candidates if letter not in word]

    return candidates


def get_letter_probabilities(word_list, match_report):
    # Returns a "score" for each remaining guessable letter. The highest scores are for letters that are in the highest
    # number of words in the list.
    probs = {}
    stripped_word_list = [strip_matches_from_word(word, match_report) for word in word_list]
    word_count = len(stripped_word_list)
    letters_to_check = [letter for letter in ascii_lowercase if letter not in match_report.nonmatch]
    for letter in letters_to_check:
        letter_count = 0
        for word in word_list:
            letter_count += sum([1 for wl in word if wl == letter])
        probs[letter] = letter_count / word_count
    return probs


def get_relevant_letters_per_position(matches):
    # Incoming argument is a map from letter to relevant positions
    # Return value is a 5-element list, with each element being a list of letters relevant to that position
    position_letters = [[], [], [], [], []]
    for match in matches:
        letter = match
        positions = matches[letter]
        for position in positions:
            position_letters[position] = [letter]
    return position_letters


def strip_matches_from_word(word, match_report):
    stripped_word = str(word)
    letters_to_strip = get_letters_in_report(match_report)
    for letter in letters_to_strip:
        stripped_word.replace(letter, "", 1)
    return stripped_word


def get_letters_in_report(match_report):
    def get_letters_in_subreport(subreport):
        letters = []
        for letter in subreport:
            for i in range(len(subreport[letter])):
                letters.append(letter)
        return letters

    report_letters = get_letters_in_subreport(match_report.exact)
    report_letters += get_letters_in_subreport(match_report.partial)
    return report_letters


def word_contains_exact_matches(word, exact_matches_by_location):
    for i in range(5):
        if exact_matches_by_location[i]:
            assert len(exact_matches_by_location[i]) == 1
            letter_to_match = exact_matches_by_location[i][0]
            if word[i] != letter_to_match:
                return False
    return True


def word_contains_partial_matches(word, partial_matches_by_location):
    # First, the word must NOT match the given letters at the given positions:
    for i in range(5):
        if partial_matches_by_location[i]:
            for letter_to_match in partial_matches_by_location[i]:
                if word[i] == letter_to_match:
                    return False

    # Second, the word must match all of the given letters at some position:
    letters = set()
    for letter_list in partial_matches_by_location:
        for letter in letter_list:
            letters.add(letter)
    for letter in letters:
        if letter not in word:
            return False

    return True


if __name__ == "__main__":
    play_game()
