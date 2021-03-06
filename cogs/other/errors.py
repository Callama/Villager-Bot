import async_cse
import discord
import traceback
from discord.ext import commands
from random import choice


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send(self, ctx, msg):
        try:
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=msg))
        except discord.errors.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, e):
        try:
            if ctx.handled is None:
                ctx.handled = False
        except AttributeError:
            ctx.handled = False

        if isinstance(e, commands.errors.NoPrivateMessage):
            await self.send(ctx, "This command can't be used in private chat channels.")
            return

        if isinstance(e, commands.MissingPermissions):
            await self.send(ctx, choice(["Nice try stupid, but you don't have the permissions to do that.", "Oops, looks like you don't have the permissions to do that, dum dum."]))
            return

        if isinstance(e, commands.CheckAnyFailure):
            if "MissingPermissions" in str(e.errors):  # yes I know this is jank but it works so shhhh
                await self.send(ctx, "Nice try stupid, but you don't have the permissions to do that.")
                return

        if isinstance(e, commands.BotMissingPermissions):
            await self.send(ctx, "You didn't give me proper the permissions to do that, stupid.")
            return

        if isinstance(e, async_cse.APIError):
            await self.send(ctx,
                            "Uh Oh! It looks like our search command is having a problem, sorry. Please try again later!")
            return

        # Commands to ignore
        for _type in [commands.CommandNotFound, commands.NotOwner, commands.CheckFailure, discord.errors.Forbidden]:
            if isinstance(e, _type):
                return

        if isinstance(e, commands.MaxConcurrencyReached):
            await self.send(ctx, "Hold on! You're using that command way too fast...")
            return

        if isinstance(e, commands.CommandOnCooldown):
            if not str(ctx.command) in ["mine"]:
                seconds = round(e.retry_after, 2)
                if seconds == 0:
                    await ctx.reinvoke()
                    return

                hours = int(seconds / 3600)
                minutes = int(seconds / 60) % 60
                seconds -= hours * 60 * 60
                seconds -= minutes * 60
                seconds = round(seconds, 2)

                time = ""
                if hours > 0:
                    time += f"{hours} hours, "
                if minutes > 0:
                    time += f"{minutes} minutes, "
                time += f"{seconds} seconds"
                descs = [
                    "Didn't your parents tell you [patience is a virtue](http://www.patience-is-a-virtue.org/)? Calm down and wait another {0}.",
                    "Hey, you need to wait another {0} before doing that again.",
                    "Hrmmm, looks like you need to wait another {0} before doing that again.",
                    "Don't you know [patience is a virtue](http://www.patience-is-a-virtue.org/)? {0}."]
                await self.send(ctx, choice(descs).format(time))
            return
        else:
            ctx.command.reset_cooldown(ctx)

        if isinstance(e, commands.errors.MissingRequiredArgument):
            await self.send(ctx, "HRMMM, looks like you're forgetting to put something in!")
            return

        if isinstance(e, commands.BadArgument) or isinstance(e, commands.errors.ExpectedClosingQuoteError):
            await self.send(ctx, "Looks like you typed something wrong, try typing it correctly the first time, idiot.")
            return

        if "error code: 50013" in str(e):
            await self.send(ctx, "I can't do that, you idiot.")
            return

        if "HTTPException: 503 Service Unavailable (error code: 0)" not in str(
                e) and "discord.errors.Forbidden" not in str(e):
            excls = ['OH SNAP', 'OH FU\*\*!', 'OH \*\*\*\*!', 'OH SH-']
            await self.send(ctx, f"{choice(excls)} "
                                 "You found an actual error, please take a screenshot and report it on our "
                                 "**[support server](https://discord.gg/39DwwUV)**, thank you!")

            error_channel = self.bot.get_channel(642446655022432267)

            # Thanks TrustedMercury!
            etype = type(e)
            trace = e.__traceback__
            verbosity = 1
            lines = traceback.format_exception(etype, e, trace, verbosity)
            traceback_text = ''.join(lines)

            final = f"{ctx.author}: {ctx.message.content}\n\n{traceback_text}"
            await self.send(error_channel, f"```{final[:2047-6]}```")


def setup(bot):
    bot.add_cog(Errors(bot))
