from .DB import DB
from collections import Counter


async def most_used_words(db: DB, guild_id: int, user_id: int = None, n: int = 5):
    message_content: list[str] = await db.get_message_content(guild_id, user_id or None)

    if not message_content:
        return None

    all_messages = " ".join(message_content)
    word_counts = Counter(all_messages.split())

    return word_counts.most_common(n)
