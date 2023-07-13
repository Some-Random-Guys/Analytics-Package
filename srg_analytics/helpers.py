import collections

import nltk

from .DB import DB
from collections import Counter
import validators


async def is_ignored(db: DB, channel_id: int = None, user_id: int = None):
    if channel_id is None and user_id is None:
        raise ValueError("channel_id and user_id cannot both be None")

    channel_ignored = False
    user_ignored = False

    # Ignore based on channel_id
    if channel_id is not None:
        res = await db.execute(
            f"""
                        SELECT * FROM `config` WHERE data1 = {channel_id} AND _key = 'channel_ignore'
                    """, fetch="one"
        )
        try:
            channel_ignored = res[0] == channel_id
        except TypeError:
            channel_ignored = False

    # Ignore based on user_id
    if user_id is not None:
        res = await db.execute(
            f"""
                        SELECT data1 FROM `config` WHERE data1 = {user_id} AND _key = 'user_ignore';
                    """, fetch="one"
        )

        # get the data1 and check if it is equal to user_id
        try:
            user_ignored = res[0] == user_id
        except TypeError:
            user_ignored = False

    if True in [channel_ignored, user_ignored]:
        return True


def get_words_from_user(db_or_msgs: DB | list, guild_id: int = None, user_id: int = None):
    if isinstance(db_or_msgs, DB):
        # message_content: list[str] = await db_or_msgs.get_message_content(guild_id, user_id or None)
        pass # todo
    else:
        message_content = db_or_msgs

    if not message_content:
        return None

    all_messages = " ".join(message_content)
    words = nltk.word_tokenize(all_messages)

    # remove stopwords
    stopwords = nltk.corpus.stopwords.words("english")
    words = [word for word in words if word not in stopwords]

    return words


async def get_top_users_by_words(db: DB, guild_id: int, channel_id: int = None, amount: int = 10, start_epoch: int = None, count_others = True):

    query = f"""
            SELECT author_id, message_content
            FROM `{guild_id}` WHERE is_bot = 0 AND message_content != ''
            """

    if channel_id is not None:
        query += f"AND channel_id = {channel_id}"

    if start_epoch is not None:
        query += f"AND epoch >= {start_epoch}"

    res = await db.execute(query, fetch="all")

    # Count words for each user
    word_counts = Counter()
    for author_id, message in res:
        words = message.split()
        word_counts[author_id] += len(words)

    # Get the top users and their word counts
    # noinspection PyTypeChecker
    top_users: list[tuple[int, int]] = word_counts.most_common()

    if count_others:
        return [*top_users[:amount], ('others', sum([i[1] for i in top_users[amount:]]))]
    else:
        return top_users[:amount]


async def get_top_channels_by_words(db: DB, guild_id: int, amount: int = 10):
    res = await db.execute(
        f"""
            SELECT channel_id, message_content
            FROM `{guild_id}` WHERE is_bot = 0 AND message_content != ''
        """, fetch="all"
    )

    # Count words for each user
    word_counts = Counter()
    for _channel_id, message in res:
        words = message.split()
        word_counts[_channel_id] += len(words)

    # Get the top users and their word counts
    top_channels = word_counts.most_common()

    return top_channels[:amount]


async def process_messages(messages):
    """Returns a list of all valid words when given a list of messages from the database."""
    # all words from data
    words = []

    try:
        stop_words = nltk.corpus.stopwords.words("english")
    except LookupError:
        nltk.download("stopwords")
        stop_words = nltk.corpus.stopwords.words("english")

    for sentence in messages:
        sentence = sentence.decode("utf-8")

        # if it is empty
        if sentence.strip() == "":
            continue
        # if it is a codeblock
        elif sentence[0:3] == "```" or sentence[-3:] == '```':
            continue
        # if it is a link
        elif validators.url(str(sentence)):
            continue

        try:
            tokens = nltk.tokenize.word_tokenize(sentence)
        except LookupError:
            nltk.download("punkt")
            tokens = nltk.tokenize.word_tokenize(sentence)

        sentence = [w for w in tokens if w not in stop_words]

        # remove non alpha
        # sentence = remove_non_alpha(sentence)

        for word in sentence:
            # if it is a mention
            # if sentence[0:2] == "<@":
            #     continue

            if len(word) <= 1:
                continue

            words.append(word)

    return words


async def get_top_words(db: DB, guild_id: int, user_id: int = None, channel_id: int = None, amount: int = 10):
    if user_id is not None:
        res = await db.execute(
            f"""
                        SELECT message_content
                        FROM `{guild_id}` WHERE author_id = {user_id}
                        AND is_bot = 0 AND message_content != ''
                    """, fetch="all"
        )
    elif channel_id is not None:
        res = await db.execute(
            f"""
                        SELECT message_content
                        FROM `{guild_id}` WHERE channel_id = {channel_id}
                        AND is_bot = 0 AND message_content != ''
                    """, fetch="all"
        )
    elif user_id is not None and channel_id is not None:
        res = await db.execute(
            f"""
                        SELECT message_content
                        FROM `{guild_id}` WHERE author_id = {user_id} AND channel_id = {channel_id}
                        AND is_bot = 0 AND message_content != ''
                    """, fetch="all"
        )
    else:
        res = await db.execute(
            f"""
                        SELECT message_content
                        FROM `{guild_id}` WHERE is_bot = 0 AND message_content != ''
                    """, fetch="all"
        )

    res = [x[0] for x in res]

    words = await process_messages(res)

    # words is a list of all words ever sent, make a list of the top words and their counts
    counts = collections.Counter(words)
    top_words = counts.most_common(amount)

    # return the top words with their counts
    return top_words  # [(word, count), (word, count), ...]
