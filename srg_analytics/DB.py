from .schemas import DbCreds, DataTemplate
import mysql.connector as mysql


class DB:
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
                data2 TEXT NULL
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

    async def add_guild(self, guild_id):
        self.cur.execute(
            f"""
                CREATE TABLE IF NOT EXISTS `{guild_id}` (
                message_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                author_id BIGINT NOT NULL,
                message_content BLOB,
                epoch BIGINT NOT NULL,
                is_bot BOOLEAN NOT NULL,                       
                num_attachments SMALLINT NOT NULL DEFAULT 0,
                ctx_id BIGINT,
                mentions TEXT,
                PRIMARY KEY (message_id)
                );
            """
        )

        self.con.commit()

    async def remove_guild(self, guild_id):
        self.cur.execute(
            f"DROP TABLE IF EXISTS `{guild_id}`;"
        )

        self.con.commit()

    async def get_guild(self, guild_id):
        self.cur.execute(
            f"SELECT * FROM `{guild_id}`;"
        )

        return self.cur.fetchall()

    async def get_guilds(self):  # TODO TEST
        self.cur.execute(
            f"SHOW TABLES;"
        )

        return self.cur.fetchall()

    async def add_message(self, guild_id, data: DataTemplate):
        self.cur.execute(
            f"""
                        INSERT IGNORE INTO `{guild_id}` (message_id, channel_id, author_id, message_content, epoch, 
                        is_bot, num_attachments, ctx_id, mentions)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);

                    """,
            (
                data.message_id,
                data.channel_id,
                data.author_id,
                data.message_content,
                data.epoch,
                data.is_bot,
                data.num_attachments,
                data.ctx_id,
                data.mentions,
            ),
        )

        self.con.commit()

    async def delete_message(self, guild_id: int, message_id: int):
        self.cur.execute(f"DELETE FROM `{guild_id}` WHERE message_id = {message_id};")
        self.con.commit()

    async def add_ignore(self, guild_id: int, channel_id: int = None, user_id: int = None):
        if channel_id is None and user_id is None:
            raise ValueError("channel_id and user_id cannot both be None")

        # Ignore based on channel_id
        if channel_id is not None:

            # Add to database
            self.cur.execute(
                f"INSERT IGNORE INTO `config` (_key, data1, data2) VALUES ('channel_ignore', ?, ?);",
                (guild_id, channel_id,)
            )

            self.con.commit()

        # Ignore based on user_id
        elif user_id is not None:

            # Add to database
            self.cur.execute(
                f"INSERT IGNORE INTO `config` (_key, data1, data2) VALUES ('user_ignore', ?, ?);",
                (guild_id, user_id,)
            )

            self.con.commit()

    async def remove_ignore(self, guild_id: int, channel_id: int = None, user_id: int = None):
        if channel_id is None and user_id is None:
            raise ValueError("channel_id and user_id cannot both be None")

        # Ignore based on channel_id
        if channel_id is not None:
            # Add to database
            self.cur.execute(
                f"DELETE FROM `config` WHERE _key = 'channel_ignore' AND data1 = ? AND data2 = ?;",
                (guild_id, channel_id,)
            )

        # Ignore based on user_id
        elif user_id is not None:
            # Add to database
            self.cur.execute(
                f"DELETE FROM `config` WHERE _key = 'user_ignore' AND data1 = ? AND data2 = ?;",
                (guild_id, user_id,)
            )

        self.con.commit()

    async def get_ignore_list(self, type_: str, guild_id: int = None) -> dict or list:
        if type_ not in ["channel", "user"]:
            raise ValueError("type_ must be either 'channel' or 'user'")

        if guild_id is not None:
            self.cur.execute(
                f"SELECT data1, data2 FROM `config` WHERE _key = ? AND data1 = ?;", (f"{type_}_ignore", guild_id)
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
                f"SELECT data1, data2 FROM `config` WHERE _key = ?;", (f"{type_}_ignore",)
            )

            # format of res: [(guild_id, channel_id), (guild_id, channel_id), ...]
            res = self.cur.fetchall()

            # convert to this format -
            # {
            #   guild_id: [channel_id, channel_id, ...],
            #   guild_id: [channel_id, channel_id, ...], ...
            # }
            res = {int(guild_id): [int(channel_id) for _, channel_id in res if _ == guild_id] for guild_id, _ in res}
            return res
