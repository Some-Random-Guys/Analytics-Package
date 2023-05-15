from .DB import DB
from collections import Counter


async def most_used_words(db: DB, guild_id: int, user_id: int = None, amount: int = 5) -> dict[str:int]:
    """Returns the n most used words in a guild."""
    message_content: list[str] = await db.get_message_content(guild_id, user_id or None)

    if not message_content:
        return None

    all_messages = " ".join(message_content)
    word_counts = Counter(all_messages.split())

    return dict(word_counts.most_common(amount))


async def most_mentioned(db: DB, guild_id: int, user_id: int) -> tuple[int, int]:
    """Returns the user which has been mentioned the most by the user, and the number of times mentioned."""
    mentions = db.get_mentions(guild_id, user_id)

    # return the most mentioned user
    return Counter(mentions).most_common(1)[0]  # todo add check for empty list
