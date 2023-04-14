import copy
import fastapi
import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse

from backend import *

error_response = {
    "http_status": 500,
    "error": "Internal Server Error"
}

success_response = {
    "http_status": 200,
    "data": None
}

app = FastAPI(
    title="SRG Analytics API",
    description="An API which acts as the backend for a SRG Analytics Discord bot.",
    version="1.0.0",
)

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
    # noinspection PyTypedDict
    return_list["data"] = "Welcome to the API. Please refer to the documentation " \
    return return_list