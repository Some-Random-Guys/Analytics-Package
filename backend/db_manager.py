# db_manager.py

import chromadb
from chromadb.config import Settings

import collections
import itertools

from backend.logging_ import log
from backend.MAT.preprocessing import all_valid_words


class DB:
    def __init__(self) -> None:
        self.client: chromadb.Client = chromadb.Client(
            Settings(
                chroma_db_impl='duckdb+parquet',
                persist_directory='./data/chroma/'
            )
        )

    def heartbeat(self) -> int:
        """
        Sends a heartbeat request to the client and returns the response.

        Returns:
            int: The heartbeat response from the client.

        Example:
            >>> db = Database()
            >>> db.connect()
            >>> db.heartbeat()
            CHROMADB | Heartbeat: 200
            200
        """
        h = self.client.heartbeat()
        log.info(f'CHROMADB | Heartbeat: {h}')
        return h

    def add_guild(self, guild_id: str, guild_name: str):
        """
        Creates a new collection with the given guild ID and name.

        Args:
            guild_id (str): A string representing the ID of the guild to add.
            guild_name (str): A string representing the name of the guild to add.

        Returns:
            chromadb.api.models.Collection.Collection: A Collection object representing the newly created collection.
        """
        collection = self.client.create_collection(
            name=guild_id, metadata={
                'name': guild_name
            }
        )
        log.info(f'CHROMADB | Added guild: {guild_name}, {guild_id}')
        return collection

    def remove_guild(self, guild_id: str):
        """
        Remove a guild from the database.

        Args:
            guild_id (str): The ID of the guild to remove.

        Returns:
            None.
        """
        collection = self.client.get_collection(guild_id)
        self.client.delete_collection(guild_id)
        log.info(
            f'CHROMADB | Removed guild: {collection.metadata["name"]}, {guild_id}')

    def get_guild(self, guild_id: str):
        """
        Retrieves a guild's collection from the client.

        Args:
            guild_id (str): The ID of the guild to retrieve.

        Returns:
            The collection for the specified guild.
        """
        collection = self.client.get_collection(guild_id)
        log.info(
            f'CHROMADB | Retrieved guild: {collection.metadata["name"]}, {guild_id}')
        return collection

    def purge_guild(self, guild_id):
        """
        Delete all data associated with the specified guild ID.

        Args:
            guild_id (int): The ID of the guild to purge.

        Returns:
            None.

        Raises:
            KeyError: If the guild ID is not found in the database.
        """
        collection = self.get_guild(guild_id)

        # delete all the data in the guild
        log.info(
            f'CHROMADB | Purged guild: {collection.metadata["name"]}, {guild_id}')
        collection.delete()

    def add_datas(self, guild_id: str, msg_content: list[str], msg_id: list[str], author_id: list[str], author_name: list[str], channel_id: list[str], channel_name: list[str], timestamp: list[str], num_attachments: list[str or None], mentions: list[list or None], context: list[str or None]) -> None:
        """
        Adds data to the specified guild's collection.

        Args:
            guild_id (str): The ID of the guild to add data to.
            msg_content (list[str]): A list of message contents to add.
            msg_id (list[str]): A list of message IDs to add.
            author_id (list[str]): A list of author IDs to add.
            author_name (list[str]): A list of author names to add.
            channel_id (list[str]): A list of channel IDs to add.
            channel_name (list[str]): A list of channel names to add.
            timestamp (list[str]): A list of timestamps to add.
            num_attachments (list[str or None]): A list of attachment counts to add.
            mentions (list[list or None]): A list of mention lists to add.
            context (list[str or None]): A list of contextual data to add.

        Returns:
            None: No return value.
        """
        collection = self.get_guild(guild_id)

        # check if all the lengths are equal
        if len(author_id) != len(author_name) or len(channel_id) != len(channel_name) or len(timestamp) != len(num_attachments) or len(mentions) != len(context):
            log.error(
                f'CHROMADB | Error: {len(author_id)}, {len(author_name)}, {len(channel_id)}, {len(channel_name)}, {len(timestamp)}, {len(num_attachments)}, {len(mentions)}, {len(context)}')
            return

        LEN = len(author_id)

        documents = []
        metadata = []
        ids = []
        for i in range(LEN):
            documents.append(msg_content[i])
            metadata.append({
                'author_id': author_id[i],
                'author_name': author_name[i],
                'channel_id': channel_id[i],
                'channel_name': channel_name[i],
                'timestamp': timestamp[i],
                'num_attachments': num_attachments[i] if num_attachments[i] is not None else "000",
                'mentions': ",".join(mentions[i]) if mentions[i] is not None else "000",
                'context': context[i] if context[i] is not None else "000"
            })
            ids.append(msg_id[i])

            log.info(
                f'CHROMADB | Added message to {collection.metadata["name"]}: {msg_content[i]}, {author_id[i]}, {author_name[i]}, {channel_id[i]}, {channel_name[i]}, {timestamp[i]}, {num_attachments[i]}, {mentions[i]}, {context[i]}')

        collection.add(
            documents=documents,
            metadatas=metadata,
            ids=ids
        )

    def _get_documents_and_metadata(self, guild_id: str) -> tuple[list, list]:
        """Retrieves all documents and metadata from a guild, and returns them along with the author_id; (message_content, author_id)"""
        collection = self.get_guild(guild_id)

        data = collection.get(
            include=["documents", "metadatas"]
        )

        return data["documents"], data["metadatas"]

    def get_all_messages_from_guild(self, guild_id: str):
        """Retrieves all messages from a guild, and returns it along with the author_id; (message_content, author_id)"""

        documents, metadatas = self._get_documents_and_metadata(guild_id)

        log.info(
            f'CHROMADB | Retrieved messages from {guild_id}')
        return [(doc, meta["author_id"]) for doc, meta in zip(documents, metadatas)]

    def get_all_messages_from_author(self, guild_id: str, author_id: str):
        """Retrieves all the messages in a particular guild pertaining to a certian author and returns them in a list."""
        collection = self.get_guild(guild_id)

        log.info(
            f'CHROMADB | Retrieved messages from {collection.metadata["name"]}, {author_id}')
        return collection.get(where={"author_id": author_id})['documents']

    def most_used_words_by_guild(self, guild_id: str, n: int = 10) -> list[tuple[str, int]]:
        """Return the `n` most common words used in the guild with ID `guild_id`.

        Args:
            guild_id (str): The ID of the guild to retrieve data from.
            n (int): The number of most common words to return. Default is 10.

        Returns:
            A list of tuples, where each tuple contains a string representing a word and an integer representing its frequency.
        """

        messages = self.get_all_messages_from_guild(guild_id)
        words = all_valid_words(messages)

        freq = collections.Counter(words)

        log.info(
            f'CHROMADB | Retrieved most used words from `{guild_id}`')
        return freq.most_common(n)

    def most_used_words_by_author(self, guild_id: str, author_id: str, n: int = 10) -> list[tuple[str, int]]:
        """Retrieves all the most used words in a guild pertaining to a certian author and returns them in a list."""
        messages = self.get_all_messages_from_author(guild_id, author_id)

        words = all_valid_words(messages)
        freq = collections.Counter(words)

        log.info(
            f'CHROMADB | Retrieved most used words from `{guild_id}`, {author_id}')
        return freq.most_common(n)

    def get_mentions(self, guild_id: str, author_id: str) -> list:
        collection = self.get_guild(guild_id)

        mentions = [x['mentions'] for x in collection.get(
            where={
                "author_id": author_id,
                "mentions": {"$ne": "000"}}
        )['metadatas']]

        # flatten the list
        mentions = list(itertools.chain(*mentions))

        log.info(
            f'CHROMADB | Retrieved mentions from {collection.metadata["name"]}, {author_id}')
        return mentions

    def total_mentions_by_author(self, guild_id: str, author_id: str) -> int:
        """Retrieves the total number of mentions in a guild pertaining to a certian author."""
        mentions = self.get_mentions(guild_id, author_id)

        log.info(
            f'CHROMADB | Retrieved total mentions from {guild_id}, {author_id}')
        return len(mentions)

    def most_mentioned_by_author(self, guild_id: str, author_id: str) -> tuple[str, int]:
        """Retrives the most mentioned user by the author and the number of times mentioned."""
        mentions = self.get_mentions(guild_id, author_id)

        freq = collections.Counter(mentions)

        log.info(
            f'CHROMADB | Retrieved most mentioned user from {guild_id}, {author_id}')
        return freq.most_common(1)[0]

    def author_most_mentioned_by(self, guild_id: str, author_id: str) -> tuple[str, int]:
        """Retrieves the user that has most mentioned the author and the number of times mentioned."""
        collection = self.get_guild(guild_id)

        filtered_metadatas = collection.get(
            where={
                "$and": [
                    {
                        "mentions": {"$ne": "000"}
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

        # return key with the highest value in mentions_count
        max_count = max(mentions_count.values())
        author_with_max_count = [
            k for k, v in mentions_count.items() if v == max_count][0]
        return author_with_max_count, max_count

    def message_count_by_guild(self, guild_id: str) -> int:
        """
        Returns the number of messages sent in the given guild.

        Args:
            guild_id (str): The ID of the guild to count messages in.

        Returns:
            int: The number of messages sent in the guild with the given ID.
        """
        log.info(f"CHROMADB | Retrieved message count from `{guild_id}`")
        return self.get_all_messages_from_guild(guild_id)

    def message_count_by_author(self, guild_id: str, author_id: str) -> int:
        """
        Returns the number of messages sent by the specified author in the specified guild.

        Args:
            guild_id (str): The ID of the guild to search in.
            author_id (str): The ID of the author to search for.

        Returns:
            int: The number of messages sent by the specified author in the specified guild.
        """
        log.info(
            f"CHROMADB | Retrieved message count from `{guild_id}`, {author_id}")
        return self.get_all_messages_from_author(guild_id, author_id)

    def most_active_channel_by_guild(self, guild_id: str) -> tuple[str, int]:
        """
        Returns the ID of the most active channel in the given guild.

        Args:
            guild_id (str): The ID of the guild to search for the most active channel in.

        Returns:
            tuple[str, int]: The ID of the most active channel in the given guild and the number of messages in that channel.
        """

        _, metadatas = self._get_documents_and_metadata(guild_id)

        channel_count = {}
        for metadata in metadatas:
            try:
                channel_count[metadata['channel_id']] += 1
            except KeyError:
                channel_count[metadata['channel_id']] = 1

        max_count = max(channel_count.values())
        author_with_max_count = [
            k for k, v in channel_count.items() if v == max_count][0]

        log.info(
            f'CHROMADB | Retrieved most active channel from {guild_id}')
        return author_with_max_count, max_count

    def most_active_channel_by_author(self, guild_id: str, author_id: str) -> tuple[str, int]:
        """
        Get the most active channel by a specific author in a guild.

        Args:
            guild_id (str): The ID of the guild to search for.
            author_id (str): The ID of the author to search for.

        Returns:
            A tuple containing the name of the most active channel and the number of messages sent.
        """
        collection = self.get_guild(guild_id)

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

        max_count = max(channel_count.values())
        author_with_max_count = [
            k for k, v in channel_count.items() if v == max_count][0]

        log.info(
            f'CHROMADB | Retrieved most active channel from {guild_id}, {author_id}')
        return author_with_max_count, max_count

    def top_n_users(self, guild_id: str, type_: str) -> None:
        """
        Returns the top N users in a guild based on the specified type.

        Args:
            guild_id (str): The ID of the guild.
            type (str): The type of metric to use when calculating the top users. Can be "messages",
                "words", or "characters".

        Returns:
            None
        """

        messages, metadatas = self._get_documents_and_metadata(guild_id)

        # TODO
