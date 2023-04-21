import copy
from fastapi import Depends
import fastapi.security
from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse

import backend.db_manager as db_manager
from config import DataTemplate, api_keys

success_response = {
    "http_status": 200,
}

app = FastAPI(
    title="SRG Analytics API",
    description="An API which acts as the backend for a SRG Analytics Discord bot.",
    version="1.0.0",
)


#
#   Exception Handlers
#

@app.exception_handler(500)
async def handler_500(err, e):
    error_content = copy.deepcopy(error_response)
    error_content["error"] = str(err)
    return JSONResponse(content=error_content, status_code=500)


@app.exception_handler(404)
async def handler_404(err, e):
    error_content = copy.deepcopy(error_response)
    error_content['http_status'] = 404
    error_content["error"] = "Not Found"
    return JSONResponse(content=error_content, status_code=404)


@app.get("/")
async def root():
    return_list = copy.deepcopy(success_response)

    return_list["data"] = "Welcome to the API. Please refer to the documentation "
    return return_list


#
#   Method Bindings: ./backend/db_manager.py
#

@app.get("/db/get_all_guilds")
async def heartbeat():
    return_list = copy.deepcopy(success_response)

    return_list["data"] = db_manager.heartbeat()
    return return_list


@app.post("/db/{guild_id}/add")
async def add_guild(guild_id: int):
    return_list = copy.deepcopy(success_response)

    return_list["data"] = db_manager.add_guild(guild_id)
    return return_list


@app.delete("/db/{guild_id}")
async def remove_guild(guild_id: int):
    return_list = copy.deepcopy(success_response)

    return_list["data"] = db_manager.remove_guild(guild_id)
    return return_list


@app.get("/db/{guild_id}")
async def get_guild(guild_id: int):
    return_list = copy.deepcopy(success_response)

    return_list["data"] = db_manager.get_guild(guild_id)
    return return_list


@app.post("/db/{guild_id}/purge")
async def purge_guild(guild_id: int):
    return_list = copy.deepcopy(success_response)

    return_list["data"] = db_manager.purge_guild(guild_id)
    return return_list


@app.post("/db/{guild_id}/add_data")
async def add_data(guild_id: int, data: DataTemplate):
    return_list = copy.deepcopy(success_response)

    db_manager.add_data(guild_id, data)
    return return_list


@app.get("/db/{guild_id}/get_data/{author_id}")
async def get_data(guild_id: int, author_id: int = None):
    return_list = copy.deepcopy(success_response)

    if author_id is None:
        return_list["data"] = db_manager.get_all_messages_from_guild(guild_id)
    else:
        return_list["data"] = db_manager.get_all_messages_from_user(guild_id, author_id)
    return return_list


@app.get("/db/{guild_id}/top/words/{amount}/{author_id}")
async def get_top_words(guild_id: int, author_id: int = None, amount: int = 10):
    return_list = copy.deepcopy(success_response)

    if author_id is None:
        return_list["data"] = db_manager.top_n_words(guild_id, amount)
    else:
        return_list["data"] = db_manager.top_n_words_user(guild_id, author_id, amount)
    return return_list


@app.get("/db/{guild_id}/mentions/{author_id}")
async def get_top_mentions(guild_id: int, author_id: int):
    return_list = copy.deepcopy(success_response)
    return_list["data"] = db_manager.total_mentions_by_author(guild_id, author_id)
    return return_list


@app.get("/db/{guild_id}/mentions/{author_id}/{amount}")
async def get_top_mentions(guild_id: int, author_id: int, amount: int = 10):
    return_list = copy.deepcopy(success_response)
    return_list["data"] = db_manager.top_mentions_by_author(guild_id, author_id, amount)
    return return_list


@app.get("/db/{guild_id}/mentioned/{author_id}")
async def get_top_mentioned(guild_id: int, author_id: int):
    return_list = copy.deepcopy(success_response)
    return_list["data"] = db_manager.total_mentioned_by(guild_id, author_id)
    return return_list


@app.get("/db/{guild_id}/mentioned/{author_id}/{amount}")
async def get_top_mentioned(guild_id: int, author_id: int, amount):
    return_list = copy.deepcopy(success_response)
    return_list["data"] = db_manager.top_mentioned_by(guild_id, author_id, amount)
    return return_list


@app.get("/db/{guild_id}/message_count/{author_id}")
async def get_message_count(guild_id: int, author_id: int = None):
    return_list = copy.deepcopy(success_response)
    if author_id is None:
        return_list["data"] = db_manager.guild_message_count(guild_id)
    else:
        return_list["data"] = db_manager.user_message_count(guild_id, author_id)

    return return_list


@app.get("/db/{guild_id}/top/channels/{amount}/{author_id}")
async def get_top_channels(guild_id: int, author_id: int = None, amount: int = 10):
    return_list = copy.deepcopy(success_response)

    if author_id is None:
        return_list["data"] = db_manager.top_n_channels(guild_id, amount)
    else:
        return_list["data"] = db_manager.top_n_channels_user(guild_id, author_id, amount)
    return return_list


@app.get("/db/{guild_id}/top/emojis/{amount}/{author_id}")
async def get_top_emojis(guild_id: int, author_id: int = None, amount: int = 10):
    # TODO backend is not ready yet
    pass


@app.get("/db/{guild_id}/top/users/{type}/{amount}")
async def get_top_users(guild_id: int, type_: str, amount: int = 10):
    if type_ not in ["messages", "words", "characters"]:
        return_list = copy.deepcopy(error_response)
        return_list["data"] = "Invalid type. Please refer to the documentation."
        return return_list

    return_list = copy.deepcopy(success_response)

    return_list["data"] = db_manager.top_n_users(guild_id, type_, amount)

    return return_list
