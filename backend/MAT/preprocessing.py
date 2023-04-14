import validators
from backend.MAT.helpers import remove_non_alpha, remove_stopwords


def all_valid_words(messages: list, stopwords=None) -> list[str]:
    """Given a list of messages, returns a list of all valid words, based on disocrd data."""
    valid_words = []
    for sentence in messages:
        # if it is empty
        if sentence.strip() == "":
            continue
        # if it is a codeblock
        elif sentence[0:3] == "```" or sentence[-3:] == '```':
            continue
        # if it is a link
        elif validators.url(sentence):
            continue

        # remove non alpha
        sentence = remove_non_alpha(sentence)

        # remove stopwords
        sentence = remove_stopwords(" ".join(
            sentence)) if stopwords is None else remove_stopwords(" ".join(sentence), stopwords)

        for word in sentence:
            # if it is a mention
            if sentence[0:2] == "<@":
                continue

            if len(word) <= 1:
                continue

            valid_words.append(word)
    return valid_words


def all_valid_characters(words: list) -> list[str]:
    return [char for word in words for char in word.split()]
