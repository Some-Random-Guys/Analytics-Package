import random
from wordcloud import WordCloud as wc
import matplotlib.pyplot as plt
import mplcyberpunk

from .DB import DB
from .helpers import get_top_words


async def wordcloud(db: DB, guild_id: int, user_id: int = None, channel_id: int = None):
    top_words = await get_top_words(db=db, guild_id=guild_id, user_id=user_id, channel_id=channel_id, amount=100)
    # top_words = [(word, count), (word, count), ...]

    # create a wordcloud
    try:
        wordcloud = wc().generate_from_frequencies(dict(top_words))
    except ValueError:
        return None
    # apply glow effects
    mplcyberpunk.add_glow_effects()

    # Set DPI for higher resolution
    dpi = 300

    # plot the wordcloud
    plt.figure(figsize=(3840/dpi, 2160/dpi), dpi=dpi)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")

    # save image    # todo fix res still being low
    name = f"{random.randint(1, 100000000)}.png"
    try:
        plt.savefig(name, format='png', dpi=dpi)
    except Exception as e:
        print(e)

    plt.close()

    return name