import copy
import logging

import requests
from fastapi import Depends
import fastapi.security
from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse

import backend.db_manager as db_manager
from config import DataTemplate, api_keys

from backend.logging_ import log

success_response = {
    "http_status": 200,
}

app = FastAPI(
    title="SRG Analytics API",
    description="An API which acts as the backend for a SRG Analytics Discord bot.",
    version="1.0.0",
    docs_url="/docs",
    root_path="/v1"

)

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="token")  # use token authentication


def check_key(api_key, level):
    print(api_key)
    if api_key in api_keys[level] or api_key in api_keys['admin']:
        return True
    else:
        return False


def view_api_auth(api_key: str = Depends(oauth2_scheme)):
    if not check_key(api_key, 'view'):
        raise HTTPException(status_code=401)


def edit_api_auth(api_key: str = Depends(oauth2_scheme)):
    if not check_key(api_key, 'edit'):
        raise HTTPException(status_code=401)


def admin_api_auth(api_key: str = Depends(oauth2_scheme)):
    if not check_key(api_key, 'admin'):
        raise HTTPException(status_code=401)


#
#   Exception Handlers
#

@app.exception_handler(500)
async def handler_500(err, e):
    return JSONResponse(status_code=500, content={"http_status": 500, "error": "Internal Server Error"})


@app.exception_handler(401)
async def handler_401(err, e):
    return JSONResponse(status_code=401, content={"http_status": 401, "error": "Unauthorized"})


@app.exception_handler(404)
async def handler_404(err, e):
    return JSONResponse(status_code=404, content={"http_status": 404, "error": "Not Found"})


@app.get("/")
async def root():
    return_list = copy.deepcopy(success_response)

    return_list["data"] = "Welcome to the API. Please refer to the documentation "
    return return_list


#
#   Method Bindings: ./backend/db_manager.py
#

@app.get("/db/guilds", dependencies=[Depends(view_api_auth)])
async def get_all_guids():
    return_list = copy.deepcopy(success_response)
    return_list["data"] = db_manager.get_all_guids()
    return return_list


@app.post("/db/guilds", dependencies=[Depends(edit_api_auth)])
async def add_guild(guild_id: int):
    return_list = copy.deepcopy(success_response)

    try:
        return_list["data"] = db_manager.add_guild(guild_id)
    except requests.exceptions.HTTPError:
        return JSONResponse(status_code=409, content={"http_status": 409, "error": "Guild already exists"})
    return return_list


@app.delete("/db/guilds/{guild_id}", dependencies=[Depends(edit_api_auth)])
async def remove_guild(guild_id: int):
    return_list = copy.deepcopy(success_response)

    try:
        return_list["data"] = db_manager.remove_guild(guild_id)
    except ValueError:
        raise HTTPException(status_code=404)
    return return_list


@app.get("/db/guilds/{guild_id}", dependencies=[Depends(view_api_auth)])
async def get_guild(guild_id: int):
    return_list = copy.deepcopy(success_response)

    try:
        resp = db_manager.get_guild(guild_id)
    except ValueError:
        raise HTTPException(status_code=404)

    return_list["data"] = resp
    return return_list


@app.post("/db/guilds/{guild_id}/purge", dependencies=[Depends(edit_api_auth)])
async def purge_guild(guild_id: int):
    return_list = copy.deepcopy(success_response)

    try:
        return_list["data"] = db_manager.purge_guild(guild_id)
    except ValueError:
        raise HTTPException(status_code=404)
    return return_list


@app.post("/db/guilds/{guild_id}", dependencies=[Depends(edit_api_auth)])
async def add_data(guild_id: int, data: DataTemplate):
    return_list = copy.deepcopy(success_response)

    try:
        db_manager.add_data(guild_id, data)
    except ValueError:
        raise HTTPException(status_code=404)
    return return_list


@app.get("/db/guilds/{guild_id}/messages/{author_id}", dependencies=[Depends(view_api_auth)])
async def get_data(guild_id: int, author_id: int = None):
    return_list = copy.deepcopy(success_response)
    try:
        if author_id is None:
            return_list["data"] = db_manager.get_all_messages_from_guild(guild_id)
        else:
            return_list["data"] = db_manager.get_all_messages_from_user(guild_id, author_id)
    except ValueError:
        raise HTTPException(status_code=404)
    return return_list


@app.get("/db/guilds/{guild_id}/top/words/{author_id}/{amount}", dependencies=[Depends(view_api_auth)])
async def get_top_words(guild_id: int, author_id: int = None, amount: int = 10):
    return_list = copy.deepcopy(success_response)

    if author_id is None:
        return_list["data"] = db_manager.top_n_words(guild_id, amount)
    else:
        return_list["data"] = db_manager.top_n_words_user(guild_id, author_id, amount)
    return return_list


@app.get("/db/guilds/{guild_id}/mentions/{author_id}", dependencies=[Depends(view_api_auth)])
async def get_total_mentions(guild_id: int, author_id: int):
    return_list = copy.deepcopy(success_response)
    return_list["data"] = db_manager.total_mentions_by_author(guild_id, author_id)
    return return_list


@app.get("/db/guilds/{guild_id}/top/mentions/{author_id}/{amount}", dependencies=[Depends(view_api_auth)])
async def get_top_mentions(guild_id: int, author_id: int, amount: int = 10):
    return_list = copy.deepcopy(success_response)
    return_list["data"] = db_manager.top_mentions_by_author(guild_id, author_id, amount)
    return return_list


@app.get("/db/guilds/{guild_id}/mentioned/{author_id}", dependencies=[Depends(view_api_auth)])
async def get_total_mentioned(guild_id: int, author_id: int):
    return_list = copy.deepcopy(success_response)
    return_list["data"] = db_manager.total_mentioned_by(guild_id, author_id)
    return return_list


@app.get("/db/guilds/{guild_id}/top/mentioned/{author_id}/{amount}", dependencies=[Depends(view_api_auth)])
async def get_top_mentioned(guild_id: int, author_id: int, amount):
    return_list = copy.deepcopy(success_response)
    return_list["data"] = db_manager.top_mentioned_by(guild_id, author_id, amount)
    return return_list


@app.get("/db/guilds/{guild_id}/message_count/{author_id}", dependencies=[Depends(view_api_auth)])
async def get_message_count(guild_id: int, author_id: int = None):
    return_list = copy.deepcopy(success_response)
    if author_id is None:
        return_list["data"] = db_manager.guild_message_count(guild_id)
    else:
        return_list["data"] = db_manager.user_message_count(guild_id, author_id)

    return return_list


@app.get("/db/guilds/{guild_id}/top/channels/{amount}/{author_id}", dependencies=[Depends(view_api_auth)])
async def get_top_channels(guild_id: int, author_id: int = None, amount: int = 10):
    return_list = copy.deepcopy(success_response)

    if author_id is None:
        return_list["data"] = db_manager.top_n_channels(guild_id, amount)
    else:
        return_list["data"] = db_manager.top_n_channels_user(guild_id, author_id, amount)
    return return_list


@app.get("/db/guilds/{guild_id}/top/emojis/{amount}/{author_id}", dependencies=[Depends(view_api_auth)])
async def get_top_emojis(guild_id: int, author_id: int = None, amount: int = 10):
    # TODO backend is not ready yet
    pass


@app.get("/db/guilds/{guild_id}/top/users/{type}/{amount}", dependencies=[Depends(view_api_auth)])
async def get_top_users(guild_id: int, type_: str, amount: int = 10):
    if type_ not in ["messages", "words", "characters"]:
        raise HTTPException(status_code=400, detail="Invalid type.")

    return_list = copy.deepcopy(success_response)

    return_list["data"] = db_manager.top_n_users(guild_id, type_, amount)

    return return_list


@app.delete("/db/guilds", dependencies=[Depends(admin_api_auth)])
async def clear_db():
    return_list = copy.deepcopy(success_response)

    db_manager.clear_db()

    return return_list
