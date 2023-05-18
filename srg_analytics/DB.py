"""Functions for interacting with the database."""

import mysql.connector as mysql
from .schemas import DbCreds, DataTemplate


class DB:
    """Class for interaction with the database."""

    def __init__(self, db_credentials: DbCreds):
        self.db_credentials: DbCreds = db_credentials

        self.con = mysql.connect(
            host=self.db_credentials.host,
            port=self.db_credentials.port,
            user=self.db_credentials.user,
            password=self.db_credentials.password,
            database=self.db_credentials.name,
        )

        self.cur = self.con.cursor(prepared=True)

        # check if the "data" table exists
        self.cur.execute(
            """
                CREATE TABLE IF NOT EXISTS config (
                _key TEXT NOT NULL,
                data1 TEXT NOT NULL,
                data2 TEXT NULL,
                data3 TEXT NULL
            );
            """
        )

        self.con.commit()

        # Note: This table will contain the following (so far):
        # - channel_ignore
        # - user_ignore
        # - guild_pause
        # - stopword
        # - alias

        # Format -
        # - channel_ignore:
        #  - _key: channel_ignore
        #  - data1: guild_id
        #  - data2: channel_id
        #  - data3: None

        # - user_ignore:
        #  - _key: user_ignore
        #  - data1: guild_id
        #  - data2: user_id
        #  - data3: None

        # - alias:
        #  - _key: alias
        #  - data1: guild_id
        #  - data2: user_id
        #  - data3: alias_id

    async def add_guild(self, guild_id):
        """Adds a guild (database), with boilerplate table."""
        self.cur.execute(
            f"""
                CREATE TABLE IF NOT EXISTS `{guild_id}` (
                message_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                author_id BIGINT NOT NULL,
                message_content BLOB,
                epoch BIGINT NOT NULL,
                is_bot BOOLEAN NOT NULL,
                has_embed BOOLEAN NOT NULL,                       
                num_attachments SMALLINT NOT NULL DEFAULT 0,
                ctx_id BIGINT,
                mentions TEXT,
                PRIMARY KEY (message_id)
                );
            """
        )

        self.con.commit()

    async def remove_guild(self, guild_id):
        """Removes the guild from the database."""
        self.cur.execute(f"DROP TABLE IF EXISTS `{guild_id}`;")

        self.con.commit()

    async def get_guild(self, guild_id):
        """Retrives the guild from the database."""
        self.cur.execute(f"SELECT * FROM `{guild_id}`;")

        return self.cur.fetchall()

    async def get_guilds(self):  # TODO TEST
        self.cur.execute("SHOW TABLES;")

        return self.cur.fetchall()

    async def add_message(self, guild_id, data: DataTemplate):
        self.cur.execute(
            f"""
                        INSERT IGNORE INTO `{guild_id}` (message_id, channel_id, author_id, message_content, epoch, 
                        is_bot, has_embed, num_attachments, ctx_id, mentions)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

                    """,
            (
                data.message_id,
                data.channel_id,
                data.author_id,
                data.message_content,
                data.epoch,
                data.is_bot,
                data.has_embed,
                data.num_attachments,
                data.ctx_id,
                data.mentions,
            ),
        )

        self.con.commit()

    async def delete_message(self, guild_id: int, message_id: int):
        self.cur.execute(f"DELETE FROM `{guild_id}` WHERE message_id = {message_id};")
        self.con.commit()

    async def add_ignore(
        self, guild_id: int, channel_id: int = None, user_id: int = None
    ):
        if channel_id is None and user_id is None:
            raise ValueError("channel_id and user_id cannot both be None")

        # Ignore based on channel_id
        if channel_id is not None:
            # Add to database
            self.cur.execute(
                "INSERT IGNORE INTO `config` (_key, data1, data2) VALUES ('channel_ignore', ?, ?);",
                (
                    guild_id,
                    channel_id,
                ),
            )

            self.con.commit()

        # Ignore based on user_id
        elif user_id is not None:
            # Add to database
            self.cur.execute(
                "INSERT IGNORE INTO `config` (_key, data1, data2) VALUES ('user_ignore', ?, ?);",
                (
                    guild_id,
                    user_id,
                ),
            )

            self.con.commit()

    async def remove_ignore(
        self, guild_id: int, channel_id: int = None, user_id: int = None
    ):
        if channel_id is None and user_id is None:
            raise ValueError("channel_id and user_id cannot both be None")

        # Ignore based on channel_id
        if channel_id is not None:
            # Add to database
            self.cur.execute(
                "DELETE FROM `config` WHERE _key = 'channel_ignore' AND data1 = ? AND data2 = ?;",
                (
                    guild_id,
                    channel_id,
                ),
            )

        # Ignore based on user_id
        elif user_id is not None:
            # Add to database
            self.cur.execute(
                "DELETE FROM `config` WHERE _key = 'user_ignore' AND data1 = ? AND data2 = ?;",
                (
                    guild_id,
                    user_id,
                ),
            )

        self.con.commit()

    async def get_ignore_list(self, type_: str, guild_id: int = None) -> dict or list:
        if type_ not in ["channel", "user"]:
            raise ValueError("type_ must be either 'channel' or 'user'")

        if guild_id is not None:
            self.cur.execute(
                "SELECT data1, data2 FROM `config` WHERE _key = ? AND data1 = ?;",
                (f"{type_}_ignore", guild_id),
            )

            # format of res: [(guild_id, channel_id), (guild_id, channel_id), ...]
            res = self.cur.fetchall()

            # convert to this format -
            # [channel_id, channel_id, ...]
            res = [int(channel_id) for _, channel_id in res if _ == guild_id]
            return res

        else:
            # get list of the one that is not None
            self.cur.execute(
                "SELECT data1, data2 FROM `config` WHERE _key = ?;",
                (f"{type_}_ignore",),
            )

            # format of res: [(guild_id, channel_id), (guild_id, channel_id), ...]
            res = self.cur.fetchall()

            # convert to this format -
            # {
            #   guild_id: [channel_id, channel_id, ...],
            #   guild_id: [channel_id, channel_id, ...], ...
            # }
            res = {
                int(guild_id): [
                    int(channel_id) for _, channel_id in res if _ == guild_id
                ]
                for guild_id, _ in res
            }
            return res

    async def add_user_alias(self, guild_id: int, user_id: int, alias_id: int):
        self.cur.execute(
            "INSERT IGNORE INTO `config` (_key, data1, data2, data3) VALUES ('alias', ?, ?, ?);",
            (guild_id, user_id, alias_id),
        )

        self.con.commit()

    async def remove_user_alias(self, guild_id: int, user_id: int, alias_id: int):
        self.cur.execute(
            "DELETE FROM `config` WHERE _key = 'alias' AND data1 = ? AND data2 = ? AND data3 = ?;",
            (guild_id, user_id, alias_id),
        )

        self.con.commit()

    async def get_user_aliases(self, guild_id: int = None):
        if guild_id is None:
            self.cur.execute(
                "SELECT data1, data2, data3 FROM `config` WHERE _key = 'alias';"
            )

            # data1 is guild_id, data2 is user_id, data3 is alias_id

            res = self.cur.fetchall()

            # convert into this format -
            # {
            #   guild_id: {
            #       user_id: [alias_id, alias_id, ...],
            #       user_id: [alias_id, alias_id, ...], ...
            #   },
            #   guild_id: {
            #       user_id: [alias_id, alias_id, ...],
            #       user_id: [alias_id, alias_id, ...], ...
            #   }, ...

            result = {}

            for row in res:
                guild_id, user_id, alias_id = row

                if guild_id not in result:
                    result[guild_id] = {}

                if user_id not in result[guild_id]:
                    result[guild_id][user_id] = []

                result[guild_id][user_id].append(alias_id)

            # make sure all the ids are ints
            result = {
                int(guild_id): {
                    int(user_id): [int(alias_id) for alias_id in alias_ids]
                    for user_id, alias_ids in user_ids.items()
                }
                for guild_id, user_ids in result.items()
            }

            return result

        else:
            self.cur.execute(
                "SELECT data2, data3 FROM `config` WHERE _key = 'alias' AND data1 = ?;",
                (guild_id,),
            )

            # data2 is user_id, data3 is alias_id

            res = self.cur.fetchall()

            # convert into this format -
            # {
            #   user_id: [alias_id, alias_id, ...],
            #   user_id: [alias_id, alias_id, ...], ...
            # }

            res = {
                int(user_id): [int(alias_id) for _, alias_id in res if _ == user_id]
                for user_id, _ in res
            }

            return res

    # analysis functions
    async def get_message_count(
        self, guild_id: int, channel_id: int = None, user_id: int = None
    ):
        if guild_id is None:
            raise ValueError("guild_id cannot be None")

        if channel_id is None and user_id is None:
            self.cur.execute(
                f"SELECT COUNT(*) FROM `{guild_id}`",
            )

            return self.cur.fetchone()[0]

        elif channel_id is not None and user_id is None:
            self.cur.execute(
                f"SELECT COUNT(*) FROM `{guild_id}` WHERE channel_id = ?;",
                (channel_id,),
            )

            return self.cur.fetchone()[0]

        elif channel_id is None and user_id is not None:
            self.cur.execute(
                f"SELECT COUNT(*) FROM `{guild_id}` WHERE author_id = ?;",
                (user_id,),
            )

            return self.cur.fetchone()[0]

        else:
            self.cur.execute(
                f"SELECT COUNT(*) FROM `{guild_id}` WHERE channel_id = ? AND author_id = ?;",
                (channel_id, user_id),
            )

            return self.cur.fetchone()[0]

    async def get_mentions(self, guild_id: int, user_id: int) -> list[int]:
        """Returns all the instances where mentions are not empty, where user_id;"""
        if user_id is not None:
            self.cur.execute(
                f"SELECT mentions FROM `{guild_id}` WHERE author_id = ? AND mentions IS NOT NULL;",
                (user_id,),
            )

        res = [x[0] for x in self.cur.fetchall()]

        # each mention can be a csv; we need to unpack the strings
        data = []
        for mention in res:
            data.extend([int(mention_) for mention_ in mention.split(",")])

        return data

    async def get_all_mentions(self, guild_id: int) -> list[int, list[int]]:
        """Returns all the instances where mentions are not empty, in the guild, along with who the messages belonged to"""
        self.cur.execute(
            f"SELECT author_id, mentions FROM `{guild_id}` WHERE mentions IS NOT NULL;",
        )

        res = self.cur.fetchall()
        data = []

        for author_id, mentions in res:
            data.extend(
                [int(author_id), [int(mention_) for mention_ in mentions.split(",")]]
            )

        return data

    async def get_message_content(
        self, guild_id: int, channel_id: int = None, user_id: int = None
    ) -> list[str]:
        if channel_id is None and user_id is None:
            self.cur.execute(
                f"SELECT message_content FROM `{guild_id}` WHERE message_content IS NOT NULL;",
            )

            res = self.cur.fetchall()

        elif channel_id is not None and user_id is None:
            self.cur.execute(
                f"SELECT message_content FROM `{guild_id}` WHERE channel_id = ? AND message_content IS NOT NULL;",
                (channel_id,),
            )

            res = self.cur.fetchall()

        elif channel_id is None and user_id is not None:
            self.cur.execute(
                f"SELECT message_content FROM `{guild_id}` WHERE author_id = ? AND message_content IS NOT NULL;",
                (user_id,),
            )

            res = self.cur.fetchall()

        else:
            self.cur.execute(
                f"SELECT message_content FROM `{guild_id}` WHERE channel_id = ? AND author_id = ? AND message_content IS NOT NULL;",
                (channel_id, user_id),
            )

            res = self.cur.fetchall()

        return [message_content[0] for message_content in res]
