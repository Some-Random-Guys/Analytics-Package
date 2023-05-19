import random

from .DB import DB
import matplotlib.pyplot as plt
import mplcyberpunk


async def is_ignored(db: DB, channel_id: int = None, user_id: int = None):
    if channel_id is None and user_id is None:
        raise ValueError("channel_id and user_id cannot both be None")

    channel_ignored = False
    user_ignored = False

    # Ignore based on channel_id
    if channel_id is not None:
        db.cur.execute(
            f"""
                        SELECT * FROM `config` WHERE data1 = {channel_id} AND _key = 'channel_ignore'
                    """
        )
        res = db.cur.fetchone()
        try:
            channel_ignored = res[0] == channel_id
        except TypeError:
            channel_ignored = False

    # Ignore based on user_id
    if user_id is not None:
        db.cur.execute(
            f"""
                        SELECT data1 FROM `config` WHERE data1 = {user_id} AND _key = 'user_ignore';
                    """
        )
        # get the data1 and check if it is equal to user_id
        res = db.cur.fetchone()
        try:
            user_ignored = res[0] == user_id
        except TypeError:
            user_ignored = False

    if True in [channel_ignored, user_ignored]:
        return True


async def get_top_users(db: DB, guild_id: int, type_: str, amount: int = 10):
    # type_ can be either "messages" or "words" or "characters"

    if type_ == "messages":
        db.cur.execute(
            f"""
                SELECT author_id, COUNT(author_id) AS count
                FROM `{guild_id}` WHERE is_bot = 0
                GROUP BY author_id
                ORDER BY count DESC
                LIMIT {amount};
            """
        )
        return db.cur.fetchall()

    elif type_ == "words":
        pass  # todo

    elif type_ == "characters":
        pass    # todo


async def get_top_users_visual(db: DB, guild_id: int, client,  type_: str, amount: int = 10):
    res = await get_top_users(db=db, guild_id=guild_id, type_=type_, amount=amount)
    plt.style.use("cyberpunk")

    # get member object from id and get their nickname, if not found, use "Deleted User"
    labels = []
    for i in res:
        try:
            # get guild
            guild = client.get_guild(guild_id).get_member(i[0])
            # get member
            member = guild
            # get nickname
            labels.append(f"{member.nick or member.name} | {i[1]}")

        except Exception:
            labels.append("Unknown User")

    pie, texts, autotexts = plt.pie([value for _, value in res], labels=labels, autopct="%1.1f%%")

    for text in autotexts:
        text.set_color('black')

    for text in texts:
        text.set_color('white')

    plt.title(f"Top {amount} users by {type_}")

    mplcyberpunk.add_glow_effects()

    # save image
    name = f"{random.randint(1, 100000000)}.png"
    try:
        plt.savefig(name, format='png', dpi=600)
    except Exception as e:
        print(e)

    plt.close() # todo fix /UserWarning: Glyph 128017 (\N{SHEEP}) missing from current font.

    return name
