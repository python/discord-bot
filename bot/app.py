import discord
import tiktoken
from discord.ext import commands

from conf import DISCORD_TOKEN
from cache import SimpleTTLCache
from misc import get_logger
from util_meta import get_gh_discuss, get_pep_text
from util_openai import text_to_chunks, send_partial_text, summarize


logger = get_logger(__name__)
intents = discord.Intents.default()
intents.message_content = True
cache = SimpleTTLCache(100)
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user.name}({bot.user.id})")


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("pong")


@bot.command(name="tldr")
async def tldr(ctx, target: str, number: int):
    requester = ctx.message.author
    logger.info(f"requester: {requester}, target: {target}, number: {number}")
    target = target.lower()
    if target not in ["pep", "gh"]:
        await ctx.send("Only supports PEP and GitHub right now.")
        return
    try:
        target_doc = f"{target}-{number:04d}"
        cached_result = cache.get(target_doc)
        author = ctx.message.author
        if cached_result:
            await ctx.send(f"{author.mention} Here you go:\n{cached_result}")
            return
        if target == "pep":
            text = await get_pep_text(target_doc)
            link = f"https://peps.python.org/{target_doc}"
        else:
            text = await get_gh_discuss(number)
            link = f"https://github.com/python/cpython/issues/{number}"
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        responses = []
        for chunk in text_to_chunks(encoding, text):
            decoded_text = encoding.decode(chunk)
            res = await send_partial_text(decoded_text, target_doc)
            responses.append(res)

        summary = await summarize(link, responses)
        # Caching for 10 mins
        cache.put(target_doc, summary, 60 * 10)
        await ctx.send(f"{author.mention} Here you go:\n{summary}")
    except Exception as e:
        logger.error("An exception was thrown!", exc_info=True)
        await ctx.send(f"Error: {e}")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
