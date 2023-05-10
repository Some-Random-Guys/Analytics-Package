import random
from wordcloud import WordCloud as wc
import matplotlib.pyplot as plt
import mplcyberpunk
from .helpers import most_used_words
from .DB import DB


async def wordcloud(db: DB, guild_id: int, user_id: int = None):
    messages: dict = await most_used_words(db=db, guild_id=guild_id, user_id=user_id or None, n=100)

    wordcloud = wc().generate_from_frequencies(messages)

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

    mplcyberpunk.add_glow_effects()

    # save image
    name = f"{random.randint(1, 100000000)}.png"
    try:
        plt.savefig(name, format='png')
    except Exception as e:
        print(e)

    return name


async def top_members(db: DB, guild_id: int, n: int = 5, type_: str = "messages"):
    if type_ == "messages":
        await db.cur.execute(
            f"""
                SELECT author_id, COUNT(author_id) AS count
                FROM `{guild_id}`
                GROUP BY author_id
                ORDER BY count DESC
                LIMIT {n};
            """
        )
        return db.cur.fetchall()

    if type_ == "words":
        pass #todo
