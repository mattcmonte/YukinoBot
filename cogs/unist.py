import discord
from discord.ext import commands
from discord import errors


PATH = '/home/matt/Documents/Projects/YukinoBot/cogs'

moves = {
    'grim reaper': f'{PATH}/grimreapah.gif'
}


class Unist(commands.Cog):
    """ A module with commands related to various fighting games.
    
    Methods:
    attack -- outputs a GIF of a character's attack and mentions a user
    """

    def __init__(self, bot):
        self.bot = bot   

    @commands.command()
    async def attack(self, ctx, victim: discord.Member, *name_of_move):
        """Outputs a GIF of a character's attack and mentions a user.

        Keyword Arguments:
        ctx             -- discord context object
        victim          -- the name of the user to be mentioned
        name_of_move    -- the name of an attack
        """
        if victim is None:
            await ctx.send('No user found with that name1111')
        else:
            mentions = [
                member.id for member in ctx.guild.members
            ]
            if victim.id != ctx.author.mention and victim.id in mentions:
                name_of_move = ' '.join(name_of_move)
                if name_of_move in moves.keys():
                    await ctx.send(
                        f'{victim.mention} was killed by'
                        f' {ctx.author.display_name}',
                        file=discord.File(moves[name_of_move])
                    )
                else:
                    await ctx.send('Name of move not found.')
            else:
                await ctx.send('You can\'t attack yourself.')

    @attack.error
    async def attack_error(self, ctx, error):
        """A function which handles errors thrown by the attack function.

        Keyword Arguments:
        ctx   -- discord context object
        error -- a discord exception object 
        """
        if isinstance(error, commands.BadArgument):
            await ctx.send("No user found with that name")

        
def setup(bot):
    bot.add_cog(Unist(bot))