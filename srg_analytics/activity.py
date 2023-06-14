from .DB import DB
import time
from matplotlib import pyplot as plt

# M = 168
# values = {365: [f'{i}' for i in range(1, 13)], 365 * 2: [f'{i}' for i in range(1, 25)]}

# todo split this function into 2 different functions, one for server and one for user
import time


async def activity_guild(db: DB, guild_id: int, time_period: int, ):
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


async def activity_guild_visual(db: DB, guild_id: int, time_period: int):
    raw_data = await activity_guild(db, guild_id, time_period)

    # based on the time_period we can determine the x-axis labels
    labels = {
        1: [f'{i}' for i in range(1, 25)],  # 1 day, 1 hour intervals
        3: [f'{i}' for i in range(1, 25)],  # 3 days, 3 hour intervals
        5: [f'{i}' for i in range(1, 25)],  # 5 days, 5 hour intervals
        7: [f'{i}' for i in range(1, 25)],  # 7 days, 7 hour intervals
        14: [f'{i}' for i in range(1, 25)],  # 14 days, 1 day intervals
        21: [f'{i}' for i in range(1, 25)],  # 21 days, 3 day intervals
        30: [f'{i}' for i in range(1, 25)],  # 30 days, 1 day intervals
        60: [f'{i}' for i in range(1, 25)],  # 60 days, 3 day intervals
        90: [f'{i}' for i in range(1, 25)],  # 90 days, 3 day intervals
        180: [f'{i}' for i in range(1, 25)],  # 180 days, 1 day intervals
        270: [f'{i}' for i in range(1, 25)],  # 270 days, 1 day intervals
        365: [f'{i}' for i in range(1, 25)],  # 365 days, 3 day intervals
        # Add more intervals as needed
    }





