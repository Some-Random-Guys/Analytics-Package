import random
from .DB import DB
import mplcyberpunk
import datetime
import matplotlib.pyplot as plt


async def activity_guild(db, guild_id, time_period, interval, time_zone: datetime.timezone = None):

    # If there is no time zone, set it to UTC+3
    if time_zone is None:
        time_zone = datetime.timezone(datetime.timedelta(hours=3))

    now = datetime.datetime.now(time_zone)

    # Define the time periods and intervals
    periods = {
        '1d': (now.replace(hour=0, minute=0, second=0, microsecond=0), datetime.timedelta(hours=1), '%H:%M'),
        '5d': (now - datetime.timedelta(days=4), datetime.timedelta(days=1), '%m-%d'),
        '1w': (now - datetime.timedelta(weeks=1), datetime.timedelta(days=1), '%m-%d'),
        '2w': (now - datetime.timedelta(weeks=2), datetime.timedelta(days=1), '%m-%d'),
        '1m': (now - datetime.timedelta(days=30), datetime.timedelta(days=1), '%m-%d'),
        '3m': (now - datetime.timedelta(days=90), datetime.timedelta(days=30), '%m-%d'),
        '6m': (now - datetime.timedelta(days=180), datetime.timedelta(days=30), '%m-%d'),
        '9m': (now - datetime.timedelta(days=270), datetime.timedelta(days=30), '%m-%d'),
        '1y': (now - datetime.timedelta(days=365), datetime.timedelta(days=30), '%m-%d'),
        '2y': (now - datetime.timedelta(days=365 * 2), datetime.timedelta(days=90), '%Y-%m'),
        '3y': (now - datetime.timedelta(days=365 * 3), datetime.timedelta(days=90), '%Y-%m'),
        '5y': (now - datetime.timedelta(days=365 * 5), datetime.timedelta(days=180), '%Y-%m'),
        'all': (datetime.datetime(1970, 1, 1, tzinfo=time_zone), datetime.timedelta(days=365), '%Y-%m')
    }

    # Retrieve the start time, interval, and label format based on the time period
    start_time, interval, label_format = periods.get(time_period)
    start_time_unix = int(start_time.timestamp())

    # Fetch activity data from the database
    query = f"SELECT FROM_UNIXTIME(epoch, '%Y-%m-%d %H:00:00') AS datetime, COUNT(*) AS count FROM `{guild_id}` WHERE epoch >= {start_time_unix} AND epoch <= UNIX_TIMESTAMP() GROUP BY datetime"
    data = await db.execute(query, fetch="all")
    # data format - [(datetime, count), ...]

    # Group the data by the specified interval (hourly, daily, etc.)
    grouped_data = {}
    for row in data:
        date = row[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        group_key = date.strftime(label_format)
        grouped_data.setdefault(group_key, 0)
        grouped_data[group_key] += row[1]

    # fill in all missing data points with 0
    for i in range(int((now - start_time) / interval) + 1):
        key = (start_time + interval * i).strftime(label_format)
        grouped_data.setdefault(key, 0)

    # if time_period is 1, fill in values till 23 but keep them 0
    if time_period == '1d':
        for i in range(24):
            key = (start_time + interval * i).strftime(label_format)
            grouped_data.setdefault(key, 0)

    # sort the data by date
    grouped_data = dict(sorted(grouped_data.items(), key=lambda x: datetime.datetime.strptime(x[0], label_format)))

    # Generate x-axis labels and values
    x_labels = list(grouped_data.keys())
    y_values = list(grouped_data.values())

    return x_labels, y_values


async def activity_user(guild_id: int, time_period: str):
    pass


async def activity_guild_visual(db: DB, guild_id: int, time_period: int, time_zone: datetime.timezone = None):
    x, y = await activity_guild(db, guild_id, time_period)
    plt.style.use("cyberpunk")

    # Plot the graph
    plt.plot(x, y, "-o")

    # Add labels and title
    plt.xlabel('Time')
    plt.ylabel('Message Count')
    plt.title(f'Activity Graph ({time_period})')

    # Rotate x-axis labels
    plt.xticks(rotation=45)

    plt.grid(True)
    plt.tight_layout()

    # apply glow effects
    mplcyberpunk.make_lines_glow()
    mplcyberpunk.add_gradient_fill(alpha_gradientglow=0.5)

    name = random.randint(1, 100000000)
    plt.savefig(f"{name}.png", format='png', dpi=400, bbox_inches="tight")
    plt.close()

    return f"{name}.png"
