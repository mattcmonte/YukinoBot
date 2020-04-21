import discord
from discord.ext import commands


class Admin(commands.Cog):
    """A module with administrative commands."""
    def __init__(self, bot):
        self.bot = bot 

    @commands.command(aliases=['delete', 'purge', 'remove'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, *, amount=None):
        """Deletes the number of messages specified or 50 if not specified.
        
        Keyword Arguments:
        ctx    -- discord context object
        amount -- the amount of messages to be deleted
        """ 
        if amount is None:
            amount = '50'
        if amount.isdigit():
            amount = int(amount)
            messages = await ctx.channel.history(limit=amount+1).flatten()
            try:
                await ctx.channel.delete_messages(messages)
            except errors.HTTPException:
                await ctx.send(
                    'One or more of the messages you tried to bulk delete'
                    ' were too old. They must be under 14 days old or else'
                    ' I can\'t delete them.'
                ) 
            except errors.ClientException:
                await ctx.send(
                    'I can\'t delete more than 100 messages at once.'
                )
        else:
            await ctx.send(
                'Invalid number specified. Must be a positive integer.'
            )

    @clear.error
    async def clear_error(self, ctx, error):
        """A function which handles errors thrown by the clear function.

        Keyword Arguments:
        ctx   -- discord context object
        error -- a discord exception object 
        """
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to delete messages.")


def setup(bot):
    bot.add_cog(Admin(bot))