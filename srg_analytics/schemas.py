class DbCreds:
    def __init__(self, host, port, user, password, name):
        self.host = host
        self.port: int = port
        self.user = user
        self.password = password
        self.name = name


class DataTemplate:
    def __init__(self, author_id, is_bot, has_embed, channel_id, epoch, num_attachments, mentions, ctx_id,
                 message_content, message_id):
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

