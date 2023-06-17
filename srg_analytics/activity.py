import random
from .DB import DB
from matplotlib import pyplot as plt
import datetime
import mplcyberpunk
import time


async def activity_guild(db: DB, guild_id: int, time_period: int, timezone: datetime.timezone):
    messages = [i[0] for i in await db.get(guild_id, selected=["epoch"])]
    current_time = time.time()

    # timeperiod can be 1d, 5d, 1w, 2w, 1m, 3m, 6m, 9m, 1y, 2y, 3y, 5y, 5y, all

    messages = sorted(filter(lambda x: x >= current_time - float(86400 * time_period), messages))

    day = 86400
    interval_mapping = {
        7 * day: 7,  # 1 day for 7 days
        14 * day: 14,  # 1 day for 14 days
        21 * day: 7,  # 3 days for 21 days
        30 * day: 30,  # 1 day for 30 days
        60 * day: 2,  # 3 days for 60 days
        90 * day: 3,  # 3 days for 90 days
        180 * day: 6,  # 1 day for 180 days
        270 * day: 9,  # 1 day for 270 days
        365 * day: 12,  # 5 days for 365 days
        # Add more intervals as needed
    }

    interval = interval_mapping.get(time_period, 24)

    x = (messages[-1] - messages[0]) // interval

    key_points = [messages[0] + x * (i + 1) for i in range(interval)]

    final_output = {k: 0 for k in key_points}

    def categorize_epoch(epoch):
        for point in key_points:
            if epoch <= point:
                return point

        return key_points[-1]

    for epoch in messages:
        final_output[categorize_epoch(epoch)] += 1

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

    match time_period:
        case 1:
            # convert the list of raw_data, i[0] is epoch, find the hour it is in with time_zone

            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract hours from datetime objects and format them
            x = [dt.strftime('%I%p') for dt, _ in datetime_data]

            plt.xlabel('Hour')

            plt.title('Message Count by Hour')
            plt.xticks(rotation=45)

        case 3:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract days from datetime objects and format them
            x = [dt.strftime('%a') for dt, _ in datetime_data]

            plt.xlabel('Day')

            plt.title('Message Count by Day')
            plt.xticks(rotation=45)

        case 7:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract days from datetime objects and format them
            x = [dt.strftime('%d') for dt, _ in datetime_data]

            plt.xlabel('Day')

            plt.title('Message Count by Day')
            plt.xticks(rotation=45)

        case 14:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract days from datetime objects and format them
            x = [dt.strftime('%d') for dt, _ in datetime_data]

            plt.xlabel('Day')

            plt.title('Message Count by Day')
            plt.xticks(rotation=45)

        case 30:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract dates from datetime objects and format them
            x = [dt.strftime('%d') for dt, _ in datetime_data]

            plt.xlabel('Day')

            plt.title('Message Count by Day')
            plt.xticks(rotation=45)

        case 60:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract months from datetime objects and format them
            x = [dt.strftime('%b') for dt, _ in datetime_data]

            plt.xlabel('Month')

            plt.title('Message Count by Month')
            plt.xticks(rotation=45)

        case 90:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract months from datetime objects and format them
            x = [dt.strftime('%b') for dt, _ in datetime_data]

            plt.xlabel('Month')

            plt.title('Message Count by Month')
            plt.xticks(rotation=45)

        case 180:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract months from datetime objects and format them
            x = [dt.strftime('%b') for dt, _ in datetime_data]

            plt.xlabel('Month')

            plt.title('Message Count by Month')
            plt.xticks(rotation=45)

        case 270:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract months from datetime objects and format them
            x = [dt.strftime('%b') for dt, _ in datetime_data]

            plt.xlabel('Month')

            plt.title('Message Count by Month')
            plt.xticks(rotation=45)

        case 365:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract months from datetime objects and format them
            x = [dt.strftime('%b') for dt, _ in datetime_data]

            plt.xlabel('Month')

            plt.title('Message Count by Month')
            plt.xticks(rotation=45)

        case _:
            # Convert epoch times to datetime objects
            datetime_data = [(datetime.datetime.fromtimestamp(epoch, time_zone), count) for epoch, count in
                             raw_data]

            # Extract months from datetime objects and format them
            x = [dt.strftime('%b') for dt, _ in datetime_data]

    y = [count for _, count in raw_data]
    plt.plot(x, y)

    plt.title(f"Guild {guild_id} activity by hour")
    plt.ylabel('Message Count')
    plt.grid(True)

    # apply glow effects
    mplcyberpunk.make_lines_glow()
    mplcyberpunk.add_gradient_fill(alpha_gradientglow=0.5)

    name = random.randint(1, 100000000)
    plt.savefig(f"{name}.png", format='png', dpi=400, bbox_inches="tight")
    plt.close()

    return f"{name}.png"
