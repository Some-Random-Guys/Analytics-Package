import io
import random

from wordcloud import WordCloud as wc
import matplotlib.pyplot as plt
import mplcyberpunk
from helpers import most_used_words
from DB import DB


async def wordcloud_user(db: DB, guild_id: int, user_id: int):
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


async def wordcloud_server(guild_id):
    messages: dict = {}  # todo: get messages from database

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
