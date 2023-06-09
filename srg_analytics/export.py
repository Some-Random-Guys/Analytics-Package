import io
import chat_exporter


async def export_html(client, channel, limit: int = None) -> io.BytesIO:
    if limit is None:
        res = await chat_exporter.export(channel, bot=client)
    else:
        res = await chat_exporter.export(channel, limit=limit, bot=client)

    # return virtual file without using discord File class
    return io.BytesIO(res.encode())

