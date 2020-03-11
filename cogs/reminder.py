import asyncio

from discord.ext import commands
from discord import errors
import discord


class Reminder:
    """ A module that allows you to create reminders."""
    
    accepted_units = ['hours', 'hour', 'minutes', 'minute', 'seconds', 'second', 'days', 'day']
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['timer'])
    async def create_reminder(self, ctx, *,
                              requested_time=None):
        """ 
        This is the create_reminder command. It takes in a string with the requested duration  
        
        Accepted format examples:
        '2 hours'
        '3 minutes'
        '4 days'
        '57 seconds'
        """
            
        try:
            time, unit = requested_time.split()
        except:
            await ctx.send('Bad time format. Please format times this way: example: 2 hours')
        
        if unit in accepted_units:
            if unit == 'hour' or 'hours':
                try:
                    time = time * 60 * 60
        else:
            await ctx.send(f'You gave me an unaccpeted unit of time, the accepted units are: {[x for x in accepted_units]}')
            
        
            
    
    
    
        
    



def setup(bot):
    bot.add_cog(Reminder(bot))
