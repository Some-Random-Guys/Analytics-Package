class DbCreds:
    def __init__(self, host, port, user, password, name):
        self.host = host
        self.port: int = port
        self.user = user
        self.password = password
        self.name = name


class Message:
    def __init__(
        self,
        guild_id,
        message_id,
        channel_id,
        author_id,
        aliased_author_id,
        message_content,
        epoch,
        edit_epoch,
        is_bot,
        has_embed,
        num_attachments,
        ctx_id,
        user_mentions,
        channel_mentions,
        role_mentions,
        reactions
    ):
        self.guild_id: int = guild_id
        self.message_id: int = message_id
        self.channel_id: int = channel_id
        self.author_id: int = author_id
        self.aliased_author_id: int = aliased_author_id
        self.message_content: str or None = message_content
        self.epoch: int = epoch
        self.edit_epoch: int or None = edit_epoch
        self.is_bot: bool = is_bot
        self.has_embed: bool = has_embed
        self.num_attachments: int = num_attachments
        self.ctx_id = ctx_id
        self.user_mentions = user_mentions
        self.channel_mentions = channel_mentions
        self.role_mentions = role_mentions
        self.reactions = reactions


class Profile:
    def __init__(self) -> None:
        # Discord IDs
        self.user_id: int = None
        self.guild_id: int = None

        # Message data
        self.messages = None
        self.top_words = []
        self.top_emojis = []

        # channel
        self.most_active_channel = None

        # mentions
        self.total_mentions = None

        self.most_mentioned = None
        self.no_of_times_most_mentioned = None

        self.most_mentioned_by = None
        self.no_of_times_most_mentioned_by = None

        # time
        self.most_active_hour = None
        self.most_active_day = None

