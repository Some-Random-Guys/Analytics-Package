import emoji
from collections import Counter

from .DB import DB
from .profile import Profile


async def total_message_count(db: DB, guild_id: int, user_id: int):
    """Returns the total number of messages in a guild."""
    return await db.get_message_count(guild_id, user_id)


async def most_used_words(
    db: DB, guild_id: int, user_id: int = None, amount: int = 5
) -> dict[str:int]:
    """Returns the n most used words in a guild."""
    message_content: list[str] = await db.get_message_content(guild_id, user_id or None)
    print(message_content)

    if not message_content:
        return None

    all_messages = " ".join(message_content)
    word_counts = Counter(all_messages.split())

    return dict(word_counts.most_common(amount))


async def most_used_emojis(
    db: DB, guild_id: int, user_id: int = None, amount: int = 5
) -> dict[str:int]:
    """Returns the n most used emojis in a guild."""
    message_content: list[bytes] = await db.get_message_content(
        guild_id, user_id or None
    )
    print(message_content)

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


async def total_mentions(db: DB, guild_id: int, user_id: int) -> int:
    """Returns the total number of mentions in a guild."""
    return len(await db.get_mentions(guild_id, user_id))


async def most_mentioned(db: DB, guild_id: int, user_id: int) -> int or None:
    """Returns the user which has been mentioned the most by the user, and the number of times mentioned."""
    mentions = db.get_mentions(guild_id, user_id)

    # return the most mentioned user
    most_common = Counter(mentions).most_common(1)
    return most_common[0] if most_common else None


async def most_mentioned_by(db: DB, guild_id: int, user_id: int) -> int:
    """Returns the user who has mentioned the user the most, and the number of times mentioned."""
    mentions: list[int, list[int]] = await db.get_mentions_by(
        guild_id
    )  # of the form list[user_id, list[mentions]]

    # get a list of unique users
    users = set([user[0] for user in mentions])

    # create a default dict with all the unique mentions[0] as key
    mentions_count = {user: 0 for user in users}

    # increment count if user_id is in the list of mentions
    for message in mentions:
        if user_id in message[1]:
            mentions_count[user_id] += 1

    # return the user, with the most mentioned value
    return Counter(mentions_count).most_common(1)[0]


async def build_profile(db: DB, guild_id: int, user_id: int) -> Profile:
    """Builds the profile for a certian user, in a certian guild."""
    profile = Profile()

    profile.user_id = user_id
    profile.guild_id = guild_id

    profile.messages = await total_message_count(db, guild_id, user_id)
    profile.top_words = await most_used_words(db, guild_id, user_id)
    profile.top_emojis = await most_used_emojis(db, guild_id, user_id)

    profile.total_mentions = await total_mentions(db, guild_id, user_id)

    most_mentioned_ = await most_mentioned(db, guild_id, user_id)
    profile.most_mentioned = most_mentioned_[0]
    profile.no_of_times_most_mentioned = most_mentioned_[1]

    most_mentioned_by_ = await most_mentioned_by(db, guild_id, user_id)
    profile.most_mentioned_by = most_mentioned_by_[0]
    profile.no_of_times_most_mentioned_by = most_mentioned_by_[1]
