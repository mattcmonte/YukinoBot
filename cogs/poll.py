import json

import discord
from discord.ext import commands
from discord import errors

from cogs.extra_funcs import duplicate_count
from cogs.extra_funcs import dump_poll_data
from cogs.extra_funcs import load_poll_data
from cogs.extra_funcs import generate_hex_int
from cogs.extra_funcs import get_next_index
from cogs.extra_funcs import remove_whitespace

polls = load_poll_data()


class Poll(commands.Cog):
    """A module with administrative commands."""
    def __init__(self, bot):
        self.bot = bot 
    
    # Helper Coroutines:

    async def create_poll_embed(self, poll_dict):
        """Returns a discord embed object containing poll data.
        
        Keyword Arguments:
        poll_dict -- dictionary containing poll data
        """
        poll_embed = discord.Embed(
            title=poll_dict['name'], 
            colour=generate_hex_int()
        )
        poll_embed.add_field(
            name='Participants:',
            value=poll_dict['participant_count'],
            inline=False
        )
        for dictionary in poll_dict['poll_options']:
            poll_embed.add_field(
                name=f'{dictionary["index"]} - {dictionary["option"]}',
                value=f'Votes: {len(dictionary["voters"])}',
                inline=False
            )
        return poll_embed

    async def get_user_input(self, sender):
        """Checks if a specific member sent a specific message.
        
        Keyword Arguments:
        sender -- the name of the sender
        """
        def check_author(message):
            return message.author == sender

        user_input = await self.bot.wait_for(
            'message',
            check=check_author
        )  
        return user_input

    async def search_poll(self, poll_name):
        """Returns a dictionary of poll data or False if not found.
        
        Keyword Arguments:
        poll_name -- a discord message object
        """
        poll = False
        dup_count = duplicate_count(polls, poll_name)

        # If the poll exists
        if dup_count == 1: 
            for poll_dict in polls:
                if poll_dict['name'] == poll_name.content:
                    poll = poll_dict
        return poll

    async def validate_poll_name(self, ctx, polls, poll_name, sender):
        """Returns a valid poll name.
        
        Keyword Arguments:
        ctx       -- discord context object
        polls     -- a list of dictionaries
        poll_name -- the name of a poll
        sender    -- the name of the sender
        """
        dup_count = duplicate_count(polls, poll_name)
            
        while dup_count >= 1:
            await ctx.send(
                'A poll with this name already exists.'
                ' Enter a different name.'
            )
            poll_name = await self.get_user_input(sender)

            dup_count = duplicate_count(polls, poll_name)
        return poll_name

    async def validate_poll_opts(self, ctx, poll_options, sender):
        """Returns a valid list of poll options.
        
        Keyword Arguments:
        ctx          -- discord context object
        poll_options -- a list of poll options
        sender       -- the name of the sender
        """
        while True:
            if '' not in set(poll_options) and len(set(poll_options)) > 1:
                break
            else:
                await ctx.send(
                    'There must be more than one option and none of the'
                    ' options can be blank. Duplicates are automatically'
                    ' removed.'
                )
            poll_options = await self.get_user_input(sender)
            poll_options = remove_whitespace(poll_options.content.split(','))
        return list(set(poll_options))

    # Commands:

    @commands.command()
    async def show_polls(self, ctx):
        """A command which allows a user to show all polls."""
        for poll_dict in polls:
            await ctx.send(embed=await self.create_poll_embed(poll_dict))

    @commands.command(aliases=['search_poll', 'find_poll'])
    async def lookup_poll(self, ctx):
        """A command which allows a user to search the poll list."""
        sender = ctx.message.author
        
        await ctx.send('Enter the name of the poll you\'re looking for')

        poll_name = await self.get_user_input(sender)
        poll_dict = await self.search_poll(poll_name)
        if poll_dict == False:
            await ctx.send('No poll found with that name.')
        else:
            await ctx.send(embed=await self.create_poll_embed(poll_dict))
   
    @commands.command()
    async def vote(self, ctx):
        """A command which allows a user to vote in a poll."""
        sender = ctx.message.author

        await ctx.send('Enter the name of the poll you\'d like to vote in')
        poll_name = await self.get_user_input(sender)
        poll_dict = await self.search_poll(poll_name)
        if poll_dict == False:
                await ctx.send('No poll found with that name.')
        else:
            voter_id = poll_name.author.id
            counter = 0
            for dictionary in poll_dict['poll_options']:
                if voter_id in dictionary['voters']:
                    await ctx.send('You\'ve already voted in this poll.')
                else:
                    counter += 1
            if counter == len(poll_dict['poll_options']):
                await ctx.send(embed=await self.create_poll_embed(poll_dict))
                while True:
                    await ctx.send(
                        'Enter the number beside the poll option'
                        ' you\'d like to vote for'
                    )
                    user_vote = await self.get_user_input(sender)

                    counter = 0
                    vote = user_vote.content
                    for dictionary in poll_dict['poll_options']:
                        if vote == str(dictionary['index']): 
                            dictionary['voters'].append(voter_id)
                            await ctx.send('Vote successfully recorded.')
                            poll_dict['participant_count'] += 1
                            dump_poll_data(polls)
                        else:
                            counter += 1
                    if counter == len(poll_dict['poll_options']):
                        await ctx.send('Invalid vote.')
                        await ctx.send('Would you like to try again?(Y/N)')
                        choice = await self.get_user_input(sender)
                        if choice.content.upper() == 'N':
                            break
                    else:
                        break

    @commands.command()
    async def poll(self, ctx):
        """A command which allows a user to create a poll."""
        await ctx.send('Enter the name of the poll')

        sender = ctx.message.author

        poll_name = await self.get_user_input(sender)

        if len(polls) > 0:
            poll_name = await self.validate_poll_name(ctx, 
                                                      polls, 
                                                      poll_name, 
                                                      sender
                                                    )
            
        await ctx.send(
            'Enter each poll option separated by a comma. For example: Red,'
            ' Yellow, Blue, Green. There must be more than one option and'
            ' none of the options can be blank. Duplicates will be removed'
            ' automatically.'
        )

        poll_options = await self.get_user_input(sender)
        poll_options = remove_whitespace(poll_options.content.split(','))
        poll_options = await self.validate_poll_opts(ctx, 
                                                     poll_options, 
                                                     sender
                                                    )
        new_poll = {}

        new_poll['name'] = poll_name.content
        new_poll['index'] = get_next_index(polls)
        new_poll['participant_count'] = 0
        new_poll['poll_options'] = []

        for poll_opt in poll_options:
            poll_option = {}
            poll_option["option"] = poll_opt
            poll_option["index"] = get_next_index(new_poll['poll_options'])
            poll_option["voters"] = []
            new_poll['poll_options'].append(poll_option)
        await ctx.send(embed=await self.create_poll_embed(new_poll))
        polls.append(new_poll)
        dump_poll_data(polls)
    
    @commands.command(aliases=['remove_poll', 'delete_poll'])
    @commands.has_permissions(administrator=True)
    async def del_poll(self, ctx):
        """A command which allows an admin to delete a poll."""
        sender = ctx.message.author

        await ctx.send('Enter the name of the poll you\'d like to delete')
        poll_name = await self.get_user_input(sender)
        poll_dict = await self.search_poll(poll_name)
        
        if poll_dict == False:
                await ctx.send('No poll found with that name.')
        else:
            polls[:] = [
                d for d in polls if d.get('name') != poll_dict['name']
            ]
            dump_poll_data(polls)
            await ctx.send('Poll successfully deleted.')

    @del_poll.error
    async def del_poll_error(self, ctx, error):
        """A function which handles errors thrown by the del_poll function.

        Keyword Arguments:
        ctx   -- discord context object
        error -- a discord exception object 
        """
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Only administrators may delete polls.")


def setup(bot):
    bot.add_cog(Poll(bot))