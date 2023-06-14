import random

from .DB import DB
import time
from matplotlib import pyplot as plt
import datetime
import mplcyberpunk


# M = 168
# values = {365: [f'{i}' for i in range(1, 13)], 365 * 2: [f'{i}' for i in range(1, 25)]}

# todo split this function into 2 different functions, one for server and one for user
import time


async def activity_guild(db: DB, guild_id: int, time_period: int):
    messages = [i[0] for i in await db.get(guild_id, selected=["epoch"])]
    current_time = time.time()

    messages = sorted(filter(lambda x: x >= current_time - float(86400 * time_period), messages))

    day = 86400
    interval_mapping = {
        14*day: 14,  # 1 day for 14 days
        21*day: 7,  # 3 days for 21 days
        30*day: 30,  # 1 day for 30 days
        60*day: 20,  # 3 days for 60 days
        90*day: 30,  # 3 days for 90 days
        180*day: 180,  # 1 day for 180 days
        270*day: 270,  # 1 day for 270 days
        365*day: 73,  # 5 days for 365 days
        # Add more intervals as needed
    }

    interval = interval_mapping.get(time_period, 24)

    x = (messages[-1] - messages[0]) // interval

    key_points = [messages[0] + x * (i + 1) for i in range(interval)]
    print(key_points)
    
    final_output = {k: 0 for k in key_points}

    def categorize_epoch(epoch):
        for point in key_points:
            if epoch <= point:
                return point

        return key_points[-1]

    for epoch in messages:
        final_output[categorize_epoch(epoch)] += 1

    print(list(final_output.items()))
    return list(final_output.items())


async def activity_user(guild_id: int, time_period: str):
    pass


async def activity_guild_visual(db: DB, guild_id: int, time_period: int, time_zone: datetime.timezone = None):
    raw_data = await activity_guild(db, guild_id, time_period)
    plt.style.use("cyberpunk")

    # output format - [(epoch, message_count), ...]

    print(raw_data)

    if time_zone is None:
        # set timezone to GMT+3 (Moscow)
        time_zone = datetime.timezone(datetime.timedelta(hours=3))

    if time_period == 1:
        # convert the list of raw_data, i[0] is epoch, find the hour it is in with time_zone

        # Convert epoch times to datetime objects
        datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                         raw_data]

        # Extract hours from datetime objects and format them
        x = [dt.strftime('%I%p') for dt, _ in datetime_data]

        plt.xlabel('Hour')

        plt.title('Message Count by Hour')
        plt.xticks(rotation=45)

    y = [count for _, count in raw_data]
    plt.plot(x, y)

    plt.title(f"Guild {guild_id} activity by hour")
    plt.ylabel('Message Count')
    plt.grid(True)

    # apply glow effects
    mplcyberpunk.make_lines_glow()
    mplcyberpunk.add_gradient_fill(alpha_gradientglow=0.5)

    name = random.randint(1, 100000000)
    plt.savefig(f"{name}.png", format='png', dpi=400)
    plt.close()

    return f"{name}.png"













