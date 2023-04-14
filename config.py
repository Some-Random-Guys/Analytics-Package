from chromadb.config import Settings
from pydantic import BaseModel

settings = Settings(
    chroma_db_impl='duckdb+parquet',
    persist_directory='./data/chroma/'
)


class DataTemplate(BaseModel):
    author_id: list[str or int]
    author_name: list[str]
    is_bot: list[bool]
    has_embed: list[bool]
    channel_id: list[str or int]
    timestamp: list[str]
    num_attachments: list[str or int]
    mentions: list[list[str or int]]
    context: list[str]
    message_content: list[str or None]
    message_id: list[str or int]
