"""All of the analysis functions, that return raw data, are defined here."""
from .DB import DB
from collections import Counter


async def total_messages(
    db: DB, guild_id: int, channel_id: int = None, user_id: int = None
) -> int:
    """Returns the total number of messages sent in(by) a (user) in a channel or guild."""
    if channel_id is not None:
        if user_id is not None:
            return db.get_user_message_count(guild_id, channel_id, user_id)
        else:
            return db.get_channel_message_count(guild_id, channel_id)

    if user_id is not None:
        return db.get_user_message_count(guild_id, user_id)

    return db.get_guild_message_count(guild_id)


async def most_used_words(
    db: DB, guild_id: int, user_id: int = None, n: int = 5
) -> dict[str:int]:
    """Returns the n most used words in a guild."""
    message_content: list[str] = await db.get_message_content(guild_id, user_id or None)

    if not message_content:
        return None

    all_messages = " ".join(message_content)
    word_counts = Counter(all_messages.split())

    return dict(word_counts.most_common(n))


async def most_mentioned(db: DB, guild_id: int, user_id: int) -> tuple[int, int]:
    """Returns the user which has been mentioned the most by the user, and the number of times mentioned."""
    mentions = db.get_mentions(guild_id, user_id)

    # return the most mentioned user
    return Counter(mentions).most_common(1)[0]
