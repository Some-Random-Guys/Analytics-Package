import random
from .DB import DB
import mplcyberpunk
import datetime
import matplotlib.pyplot as plt


async def activity_guild(db, guild_id, time_period, interval=None, time_zone: datetime.timezone = None):

    # If there is no time zone, set it to UTC+3
    if time_zone is None:
        time_zone = datetime.timezone(datetime.timedelta(hours=3))

    now = datetime.datetime.now(time_zone)

    # Define the time periods and intervals
    periods = {
        '1d': (now.replace(hour=0, minute=0, second=0, microsecond=0), datetime.timedelta(hours=1), '%H:%M'),
        '3d': (now - datetime.timedelta(days=2), datetime.timedelta(days=1), '%d-%m'),
        '5d': (now - datetime.timedelta(days=4), datetime.timedelta(days=1), '%d-%m'),
        '1w': (now - datetime.timedelta(weeks=1), datetime.timedelta(days=1), '%d-%m'),
        '2w': (now - datetime.timedelta(weeks=2), datetime.timedelta(days=1), '%d-%m'),
        '1m': (now - datetime.timedelta(days=30), datetime.timedelta(days=1), '%d-%m'),
        '3m': (now - datetime.timedelta(days=90), datetime.timedelta(days=30), '%m-%Y'),    # todo shows 4 months
        '6m': (now - datetime.timedelta(days=180), datetime.timedelta(days=30), '%m-%Y'),   # todo shows 7 months
        '9m': (now - datetime.timedelta(days=270), datetime.timedelta(days=30), '%m-%Y'),
        '1y': (now - datetime.timedelta(days=365), datetime.timedelta(days=30), '%m-%Y'),
        '2y': (now - datetime.timedelta(days=365 * 2), datetime.timedelta(days=90), '%m-%Y'),
        '3y': (now - datetime.timedelta(days=365 * 3), datetime.timedelta(days=90), '%Y'),
        '5y': (now - datetime.timedelta(days=365 * 5), datetime.timedelta(days=180), '%Y'),
        'all': (datetime.datetime(2015, 4, 1, tzinfo=time_zone), datetime.timedelta(days=365), '%Y')
    }

    start_time, _, label_format = periods.get(time_period)
    start_time_unix = int(start_time.timestamp())

    # Determine the interval based on the provided or default value
    if interval is None:
        # Retrieve the start time, interval, and label format based on the time period
        interval = _

        print(interval)

    else:
        # interval can be `hours`, `days`, `weeks`, `months`, or `years`
        if interval in ["hours", "days", "weeks"]:
            interval = datetime.timedelta(**{f'{interval}': 1})
        elif interval == "months":
            interval = datetime.timedelta(days=30)
        elif interval == "years":
            interval = datetime.timedelta(days=365)

        # get the label format based on the interval
        if interval.days >= 365:
            label_format = '%m-%Y'
        elif interval.days >= 30:
            label_format = '%d-%m'
        else:
            label_format = '%H:%M'

    interval_hours = interval.total_seconds() / 3600

    # Fetch activity data from the database
    query = f"SELECT FROM_UNIXTIME(epoch, '%Y-%m-%d %H:00:00') AS datetime, COUNT(*) AS count FROM `{guild_id}` WHERE epoch >= {start_time_unix} AND epoch <= UNIX_TIMESTAMP() GROUP BY datetime"
    data = await db.execute(query, fetch="all")

    # Group the data by the specified interval (hourly, daily, etc.)
    grouped_data = {}
    for row in data:
        date = row[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        if interval_hours < 1:
            group_key = date.strftime(label_format)
        else:
            group_key = (date - datetime.timedelta(hours=date.hour % interval_hours)).strftime(label_format)
        grouped_data.setdefault(group_key, 0)
        grouped_data[group_key] += row[1]

    # Fill in all missing data points with 0
    current_time = start_time
    while current_time <= now:
        key = current_time.strftime(label_format)
        grouped_data.setdefault(key, 0)
        current_time += interval

    # If time_period is 1d, fill in values till 23 but keep them 0
    if time_period == '1d':
        for i in range(24):
            key = (start_time + datetime.timedelta(hours=i)).strftime(label_format)
            grouped_data.setdefault(key, 0)

    # Sort the data by date
    grouped_data = dict(sorted(grouped_data.items(), key=lambda x: datetime.datetime.strptime(x[0], label_format)))

    # Generate x-axis labels and values
    x_labels = list(grouped_data.keys())
    y_values = list(grouped_data.values())

    return x_labels, y_values


async def activity_user(guild_id: int, time_period: str):
    pass


async def activity_guild_visual(db: DB, guild_id: int, time_period: int, interval: str = None,
                                timezone: datetime.timezone = None):
    x, y = await activity_guild(db, guild_id, time_period, interval, timezone)
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
    mplcyberpunk.add_glow_effects()

    name = random.randint(1, 100000000)
    plt.savefig(f"{name}.png", format='png', dpi=400, bbox_inches="tight")
    plt.close()

    return f"{name}.png"
