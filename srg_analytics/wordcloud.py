import random
import time

from wordcloud import WordCloud as wc
import matplotlib.pyplot as plt
import mplcyberpunk

from .DB import DB
from .helpers import get_top_words


async def wordcloud(db: DB, guild_id: int, user_id: int = None, channel_id: int = None):
    top_words = await get_top_words(db=db, guild_id=guild_id, user_id=user_id, channel_id=channel_id, amount=100)
    # top_words = [(word, count), (word, count), ...]

    dpi = 300

    # create a wordcloud
    try:
        wordcloud = wc(width=1920, height=1080).generate_from_frequencies(dict(top_words))
    except ValueError:
        return None
    # apply glow effects
    mplcyberpunk.add_glow_effects()

    # plot the wordcloud
    plt.figure(figsize=(20, 10), dpi=dpi)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")

    # save image    # todo fix res still being low
    name = f"{random.randint(1, 100000000)}.png"
    try:
        plt.savefig(name, format='png', dpi=dpi, facecolor='k', bbox_inches='tight')
    except Exception as e:
        print(e)
        return None

    plt.close()

    return name