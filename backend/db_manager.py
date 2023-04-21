# db_manager.py

import chromadb
from config import settings, DataTemplate

import collections
import itertools

from backend.logging_ import log
from backend.MAT.preprocessing import all_valid_words

client = chromadb.Client(settings)


def heartbeat() -> int:
    """
    Sends a heartbeat request to the client and returns the response.

    Returns:
        int: The heartbeat response from the client.
    """

    heartbeat = client.heartbeat()
    log.info(f'CHROMADB | Heartbeat: {heartbeat}')
    return heartbeat


def get_all_guids() -> list[str]:
    """
    Returns a list of all the guild IDs in the database.

    Returns:
        list[str]: A list of all the guild IDs in the database.
    """

    guilds = client.list_collections()
    return guilds


def add_guild(guild_id: str or int):
    """
    Creates a new collection with the given guild ID and name.

    Args:
        guild_id (str or int): A string representing the ID of the guild to add.
        # guild_name (str): A string representing the name of the guild to add.

    Returns:
        chromadb.api.models.Collection.Collection: A Collection object representing the newly created collection.
    """
    guild_id = str(guild_id)
    collection = client.create_collection(
        name=guild_id, metadata={
            # 'name': guild_name
        }
    )
    log.info(f'CHROMADB | Added guild: {guild_id}')
    return collection


def remove_guild(guild_id: str or int):
    """
    Remove a guild from the database.

    Args:
        guild_id (str or int): The ID of the guild to remove.

    Returns:
        None.
    """

    guild_id = str(guild_id)
    collection = client.get_collection(guild_id)

    client.delete_collection(guild_id)

    log.info(f'CHROMADB | Removed guild: {collection.metadata["name"]}, {guild_id}')


def get_guild(guild_id: str or int):
    """
    Retrieves a guild's collection from the client.

    Args:
        guild_id (str or int): The ID of the guild to retrieve.

    Returns:
        The collection for the specified guild.
    """

    guild_id = str(guild_id)
    collection = client.get_collection(guild_id)
    log.info(
        f'CHROMADB | Retrieved guild: {collection.metadata["name"]}, {guild_id}')
    return collection


def purge_guild(guild_id: str or int):
    """
    Delete all data associated with the specified guild ID.

    Args:
        guild_id (str or int): The ID of the guild to purge.

    Returns:
        None.

    Raises:
        KeyError: If the guild ID is not found in the database.
    """

    guild_id = str(guild_id)
    collection = get_guild(guild_id)

    # delete all the data in the guild
    log.info(
        f'CHROMADB | Purged guild: {collection.metadata["name"]}, {guild_id}')
    collection.delete()


def add_data(guild_id: str or int, data: DataTemplate) -> None:
    """
    Adds data to the specified guild's collection.

    Args:
        guild_id (str or int): The ID of the guild to add data to.
        data (DataTemplate): A DataTemplate object containing the data to add.

    Returns:
        None: No return value.
    """

    guild_id = str(guild_id)
    collection = get_guild(guild_id)

    # check if all the lengths of the lists are equal
    if not all(len(data.__dict__[key]) == len(data.message_id) for key in data.__dict__.keys()):
        raise ValueError("All data lengths must be equal.")

    len_ = len(data.author_id)

    documents = []
    metadata = []
    ids = []
    for i in range(len_):
        documents.append(data.message_content[i] if data.message_content[i] is not None else "{{{nOnE}}}")
        metadata.append({
            'author_id': data.author_id[i],
            'is_bot': data.is_bot[i],
            'has_embed': data.has_embed[i],
            'channel_id': data.channel_id[i],
            'timestamp': data.timestamp[i],
            'num_attachments': data.num_attachments[i] if data.num_attachments[i] is not None else "{{{nOnE}}}",
            'mentions': ",".join(data.mentions[i]) if data.mentions[i] is not None else "{{{nOnE}}}",
            'context': data.context[i] if data.context[i] is not None else "{{{nOnE}}}"
        })
        ids.append(data.message_id[i])

        log.info(
            f'CHROMADB | Added message to {collection.metadata["name"]}: {data.message_id}')

    collection.add(
        documents=documents,
        metadatas=metadata,
        ids=ids
    )


def _get_documents_and_metadata(guild_id: str or int) -> tuple[list, list]:
    """Retrieves all documents and metadata from a guild, and returns them along with the author_id; (
    message_content, author_id) """

    guild_id = str(guild_id)
    collection = get_guild(guild_id)

    data = collection.get(
        include=["documents", "metadatas"]
    )

    return data["documents"], data["metadatas"]


def get_all_messages_from_guild(guild_id: str or int):
    """Retrieves all messages from a guild, and returns it along with the author_id; (message_content, author_id)"""

    guild_id = str(guild_id)
    documents, metadatas = _get_documents_and_metadata(guild_id)

    log.info(
        f'CHROMADB | Retrieved messages from {guild_id}')
    return [(doc, meta["author_id"]) for doc, meta in zip(documents, metadatas)]


def get_all_messages_from_user(guild_id: str or int, author_id: str or int) -> list[dict]:
    """Retrieves all the messages in a particular guild pertaining to a certain author and returns them in a list. """

    guild_id = str(guild_id)
    author_id = str(author_id)
    collection = get_guild(guild_id)

    log.info(
        f'CHROMADB | Retrieved messages from {collection.metadata["name"]}, {author_id}')
    return collection.get(where={"author_id": author_id})['documents']


def top_n_words(guild_id: str or int, n: int = 10) -> list[tuple[str, int]]:
    """Return the `n` most common words used in the guild with ID `guild_id`.

    Args:
        guild_id (int or str): The ID of the guild to retrieve data from.
        n (int): The number of most common words to return. Default is 10.

    Returns: A list of tuples, where each tuple contains a string representing a word and an integer representing
    its frequency.
    """
    guild_id = str(guild_id)
    messages = get_all_messages_from_guild(guild_id)
    words = all_valid_words(messages)

    freq = collections.Counter(words)

    log.info(
        f'CHROMADB | Retrieved most used words from `{guild_id}`')
    return freq.most_common(n)


def top_n_words_user(guild_id: str or int, author_id: str or int, n: int = 10) -> list[tuple[str, int]]:
    """Retrieves all the most used words in a guild pertaining to a certain author and returns them in a list."""

    guild_id = str(guild_id)
    author_id = str(author_id)
    messages = get_all_messages_from_user(guild_id, author_id)

    words = all_valid_words(messages)
    freq = collections.Counter(words)

    log.info(
        f'CHROMADB | Retrieved most used words from `{guild_id}`, {author_id}')
    return freq.most_common(n)


def get_mentions(guild_id: str, author_id: str) -> list:
    """Retrieves all the mentions in a guild pertaining to a certain author and returns them in a list."""
    collection = get_guild(guild_id)

    mentions = [x['mentions'] for x in collection.get(
        where={
            "author_id": author_id,
            "mentions": {"$ne": "{{{nOnE}}}"}}
    )['metadatas']]

    # flatten the list
    mentions = list(itertools.chain(*mentions))

    log.info(
        f'CHROMADB | Retrieved mentions from {collection.metadata["name"]}, {author_id}')
    return mentions


def total_mentions_by_author(guild_id: str or int, author_id: str or int) -> int:
    """Retrieves the total number of mentions in a guild pertaining to a certain author."""

    guild_id = str(guild_id)
    author_id = str(author_id)
    mentions = get_mentions(guild_id, author_id)

    log.info(f'CHROMADB | Retrieved total mentions from {guild_id}, {author_id}')
    return len(mentions)


def top_mentions_by_author(guild_id: str or int, author_id: str or int, amount: int) -> tuple[str, int]:
    """Retrieves the most mentioned user by the author and the number of times mentioned."""

    guild_id = str(guild_id)
    author_id = str(author_id)
    mentions = get_mentions(guild_id, author_id)

    freq = collections.Counter(mentions)

    log.info(
        f'CHROMADB | Retrieved most mentioned user from {guild_id}, {author_id}')
    return freq.most_common(amount)[0]  # todo test


def top_mentioned_by(guild_id: str or int, author_id: str or int, amount: int) -> list[tuple[str, int]]:
    """Retrieves the user that has most mentioned the author and the number of times mentioned."""
    collection = get_guild(guild_id)

    filtered_metadatas = collection.get(
        where={
            "$and": [
                {
                    "mentions": {"$ne": "{{{nOnE}}}"}
                },
                {
                    "mentions": {"$contains": author_id}
                }
            ]
        },
        include=["metadatas"]
    )

    mentions_count = {}
    for metadata in filtered_metadatas:
        try:
            mentions_count[metadata['author_id']] += 1
        except KeyError:
            mentions_count[metadata['author_id']] = 1

    mentions_count = sorted(mentions_count.items(), key=lambda x: x[1], reverse=True)
    return mentions_count[:amount] if mentions_count > amount else mentions_count


def total_mentioned_by(guild_id: str or int, author_id: str or int) -> int:  # todo test this, it's probably broken
    """Retrieves the total number of times a user has been mentioned in a guild."""

    guild_id = str(guild_id)
    author_id = str(author_id)
    collection = get_guild(guild_id)

    filtered_metadatas = collection.get(
        where={
            "$and": [
                {
                    "mentions": {"$ne": "{{{nOnE}}}"}
                },
                {
                    "mentions": {"$contains": author_id}
                }
            ]
        },
        include=["metadatas"]
    )

    log.info(
        f'CHROMADB | Retrieved total mentions from {guild_id}, {author_id}')
    return len(filtered_metadatas)


def guild_message_count(guild_id: str or int) -> list[tuple]:
    """
    Returns the number of messages sent in the given guild.

    Args:
        guild_id (str or int): The ID of the guild to count messages in.

    Returns:
        int: The number of messages sent in the guild with the given ID.
    """

    guild_id = str(guild_id)

    log.info(f"CHROMADB | Retrieved message count from `{guild_id}`")
    return get_all_messages_from_guild(guild_id)


def user_message_count(guild_id: str or int, author_id: str or int) -> int:
    """
    Returns the number of messages sent by the specified author in the specified guild.

    Args:
        guild_id (str or int): The ID of the guild to search in.
        author_id (str or int): The ID of the author to search for.

    Returns:
        int: The number of messages sent by the specified author in the specified guild.
    """

    guild_id = str(guild_id)
    author_id = str(author_id)

    log.info(
        f"CHROMADB | Retrieved message count from `{guild_id}`, {author_id}")
    return len(get_all_messages_from_user(guild_id, author_id))


def top_n_channels(guild_id: str or int, amount: int) -> list[tuple]:
    """
    Returns the ID of the most active channel in the given guild.

    Args:
        guild_id (str or int): The ID of the guild to search for the most active channel in.
        amount (int): The number of channels to return.

    Returns: tuple[str, int]: The ID of the most active channel in the given guild and the number of messages in
    that channel.
    """

    guild_id = str(guild_id)
    _, metadatas = _get_documents_and_metadata(guild_id)

    channel_count = {}
    for metadata in metadatas:
        try:
            channel_count[metadata['channel_id']] += 1
        except KeyError:
            channel_count[metadata['channel_id']] = 1

    channel_count = sorted(channel_count.items(), key=lambda x: x[1], reverse=True)

    log.info(f'CHROMADB | Retrieved most active channel from {guild_id}')

    return channel_count[:amount] if amount < len(channel_count) else channel_count


def top_n_channels_user(guild_id: str or int, author_id: str or int, amount: int) -> list:
    """
    Get the most active channel by a specific author in a guild.

    Args:
        guild_id (str or int): The ID of the guild to search for.
        author_id (str or int): The ID of the author to search for.
        amount (int): The amount of channels to return.

    Returns:
        A tuple containing the name of the most active channel and the number of messages sent.
    """

    guild_id = str(guild_id)
    author_id = str(author_id)
    collection = get_guild(guild_id)

    filtered_metadatas = collection.get(
        where={
            "author_id": author_id,
        }
    )

    channel_count = {}
    for metadata in filtered_metadatas:
        try:
            channel_count[metadata['channel_id']] += 1
        except KeyError:
            channel_count[metadata['channel_id']] = 1

    channel_count = sorted(channel_count.items(), key=lambda x: x[1], reverse=True)

    log.info(f'CHROMADB | Retrieved most active channel from {guild_id}, {author_id}')

    return channel_count[:amount] if amount < len(channel_count) else channel_count


def top_n_users(guild_id: str or int, type_: str, amount: int):
    """
    Returns the top N users in a guild based on the specified type.

    Args:
        guild_id (str or int): The ID of the guild.
        type_ (str): The type of metric to use when calculating the top users. Can be "messages",
            "words", or "characters".

    Returns:
        None
    """

    guild_id = str(guild_id)
    if type_ not in ["messages", "words", "characters"]:
        if type_ not in ["m" "w", "c"]:
            raise ValueError("type_ must be one of 'messages', 'words', or 'characters'")
        else:
            type_ = "messages" if type_ == "m" else "words" if type_ == "w" else "characters"

    messages, metadatas = _get_documents_and_metadata(guild_id)

    # TODO make this, and respect amount


def top_n_emojis(guild_id: str or int, amount: int):
    """
    Returns the top N emojis used in a guild.

    Args:
        guild_id (str or int): The ID of the guild.

    Returns:
        None
    """

    guild_id = str(guild_id)

    # TODO make this, and respect amount
