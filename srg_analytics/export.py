import io
import chat_exporter


async def export_html(client, channel, limit: int = None) -> io.BytesIO:
    res = await chat_exporter.export(channel, bot=client, limit=limit)

    # return virtual file without using discord File class
    return io.BytesIO(res.encode())

