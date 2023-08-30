import time

from .DB import DB
import multiprocessing
from collections import Counter

# Top-level function, not nested inside letter_leaderboard
def count_letters(message_list):
    letters = Counter()
    for message in message_list:
        for letter in message.lower():
            if letter.isalpha():
                letters[letter] += 1

    return letters

async def letter_leaderboard(db: DB, guild_id: int, user_id: int = None):
    messages = await db.get_message_content(guild_id)
    batch_size = 10000

    # Create counter for letters
    letters = Counter()

    # Split messages into batches
    message_batches = [messages[i:i + batch_size] for i in range(0, len(messages), batch_size)] # todo make faster

    # Process batches concurrently using multiprocessing pool
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(count_letters, message_batches)
        pool.close()
        pool.join()

    # Sum the results from all batches
    for result in results:
        letters.update(result)

    print(letters)






    return letters

