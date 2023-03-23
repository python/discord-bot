import discord
import tiktoken
from discord.ext import commands

from conf import DISCORD_TOKEN
from cache import SimpleTTLCache
from misc import get_logger
from util_openai import get_pep_text, text_to_chunks, send_partial_text, summarize


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
    if target.lower() != "pep":
        await ctx.send("Only supports PEP right now.")
        return
    try:
        target_pep = f"pep-{number:04d}"
        cached_result = cache.get(target_pep)
        author = ctx.message.author
        if cached_result:
            await ctx.send(f"{author.mention} Here you go:\n{cached_result}")
            return
        pep_text = await get_pep_text(target_pep)
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        responses = []
        for chunk in text_to_chunks(encoding, pep_text):
            text = encoding.decode(chunk)
            res = await send_partial_text(text, target_pep)
            responses.append(res)

        summary = await summarize(target_pep, responses)
        # Caching for 10 mins
        cache.put(target_pep, summary, 60 * 10)
        await ctx.send(f"{author.mention} Here you go:\n{summary}")
    except Exception as e:
        logger.error("An exception was thrown!", exc_info=True)
        await ctx.send(f"Error: {e}")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
