import time
from collections import Counter
from .DB import DB
import emoji
from .schemas import Profile


async def total_message_count(db: DB, guild_id: int, user_id: int) -> int:
    """Returns the total number of messages in a guild."""
    return await db.get_message_count(guild_id=guild_id, user_id=user_id)


async def top_words(db_or_msgs: DB | list[str], guild_id: int, user_id: int = None, amount: int = 5) -> dict[str:int]:
    """Returns the n most used words in a guild."""

    if isinstance(db_or_msgs, DB):
        message_content: list[str] = await db_or_msgs.get_message_content(guild_id, user_id or None)
    else:
        message_content = db_or_msgs

    if not message_content:
        return None

    all_messages = " ".join(message_content)
    word_counts = Counter(all_messages.split())

    return dict(word_counts.most_common(amount))


async def top_emoji(db_or_msgs: DB | list[str], guild_id: int, user_id: int = None, amount: int = 5) -> dict[str:int]:
    """Returns the n most used emojis in a guild."""
    if isinstance(db_or_msgs, DB):  # If a DB is passed, get the message content from the DB
        message_content: list[str] = await db_or_msgs.get_message_content(guild_id=guild_id, user_id=user_id or None)
    else:  # If a list of messages is passed, use that
        message_content = db_or_msgs

    if not message_content:
        return None

    all_messages = "".join(message_content)
    emoji_counts = list(Counter(all_messages.split()))

    emojis = []
    for block in emoji_counts:
        if emoji.is_emoji(block[0]):
            emojis.append(block)

    emojis = Counter(emojis)
    return dict(emojis.most_common(amount))


async def most_mentioned(db: DB, guild_id: int, user_id: int) -> int or None:
    """Returns the user which has been mentioned the most by the user, and the number of times mentioned."""
    mentions = await db.get_mentions(guild_id, user_id)

    # return the most mentioned user
    most_common = Counter(mentions).most_common(1)
    return most_common[0] if most_common else None


async def most_mentioned_by(db: DB, guild_id: int, user_id: int) -> int:
    """Returns the user who has mentioned the user the most, and the number of times mentioned."""
    mentions: list[int, list[int]] = await db.get_mentions_by(
        guild_id
    )  # of the form list[user_id, list[mentions]]

    # get a list of unique users
    users = set([user for user in mentions])

    # create a default dict with all the unique mentions[0] as key
    mentions_count = {user: 0 for user in users}

    # increment count if user_id is in the list of mentions
    for message in mentions:
        if user_id in message[1]:
            mentions_count[user_id] += 1

    # return the user, with the most mentioned value
    return Counter(mentions_count).most_common(1)[0]


async def get_word_count(db_or_msgs: DB | list[str], guild_id: int, user_id: int) -> int:
    """Returns the number of words in a guild."""
    if isinstance(db_or_msgs, DB):
        message_content: list[str] = await db_or_msgs.get_message_content(guild_id, user_id or None)
    else:
        message_content = db_or_msgs
    all_messages = " ".join(message_content)

    return len(all_messages.split())


async def get_character_count(db_or_msgs: DB | list[str], guild_id: int, user_id: int) -> int:
    """Returns the number of characters in a guild."""
    if isinstance(db_or_msgs, DB):
        message_content: list[str] = await db_or_msgs.get_message_content(guild_id, user_id or None)
    else:
        message_content = db_or_msgs

    # get the number of characters in each message
    all_messages = "".join(message_content).replace(" ", "")

    return len(all_messages)


async def build_profile(db: DB, guild_id: int, user_id: int) -> Profile:
    """Builds the profile for a certain user, in a certain guild."""
    start_time = time.time()

    profile = Profile()

    profile.user_id = user_id
    profile.guild_id = guild_id

    msg_list = await db.get_message_content(guild_id, user_id=user_id)

    profile.messages = await total_message_count(db, guild_id, user_id)
    profile.words = await get_word_count(msg_list, guild_id, user_id)
    profile.characters = await get_character_count(msg_list, guild_id, user_id)
    profile.average_msg_length = profile.characters / profile.messages # in chars

    profile.top_words = await top_words(msg_list, guild_id, user_id)
    # profile.top_emojis = await top_emoji(msg_list, guild_id, user_id)

    # most_mentioned_ = await most_mentioned(db, guild_id, user_id)
    # profile.total_mentions = len(most_mentioned_)

    # profile.most_mentioned = most_mentioned_[0]
    # profile.no_of_times_most_mentioned = most_mentioned_[1]

    # most_mentioned_by_ = await most_mentioned_by(db, guild_id, user_id)
    # profile.most_mentioned_by = most_mentioned_by_[0]
    # profile.no_of_times_most_mentioned_by = most_mentioned_by_[1]

    profile.time_taken = time.time() - start_time

    return profile
