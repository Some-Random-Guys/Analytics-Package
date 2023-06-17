import random
from .DB import DB
from matplotlib import pyplot as plt
import datetime
import mplcyberpunk
import time
from collections import Counter

import datetime


async def activity_guild(db, guild_id, time_period):
    timezone = datetime.timezone(datetime.timedelta(hours=3))
    # Calculate the start and end times based on the provided time_period
    now = datetime.datetime.now(timezone)
    if time_period == '1d':
        # starttime is epoch of start of today
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        label_format = '%H:%M'  # Format for x-axis labels
        interval = datetime.timedelta(hours=1)  # Interval for grouping messages
    elif time_period == '5d':
        # starttime is epoch of start of 4 days ago
        start_time = now - datetime.timedelta(days=4)
        label_format = '%m-%d'  # Format for x-axis labels
        interval = datetime.timedelta(days=1)  # Interval for grouping messages
    elif time_period == '1w':
        start_time = now - datetime.timedelta(weeks=1)
        label_format = '%m-%d'  # Format for x-axis labels
        interval = datetime.timedelta(days=1)  # Interval for grouping messages
    elif time_period == '2w':
        start_time = now - datetime.timedelta(weeks=2)
        label_format = '%m-%d'  # Format for x-axis labels
        interval = datetime.timedelta(days=1)  # Interval for grouping messages
    elif time_period == '1m':
        start_time = now - datetime.timedelta(days=30)
        label_format = '%m-%d'  # Format for x-axis labels
        interval = datetime.timedelta(days=1)  # Interval for grouping messages
    elif time_period == '3m':
        start_time = now - datetime.timedelta(days=90)
        label_format = '%m-%d'  # Format for x-axis labels
        interval = datetime.timedelta(days=30)  # Interval for grouping messages
    elif time_period == '6m':
        start_time = now - datetime.timedelta(days=180)
        label_format = '%m-%d'  # Format for x-axis labels
        interval = datetime.timedelta(days=30)  # Interval for grouping messages
    elif time_period == '9m':
        start_time = now - datetime.timedelta(days=270)
        label_format = '%m-%d'  # Format for x-axis labels
        interval = datetime.timedelta(days=30)  # Interval for grouping messages
    elif time_period == '1y':
        start_time = now - datetime.timedelta(days=365)
        label_format = '%m-%d'  # Format for x-axis labels
        interval = datetime.timedelta(days=30)  # Interval for grouping messages
    elif time_period == '2y':
        start_time = now - datetime.timedelta(days=365 * 2)
        label_format = '%Y-%m'  # Format for x-axis labels
        interval = datetime.timedelta(days=90)  # Interval for grouping messages
    elif time_period == '3y':
        start_time = now - datetime.timedelta(days=365 * 3)
        label_format = '%Y-%m'  # Format for x-axis labels
        interval = datetime.timedelta(days=90)  # Interval for grouping messages
    elif time_period == '5y':
        start_time = now - datetime.timedelta(days=365 * 5)
        label_format = '%Y-%m'  # Format for x-axis labels
        interval = datetime.timedelta(days=180)  # Interval for grouping messages
    elif time_period == 'all':
        start_time = datetime.datetime(1970, 1, 1, tzinfo=timezone)
        label_format = '%Y-%m'  # Format for x-axis labels
        interval = datetime.timedelta(days=365)  # Interval for grouping messages
    else:
        raise ValueError("Invalid time_period.")

    # Fetch activity data from the database
    start_time_unix = int(start_time.timestamp())
    query = f"SELECT DATE(FROM_UNIXTIME(epoch, '%Y-%m-%d %H:%i:%s')) AS date, HOUR(FROM_UNIXTIME(epoch, " \
            f"'%Y-%m-%d %H:%i:%s')) AS hour, COUNT(*) AS count FROM `{guild_id}` WHERE epoch >= {start_time_unix} AND epoch <= " \
            f"UNIX_TIMESTAMP() GROUP BY date, hour"

    data = await db.execute(query, fetch="all")
    print(data)
    # data format - [date, hour, count]

    # Group the data by the specified interval (hourly, daily, etc.)
    grouped_data = {}

    for row in data:
        date = row[0]

        # if time_period 1d, 5d, 1w, 2w, 1m
        if interval == datetime.timedelta(hours=1):
            group_key = date.strftime('%H')
        elif interval == datetime.timedelta(days=30):
            group_key = date.strftime('%Y-%m')
        elif interval == datetime.timedelta(days=90):
            group_key = date.strftime('%Y-%m')
        elif interval == datetime.timedelta(days=180):
            group_key = date.strftime('%Y-%m')
        elif interval == datetime.timedelta(days=365):
            group_key = date.strftime('%Y')
        else:
            group_key = date.strftime('%Y-%m-%d')
        grouped_data[group_key] += row[2]

    # Generate x-axis labels and values
    x_labels = []
    y_values = []
    current_time = start_time
    while current_time <= now:
        if interval == datetime.timedelta(hours=1):
            x_labels.append(current_time.strftime(label_format))
        else:
            x_labels.append(current_time.strftime(label_format))
        y_values.append(grouped_data.get(current_time.strftime('%Y-%m-%d %H'), 0))
        current_time += interval
    # Plot the graph
    plt.plot(x_labels, y_values)
    plt.xlabel('Time')
    plt.ylabel('Message Count')
    plt.title(f'Activity Graph ({time_period})')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('activity.png', dpi=300)

    return list(zip(x_labels, y_values))






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
