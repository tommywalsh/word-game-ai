
# Summarizes the match-related information we have about a word.
# Fields are:
#    exact: A dictionary that gives information about letters for which we know the exact location
#         This maps each letter to a list of indices of where the letter is known to appear in the word
#    partial: A dictionary that gives information about letters that are in the word, but not at a known location
#         This maps each letter to a list of indices of where the letter is known *NOT* to appear in the word
#    nonmatch: A list of letters that are known to not appear anywhere in the word
class MatchReport:
    def __init__(self, word=None, results=None):
        self.word = word
        if results:
            self.exact, self.partial, self.nonmatch = _get_subreports(word, results)
        else:
            self.exact = {}
            self.partial = {}
            self.nonmatch = []


# Helper function to generate a map from letter to word location (index).
def _generate_subreport_given_indices(word, matching_indices):
    report = {}
    for index in matching_indices:
        letter = word[index]
        if letter in report:
            report[letter].append(index)
        else:
            report[letter] = [index]
    return report


# Helper function to generate each of the three "subreports" (exact match, partial match, no match)
def _get_subreports(word, results):
    exact_indices = []
    partial_indices = []
    nonmatch_indices = []
    for index in range(5):
        result = results[index]
        if result == 'g':
            exact_indices.append(index)
        elif result == 'y':
            partial_indices.append(index)
        else:
            nonmatch_indices.append(index)

    exact_report = _generate_subreport_given_indices(word, exact_indices)
    partial_report = _generate_subreport_given_indices(word, partial_indices)

    # A "grey" square only indicates a nonmatching letter if that same letter isn't already a partial or exact match.
    nonmatching_letters = []
    for index in nonmatch_indices:
        letter = word[index]
        if letter not in exact_report and letter not in partial_report:
            nonmatching_letters.append(letter)

    return exact_report, partial_report, set(nonmatching_letters)
