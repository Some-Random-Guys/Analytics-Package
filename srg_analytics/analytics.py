from .DB import DB
from .profile import Profile
from collections import Counter
from typing import DefaultDict


async def total_message_count(db: DB, guild_id: int, user_id: int):
    """Returns the total number of messages in a guild."""
    return await db.get_message_count(guild_id, user_id)


async def most_used_words(
    db: DB, guild_id: int, user_id: int = None, amount: int = 5
) -> dict[str:int]:
    """Returns the n most used words in a guild."""
    message_content: list[str] = await db.get_message_content(guild_id, user_id or None)

    if not message_content:
        return None

    all_messages = " ".join(message_content)
    word_counts = Counter(all_messages.split())

    return dict(word_counts.most_common(amount))


async def total_mentions(db: DB, guild_id: int, user_id: int) -> int:
    """Returns the total number of mentions in a guild."""
    return len(await db.get_mentions(guild_id, user_id))


async def most_mentioned(db: DB, guild_id: int, user_id: int) -> int:
    """Returns the user which has been mentioned the most by the user, and the number of times mentioned."""
    mentions = db.get_mentions(guild_id, user_id)

    # return the most mentioned user
    return Counter(mentions).most_common(1)[0]  # todo add check for empty list


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

    most_mentioned_ = most_mentioned(db, guild_id, user_id)
    most_mentioned_by_ = most_mentioned_by(db, guild_id, user_id)

    profile = Profile(
        guild_id=guild_id,
        id_=user_id,
        no_of_messages=total_message_count(db, guild_id, user_id),
        top_5_words=most_used_words(db, guild_id, user_id),
        net_polarity=0,
        most_mentioned_channels=None,
        most_mentioned_person_id=most_mentioned_[0],
        total_times_mentioned=most_mentioned_[1],
        most_mentioned_by_id=most_mentioned_by_[0],
        most_mentioned_by_id_no=most_mentioned_by_[1],
        active_channel=None,
    )
