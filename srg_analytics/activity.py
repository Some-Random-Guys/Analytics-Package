from .DB import DB
import time

# M = 168
# values = {365: [f'{i}' for i in range(1, 13)], 365 * 2: [f'{i}' for i in range(1, 25)]}


async def backend(db: DB, guild: int, time_period: int, target: str, user: int = None):
    if target == "server":
        messages = [i[0] for i in await db.get(guild, selected=["epoch"])]
        current_time = time.time()

        messages = sorted(filter(lambda x: x >= current_time - (8400 * time_period), messages))

        value = values.get(time_period, time_period)

        x = (messages[-1] - messages[0]) // value

        key_points = [messages[0] + x * (i + 1) for i in range(value)]
        final_output = {k: 0 for k in key_points}

        def categorize_epoch(epoch):
            for point in key_points:
                if epoch <= point:
                    return point

            return key_points[-1]

        for epoch in messages:
            final_output[categorize_epoch(epoch)] += 1

        return list(final_output.items())

    else:
        # Add code for the "user" target
        pass
