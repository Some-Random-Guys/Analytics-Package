class Profile:
    def __init__(self) -> None:
        # id; discord things
        self.user_id = None
        self.guild_id = None

        ## self.rank = None

        # messages
        self.messages = None
        self.top_words = []
        self.top_emojis = [] 

        ## self.messages_deleted = None
        ## self.messages_edited = None
        ## self.top_characters = []
        ## self.top_phrases = []

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

        # roles