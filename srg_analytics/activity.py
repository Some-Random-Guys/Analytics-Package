import random
from typing import Any

from .DB import DB
import mplcyberpunk
import datetime
import matplotlib.pyplot as plt

_days = {
    # format - timeperiod: (days, number of data points)
        '1d': (1, 24),
        '3d': (3, 3),
        '5d': (5, 5),
        '1w': (7, 7),
        '2w': (14, 14),
        '1m': (30, 30),
        '3m': (90, 3),
        '6m': (180, 6),
        '9m': (270, 9),
        '1y': (365, 12),
        '2y': (730, 24),
        '3y': (1095, 36),
        '5y': (1825, 5),
    }

async def _generate_timeperiod(time_period, timezone: datetime.timezone = None):

    # If there is no time zone, set it to UTC+3
    if timezone is None:
        timezone = datetime.timezone(datetime.timedelta(hours=3))

    now = datetime.datetime.now(timezone)

    # Define the time periods and intervals
    periods = {
        # todo this will take days=30 for some reason when if it's set to anything else in 3m and above when format is %d-%m
        '1d': (now.replace(hour=0, minute=0, second=0, microsecond=0), '%H'),
        '5d': (now - datetime.timedelta(days=_days['5d'][0]), '%d-%m-%Y'),
        '1w': (now - datetime.timedelta(days=_days['1w'][0]), '%d-%m-%Y'),
        '2w': (now - datetime.timedelta(days=_days['2w'][0]), '%d-%m-%Y'),
        '1m': (now - datetime.timedelta(days=_days['1m'][0]), '%d-%m-%Y'),
        '3m': (now - datetime.timedelta(days=_days['3m'][0]), '%m-%Y'),
        '6m': (now - datetime.timedelta(days=_days['6m'][0]), '%m-%Y'),
        '9m': (now - datetime.timedelta(days=_days['9m'][0]), '%m-%Y'),
        '1y': (now - datetime.timedelta(days=_days['1y'][0]), '%m-%Y'),
        '2y': (now - datetime.timedelta(days=_days['2y'][0]), '%m-%Y'),
        '3y': (now - datetime.timedelta(days=_days['3y'][0]), '%m-%Y'),
        '5y': (now - datetime.timedelta(days=_days['5y'][0]), '%Y'),
        'all': (datetime.datetime(2015, 4, 1, tzinfo=timezone), '%Y')
    }

    try:
        start_time, label_format = periods.get(time_period)
    except TypeError:
        raise ValueError(f"Invalid time period: {time_period}")


    return now, start_time, label_format

async def _structure_data(data, start_time, time_period, label_format, timezone: datetime.timezone = None):
    # Group the data by the specified interval (hourly, daily, etc.)
    grouped_data = {}
    for row in data:
        group_key = row[0]
        grouped_data.setdefault(group_key, 0)
        grouped_data[group_key] += row[1]

    # Fill in missing data points with 0
    for i in range(_days[time_period][1]):
        if time_period == '1d':
            key = (start_time + datetime.timedelta(hours=i)).strftime(label_format)
        else:
            key = (start_time + datetime.timedelta(days=i)).strftime(label_format)

        grouped_data.setdefault(key, 0)

    # Sort the data by date
    sorted_data = sorted(grouped_data.items(), key=lambda x: datetime.datetime.strptime(x[0], label_format))

    # Split the data into x and y values
    x = [row[0] for row in sorted_data]
    y = [row[1] for row in sorted_data]

    # if there are extra values, pop the start values to make length == time_period
    if time_period != "all":
        if len(y) > _days[time_period][1]:
            y = y[len(y) - (_days[time_period][1]):]
            x = x[len(x) - (_days[time_period][1]):]


    return x, y


async def activity_guild(db, guild_id, time_period, timezone: datetime.timezone = None):

    now, start_time, label_format = await _generate_timeperiod(time_period, timezone)

    # Define the SQL query template
    query_template = f"""
        SELECT 
            DATE_FORMAT(FROM_UNIXTIME(epoch), %s) AS datetime, 
            COUNT(*) AS count 
        FROM 
            `{guild_id}` 
        WHERE 
            epoch >= %s AND epoch <= UNIX_TIMESTAMP() 
        GROUP BY 
            datetime
    """

    # Define the query parameters
    query_params = (label_format.replace("%M", "%i"), start_time.timestamp(),)

    # Execute the SQL query
    data = await db.execute(query_template, query_params, fetch="all")

    # Structure the data
    x_labels, y_values = await _structure_data(data, start_time, time_period, label_format, timezone)

    return x_labels, y_values



async def activity_guild_visual(db: DB, guild_id: int, time_period: str, timezone: datetime.timezone = None):
    x, y = await activity_guild(db, guild_id, time_period, timezone)
    plt.style.use("cyberpunk")

    try:
        # Plot the graph
        plt.plot(x, y, "-o")

        # Add labels and title
        plt.xlabel("Timeperiod")
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

    except Exception as e:
        print(e)
        plt.close()

        return None


async def activity_user(
        db: DB, guild_id: int, user_list: list[int], time_period: str, include_server: bool, timezone: datetime.timezone = None
) -> tuple[tuple[Any, ...] | None, dict[int, list[Any]]]:
    # user_list is a list of user ids

    now, start_time, label_format = await _generate_timeperiod(time_period, timezone)

    x_labels = None
    y_values = {}

    for user_id in user_list:

        # Define the SQL query template
        query_template = f"""
            SELECT 
                DATE_FORMAT(FROM_UNIXTIME(epoch), %s) AS datetime, 
                COUNT(*) AS count
            FROM 
                `{guild_id}`
            WHERE
                epoch >= %s AND epoch <= UNIX_TIMESTAMP() 
                AND author_id = %s
            GROUP BY
                datetime
        """

        # Define the query parameters
        query_params = (label_format.replace("%M", "%i"), start_time.timestamp(), user_id,)

        # Execute the SQL query
        data = await db.execute(query_template, query_params, fetch="all")

        # Structure the data
        x, y = await _structure_data(data, start_time, time_period, label_format, timezone)

        # Add the data to the graph
        if x_labels is None:
            x_labels = tuple(x)
        y_values[user_id] = y

    if include_server:
        # Define the SQL query template
        query_template = f"""
            SELECT 
                DATE_FORMAT(FROM_UNIXTIME(epoch), %s) AS datetime, 
                COUNT(*) AS count
            FROM 
                `{guild_id}`            
            WHERE
                epoch >= %s AND epoch <= UNIX_TIMESTAMP()
                
            GROUP BY
                datetime
        """

        # Define the query parameters
        query_params = (label_format.replace("%M", "%i"), start_time.timestamp(),)

        # Execute the SQL query
        data = await db.execute(query_template, query_params, fetch="all")

        # Structure the data
        x, y = await _structure_data(data, start_time, time_period, label_format, timezone)

        # Add the data to the graph
        if x_labels is None:
            x_labels = tuple(x)
        y_values["Server"] = y

    return x_labels, y_values

async def activity_user_visual(db: DB, guild_id: int, user_list: list, time_period: str, include_server: bool, timezone: datetime.timezone = None):

    usernames = [user[0] for user in user_list]
    user_ids = [user[1] for user in user_list]

    x, y = await activity_user(db, guild_id, user_ids, time_period, include_server, timezone)
    plt.style.use("cyberpunk")
    try:
        # y is a dict of user_id: y_values
        for user_id, y_values in y.items():
            plt.plot(x, y_values, "-o", label=f"{usernames[user_ids.index(user_id)]}")

        # Add labels and title
        plt.xlabel("Timeperiod")
        plt.ylabel('Message Count')
        plt.title(f'Activity Graph ({time_period})')

        # Rotate x-axis labels
        plt.xticks(rotation=45)

        plt.grid(True)
        plt.tight_layout()
        plt.legend()

        # apply glow effects
        mplcyberpunk.add_glow_effects()

        name = random.randint(1, 100000000)
        plt.savefig(f"{name}.png", format='png', dpi=400, bbox_inches="tight")
        plt.close()

        return f"{name}.png"
    except Exception as e:
        print(e)
        plt.close()
        return None
