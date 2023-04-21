import nltk
from nltk.stem import WordNetLemmatizer

try:
    BASIC_STOP_WORDS = set(nltk.corpus.stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    BASIC_STOP_WORDS = set(nltk.corpus.stopwords.words('english'))

# with open('./data/MAT/stopwords.txt') as f:
#     ADVANCED_STOP_WORDS = set(f.read().splitlines())

WNL = WordNetLemmatizer()


def remove_stopwords(text: str, stopwords=None) -> list[str]:
    """Given a returns a list of tokens with stopwords removed"""
    if stopwords is None:
        stopwords = BASIC_STOP_WORDS

    tokens = WNL.tokenize(text)
    return [token for token in tokens if token not in stopwords]


def remove_non_alpha(text: str) -> list[str]:
    """Given a returns a list of tokens with non-alphabetic characters removed"""
    return [token.lower() for token in text.split(" ") if token.isalpha()]
