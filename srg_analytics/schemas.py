class DbCreds:
    def __init__(self, host, port, user, password, name):
        self.host = host
        self.port: int = port
        self.user = user
        self.password = password
        self.name = name


class DataTemplate:
    def __init__(
        self,
        author_id,
        is_bot,
        has_embed,
        channel_id,
        epoch,
        num_attachments,
        mentions,
        ctx_id,
        message_content,
        message_id,
    ):
        self.message_id: int = message_id
        self.channel_id: int = channel_id
        self.author_id: int = author_id
        self.message_content: str or None = message_content
        self.epoch: int = epoch
        self.is_bot: bool = is_bot
        self.has_embed: bool = has_embed
        self.num_attachments: int = num_attachments
        self.ctx_id = ctx_id
        self.mentions = mentions


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

