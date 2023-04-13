from backend.logging_ import log


class Profile:
    def __init__(self, guild_id: int, id_: int, no_of_messages: int, top_2_words: list, net_polarity: int,
                 most_mentioned_channels: list,
                 total_mentions: int, most_mentioned_person_id: int, total_times_mentioned: int,
                 most_mentioned_by_id: int, most_mentioned_by_id_no: int,
                 active_channel: int) -> None:
        self.guildID = guild_id  # to be removed in the future
        self.ID = id_

        # NLP
        self.no_of_messages = no_of_messages
        self.top_2_words = top_2_words
        self.net_polarity = net_polarity
        self.most_mentioned_channels = most_mentioned_channels

        # Mentions
        self.total_mentions = total_mentions
        self.most_mentioned_person_id = most_mentioned_person_id
        self.total_times_mentioned = total_times_mentioned
        self.most_mentioned_by_id = most_mentioned_by_id
        self.most_mentioned_by_id_no = most_mentioned_by_id_no

        # Channels
        self.active_channel = active_channel

    def __dict__(self):
        return {
            "guildID": self.guildID,
            "ID": self.ID,
            "number_of_messages": self.no_of_messages,
            "top_2_words": self.top_2_words,
            "net_polarity": self.net_polarity,
            "most_mentioned_channels": self.most_mentioned_channels,
            "total_mentions": self.total_mentions,
            "most_mentioned_person_id": self.most_mentioned_person_id,
            "total_times_mentioned": self.total_times_mentioned,
            "most_mentioned_by_id": self.most_mentioned_by_id,
            "most_mentioned_by_id_no": self.most_mentioned_by_id_no,
            "active_channel": self.active_channel
        }

    def __str__(self):
        return str(self.__dict__())