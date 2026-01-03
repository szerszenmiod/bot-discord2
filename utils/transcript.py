import aiofiles, datetime, html

async def save_transcript(channel):
    msgs = [m async for m in channel.history(limit=None, oldest_first=True)]
    content = [
        f"<html><head><meta charset=\"utf-8\"><title>{channel.name}</title></head><body>",
        f"<h1>Transcript {channel.name}</h1>"
    ]
    for m in msgs:
        ts = m.created_at.astimezone(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        content.append(
            f"<p><strong>{html.escape(str(m.author))}</strong> [{ts}]<br/>{html.escape(m.content or '<attachment>')}</p>"
        )
    content.append("</body></html>")
    path = f"transcripts/{channel.name}.html"
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write("\n".join(content))
    return path
