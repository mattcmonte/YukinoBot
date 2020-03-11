import json

import discord
from discord.ext import commands
from discord import errors

from cogs.extra_funcs import duplicate_count
from cogs.extra_funcs import dump_poll_data
from cogs.extra_funcs import load_poll_data
from cogs.extra_funcs import generate_hex_int
from cogs.extra_funcs import get_next_index

polls = []
# polls = load_poll_data()


class Admin(commands.Cog):
    """ A module with administrative commands."""
    def __init__(self, bot):
        self.bot = bot 

    @commands.command(aliases=['delete', 'purge', 'remove'])
    async def clear(self, ctx, *, amount=None):
        """ This is the clear command. It takes in the number of messages to be deleted. If none are specified, it will try to delete 50 messages.
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
                    'One or more of the messages you tried to bulk delete were too old. They must be under 14 days old or else I can\'t delete them.'
                ) 
            except errors.ClientException:
                await ctx.send(
                    'I can\'t delete more than 100 messages at once, baka!'
                )
        else:
            await ctx.send(
                'Invalid number specified. Must be a positive integer.'
            )
    
    # async def create_poll_embed(self, poll_dict):
    #     """Accepts a dictionary containing poll data and returns it as a discord embed
    #     """
    #     poll_embed = discord.Embed(
    #         title=poll_dict['name'], 
    #         colour=generate_hex_int()
    #     )
    #     poll_embed.add_field(
    #         name='Participants:',
    #         value=poll_dict['participant_count'],
    #         inline=False
    #     )
    #     index = 0
    #     for k, v in poll_dict['poll_options'].items():
    #         index += 1
    #         poll_embed.add_field(
    #             name=f'{index} - {k}',
    #             value=v[0],
    #             inline=False
    #         )
    #     return poll_embed

    async def get_user_input(self, sender):
        """"""
        def check_author(message):
            return message.author == sender

        user_input = await self.bot.wait_for(
            'message',
            check=check_author
        )  
        return user_input

    # async def search_poll(self, poll_name):
    #     """Accepts a poll and returns a dictionary representing that poll or False if not found.
    #     """

    #     poll = False
    #     dup_count = duplicate_count(polls, poll_name)

    #     # If the poll exists
    #     if dup_count == 1: 
    #         for poll_dict in polls:
    #             if poll_dict['name'] == poll_name.content:
    #                 poll = poll_dict
    #     return poll

    # # @commands.command()
    # # async def show_polls(self, ctx):
    # #     """"""

    # @commands.command(aliases=['search_poll', 'find_poll'])
    # async def lookup_poll(self, ctx):
    #     """Allows the user to search for a poll by name and then returns that poll data in a discord embed if the poll is found
    #     """

    #     sender = ctx.message.author
        
    #     await ctx.send(
    #         'Enter the name of the poll you\'re looking for'
    #     )

    #     poll_name = await self.get_user_input(sender)
    #     poll_dict = await self.search_poll(poll_name)
    #     if poll_dict == False:
    #         await ctx.send('No poll found with that name.')
    #     else:
    #         await ctx.send(
    #             embed=await self.create_poll_embed(
    #                 poll_dict
    #             )
    #         )
   
    # @commands.command()
    # async def vote(self, ctx):
    #     """This command allows the user to vote in a poll"""
        
    #     sender = ctx.message.author

    #     await ctx.send(
    #         'Enter the name of the poll you\'d like to vote in'
    #     )

    #     poll_name = await self.get_user_input(sender)
    #     poll_dict = await self.search_poll(poll_name)
    #     if poll_dict == False:
    #         await ctx.send('No poll found with that name.')
    #     else:
    #         await ctx.send(
    #             embed=await self.create_poll_embed(poll_dict)
    #         )

    #         await ctx.send(
    #             'Enter the poll option you\'d like to vote for. (Not case-sensitive)'
    #         )

    #         user_vote = await self.get_user_input(
    #             sender
    #         )

    #         user = user_vote.content
    #         counter = 0
    #         for k, v in poll_dict['poll_options'].items():
    #             if user.lower() == k.lower() and user not in v[1]:
    #                 v[0] += 1
    #                 v[1].append(
    #                     user_vote.author.name
    #                 )
    #                 await ctx.send(
    #                     'Vote successfully recorded.'
    #                 )
    #                 poll_dict['participant_count'] += 1

    #                 poll_str = json.dumps(
    #                     poll_dict, 
    #                     indent=4
    #                 )

    #                 await ctx.send(f'Updated Poll:\n {poll_str}')
    #                 dump_poll_data(poll_dict)
    #             else:
    #                 counter += 1
    #         if counter == len(poll_dict['poll_options']):
    #             await ctx.send(
    #                 'What are you... as blind as Matt? That wasn\'t one of the fucking vote options.'
    #             )

    @commands.command()
    async def poll(self, ctx):
        """A command which allows the user to create a poll. This command creates a dictionary containing poll data which will then be appended to a list and written to a json file
        """
        await ctx.send('Enter the name of the poll')

        sender = ctx.message.author

        poll_name = await self.get_user_input(sender)

        if len(polls) > 0:
            dup_count = duplicate_count(polls, poll_name)
            
            while dup_count >= 1:
                await ctx.send(
                    'A poll with this name already exists. Enter a different name.'
                )

                poll_name = await self.get_user_input(sender)

                dup_count = duplicate_count(polls, poll_name)

        await ctx.send(
            'Enter each poll option separated by a comma. For example: Red, Yellow, Blue, Green'
        )

        poll_options = await self.get_user_input(sender)

        while len(set(poll_options.content.split(','))) == 1:
            await ctx.send(
                'How in the name of all that is holy can you have a poll with one fucking option or the same option more than once?! Reenter, you animal.'
            )

            poll_options = await self.get_user_input(sender)
        
        new_poll = {}

        new_poll['name'] = poll_name.content
        new_poll['index'] = get_next_index(polls)
        new_poll['participant_count'] = 0
        new_poll['poll_options'] = []

        poll_opts = set(poll_options.content.split(','))
        for poll_opt in poll_opts:
            poll_option = {}
            poll_option["option"] = poll_opt,
            poll_option["index"] = get_next_index(new_poll['poll_options']),
            poll_option["voters"] = []
            new_poll['poll_options'].append(poll_option)

        await ctx.send()

        # for dictionary in polls:
        #     if dictionary['name'] == poll_name.content:

        polls.append(new_poll)
        dump_poll_data(polls)

        # await ctx.send(
        #     embed=await self.create_poll_embed(new_poll)
        # )


def setup(bot):
    bot.add_cog(Admin(bot))