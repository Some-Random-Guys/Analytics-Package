"""Functions for interacting with the database."""

import aiomysql
from .schemas import DbCreds, DataTemplate
import asyncio


class DB:
    """Class for interaction with the database."""

    def __init__(self, db_credentials: DbCreds):
        self.con = None
        self.db_credentials: DbCreds = db_credentials
        self.is_connected = False

        asyncio.create_task(self.connect())  # this doesn't work

    async def connect(self):
        self.con = await aiomysql.create_pool(
            host=self.db_credentials.host,
            port=self.db_credentials.port,
            user=self.db_credentials.user,
            password=self.db_credentials.password,
            db=self.db_credentials.name,
            autocommit=True
        )

        self.is_connected = True

        await self._create_data_table()

    async def _create_data_table(self):
        # check if the "data" table exists, if not, create it
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                        CREATE TABLE IF NOT EXISTS config (
                        _key TEXT NOT NULL,
                        data1 TEXT NOT NULL,
                        data2 TEXT NULL,
                        data3 TEXT NULL
                    );
                    """
                )

        # Note: This table will contain the following (so far):
        # - channel_ignore
        # - user_ignore
        # - guild_pause
        # - stopword
        # - alias
        # - timezone

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

        # - timezone:
        #  - _key: timezone
        #  - data1: guild_id
        #  - data2: user_id
        #  - data3: timezone


    async def add_guild(self, guild_id):
        """Adds a guild (database), with boilerplate table."""
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
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

    async def remove_guild(self, guild_id):
        """Removes the guild from the database."""
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"DROP TABLE IF EXISTS `{guild_id}`;")

    async def execute(self, query, args=None, fetch=None):
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query.replace("?", "%s"), args)
                if fetch is None:
                    return
                if fetch == "all":
                    return await cur.fetchall()
                elif fetch == "one":
                    return await cur.fetchone()

            await conn.commit()

    async def get(self, guild_id, selected: list = None):
        """Retrieves the guild from the database."""

        if selected is None:
            selected = ["*"]
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"SELECT {', '.join(selected)} FROM `{guild_id}`;")

                return await cur.fetchall()

    async def get_guilds(self):  # TODO TEST
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SHOW TABLES;")

                return await cur.fetchall()

    async def add_message(self, guild_id, data: DataTemplate):
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
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

    async def delete_message(self, guild_id: int, message_id: int):
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"DELETE FROM `{guild_id}` WHERE message_id = {message_id};")

    async def edit_message(self, guild_id: int, message_id: int, new_content: str):
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"UPDATE `{guild_id}` SET message_content = %s WHERE message_id = %s;",
                    (new_content, message_id,),
                )

    async def add_ignore(
            self, guild_id: int, channel_id: int = None, user_id: int = None, update_existing: bool = False
    ):
        if channel_id is None and user_id is None:
            raise ValueError("channel_id and user_id cannot both be None")

        # Ignore based on channel_id
        if channel_id is not None:
            # Add to database
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "INSERT IGNORE INTO `config` (_key, data1, data2) VALUES ('channel_ignore', %s, %s);",
                        (guild_id, channel_id,),
                    )

                    if update_existing:
                        await cur.execute(
                            f"DELETE FROM `{guild_id}` WHERE channel_id = {channel_id};"
                        )

        # Ignore based on user_id
        elif user_id is not None:
            # Add to database
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "INSERT IGNORE INTO `config` (_key, data1, data2) VALUES ('user_ignore', %s, %s);",
                        (guild_id, user_id),
                    )

                    if update_existing:
                        await cur.execute(
                            f"DELETE FROM `{guild_id}` WHERE author_id = {user_id};"
                        )



    async def remove_ignore(
            self, guild_id: int, channel_id: int = None, user_id: int = None
    ):
        if channel_id is None and user_id is None:
            raise ValueError("channel_id and user_id cannot both be None")

        # Ignore based on channel_id
        if channel_id is not None:
            # Add to database
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "DELETE FROM `config` WHERE _key = 'channel_ignore' AND data1 = %s AND data2 = %s;",
                        (guild_id, channel_id),
                    )

        # Ignore based on user_id
        elif user_id is not None:
            # Add to database
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "DELETE FROM `config` WHERE _key = 'user_ignore' AND data1 = %s AND data2 = %s;",
                        (guild_id, user_id),
                    )

    async def get_ignore_list(self, type_: str, guild_id: int = None) -> dict or list:
        if type_ not in ["channel", "user"]:
            raise ValueError("type_ must be either 'channel' or 'user'")

        if guild_id is not None:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT data1, data2 FROM `config` WHERE _key = %s AND data1 = %s;",
                        (f"{type_}_ignore", guild_id),
                    )

                    # format of res: [(guild_id, channel_id), (guild_id, channel_id), ...]
                    res = await cur.fetchall()

            # convert to this format -
            # [channel_id, channel_id, ...]
            res = [int(channel_id) for _, channel_id in res if _ == guild_id]  # todo check if == guild_id is needed
            return res

        else:
            # get list of the one that is not None
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT data1, data2 FROM `config` WHERE _key = %s;",
                        (f"{type_}_ignore",),
                    )

                    # format of res: [(guild_id, channel_id), (guild_id, channel_id), ...]
                    res = await cur.fetchall()

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

    async def add_user_alias(self, guild_id: int, user_id: int, alias_id: int, update_existing: bool = True):
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT IGNORE INTO `config` (_key, data1, data2, data3) VALUES ('alias', %s, %s, %s);",
                    (guild_id, user_id, alias_id),
                )
                if update_existing:
                    # replace all existing aliases with the new one
                    await cur.execute(
                        f"UPDATE `{guild_id}` SET author_id = {user_id} WHERE author_id = {alias_id};"
                    )

    async def remove_user_alias(self, guild_id: int, user_id: int, alias_id: int):
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM `config` WHERE _key = 'alias' AND data1 = %s AND data2 = %s AND data3 = %s;",
                    (guild_id, user_id, alias_id),
                )

    async def get_user_aliases(self, guild_id: int = None):
        if guild_id is None:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT data1, data2, data3 FROM `config` WHERE _key = 'alias';"
                    )

                    # data1 is guild_id, data2 is user_id, data3 is alias_id

                    res = await cur.fetchall()

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
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT data2, data3 FROM `config` WHERE _key = 'alias' AND data1 = %s;",
                        (guild_id,),
                    )

                    # data2 is user_id, data3 is alias_id

                    res = await cur.fetchall()

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

    async def set_timezone(self, guild_id: int, timezone: int):
        # timezone here is an offset from UTC

        if await self.execute(
                f"SELECT data2 FROM `config` WHERE _key = 'timezone' AND data1 = '%s';",
                (guild_id,), fetch="one"
        ) is None:
            await self.execute(
                "INSERT INTO `config` (_key, data1, data2) VALUES ('timezone', %s, %s);",
                (guild_id, timezone),
            )
            return

        await self.execute(
            "UPDATE `config` SET data2 = %s WHERE _key = 'timezone' AND data1 = %s;",
            (timezone, guild_id),
        )

    async def get_timezone(self, guild_id: int):
        res = await self.execute(f"SELECT data2 FROM `config` WHERE _key = 'timezone' AND data1 = '%s';",
            (guild_id,), fetch="one")

        if res is None:
            return None

        return res[0]



    # analysis functions
    async def get_message_count(
            self, guild_id: int, channel_id: int = None, user_id: int = None
    ):
        if guild_id is None:
            raise ValueError("guild_id cannot be None")

        if channel_id is None and user_id is None:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"SELECT COUNT(*) FROM `{guild_id}`",
                    )

                    return (await cur.fetchone())[0]

        elif channel_id is not None and user_id is None:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"SELECT COUNT(*) FROM `{guild_id}` WHERE channel_id = %s;",
                        (channel_id,),
                    )

                    return (await cur.fetchone())[0]

        elif channel_id is None and user_id is not None:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"SELECT COUNT(*) FROM `{guild_id}` WHERE author_id = %s;",
                        (user_id,),
                    )

                    return (await cur.fetchone())[0]

        else:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"SELECT COUNT(*) FROM `{guild_id}` WHERE channel_id = %s AND author_id = %s;",
                        (channel_id, user_id),
                    )

                    return (await cur.fetchone())[0]

    async def get_mentions(self, guild_id: int, user_id: int) -> list[int]:
        """Returns all the instances where mentions are not empty, where user_id;"""
        if user_id is not None:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"SELECT mentions FROM `{guild_id}` WHERE author_id = %s AND mentions IS NOT NULL;",
                        (user_id,),
                    )

                res = [x[0] for x in await cur.fetchall()]

        # each mention can be a csv; we need to unpack the strings
        data = []
        for mention in res:
            data.extend([int(mention_) for mention_ in mention.split(",")])

        return data

    async def get_all_mentions(self, guild_id: int) -> list[int, list[int]]:
        """Returns all the instances where mentions are not empty along with whom the messages belong to"""
        async with self.con.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"SELECT author_id, mentions FROM `{guild_id}` WHERE mentions IS NOT NULL;",
                )

                res = await cur.fetchall()

        data = []

        for author_id, mentions in res:
            data.extend(
                [int(author_id), [int(mention_) for mention_ in mentions.split(",")]]
            )

        return data

    async def get_message_content(self, guild_id: int, channel_id: int = None, user_id: int = None) -> list[str]:
        if channel_id is None and user_id is None:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"SELECT message_content FROM `{guild_id}` WHERE message_content IS NOT NULL;",
                    )

                    res = await cur.fetchall()

        elif channel_id is not None and user_id is None:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"SELECT message_content FROM `{guild_id}` WHERE channel_id = %s AND message_content IS NOT "
                        f"NULL;",
                        (channel_id,),
                    )

                    res = await cur.fetchall()

        elif channel_id is None and user_id is not None:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"SELECT message_content FROM `{guild_id}` WHERE author_id = %s AND message_content IS NOT NULL;",
                        (user_id,),
                    )

                    res = await cur.fetchall()

        else:
            async with self.con.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"SELECT message_content FROM `{guild_id}` WHERE channel_id = %s AND author_id = %s AND "
                        f"message_content IS NOT NULL;",
                        (channel_id, user_id),
                    )

                    res = await cur.fetchall()

        return [(message_content[0]).decode("utf-8") for message_content in res]
