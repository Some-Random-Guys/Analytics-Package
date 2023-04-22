from chromadb.config import Settings
from pydantic import BaseModel

# The config for the chroma database
# Use the below (default) if you don't have a separate chroma database
settings = Settings(
    chroma_db_impl='rest',
    persist_directory='./data/chroma/'
)

# If you have a separate chroma database, use the below config
"""
settings = Settings(
    chroma_api_impl="rest",
    chroma_server_host='localhost',
    chroma_server_http_port='1234',
)
"""


class DataTemplate(BaseModel):
    author_id: list[str or int]
    is_bot: list[bool]
    has_embed: list[bool]
    channel_id: list[str or int]
    timestamp: list[str]
    num_attachments: list[str or int]
    mentions: list[list[str or int]]
    context: list[str]
    message_content: list[str or None]
    message_id: list[str or int]


api_keys = {
    "view": ['123'],
    "edit": ['123'],
    "admin": ['123']
}

