import discord
from discord.ext import commands
import aiohttp

from omdbKey import omdb_api_key

URL = 'https://www.omdbapi.com/'


class MovieTv(commands.Cog):
    """A module with movie/tv related commands.
    
    Methods:
    get_movie_tv -- outputs a movie or tv show's data formatted 
                    in a discord embed
    """

    def __init__(self, bot):
        self.bot = bot

    async def create_embed(self, data_dict):
        """Returns a discord embed object.
        
        Keyword Arguments:
        data_dict -- dictionary containing show/film metadata 
        """
        media_embed = discord.Embed(
            title=data_dict['Title'],
            colour=0xffae42
        )
        media_embed.add_field(
            name='Synopsis:',
            value=data_dict['Plot'],
            inline=False
        )
        media_embed.add_field(
            name='Year:',
            value=data_dict['Year'],
            inline=True
        )
        media_embed.add_field(
            name='Runtime:',
            value=data_dict['Runtime'],
            inline=True
        )
        media_embed.add_field(
            name='IMDB Rating:',
            value=data_dict['imdbRating'],
            inline=True
        )
        media_embed.add_field(
            name='Director:',
            value=data_dict['Director'],
            inline=True)
        media_embed.add_field(
            name='Writer:',
            value=data_dict['Writer'],
            inline=False
        )
        media_embed.add_field(
            name='Genres:',
            value=data_dict['Genre'],
            inline=False
        )
        media_embed.add_field(
            name='Languages:',
            value=data_dict['Language'],
            inline=False
        )
        media_embed.add_field(
            name='Main Actors:',
            value=data_dict['Actors'],
            inline=False
        )
        media_embed.set_image(url=data_dict['Poster'])
        media_embed.set_footer(
            text='Source: The Open Movie Database' 
                 ' API - http://www.omdbapi.com/'
        )
        return media_embed

    @commands.command(aliases=['movie', 'tv'])
    async def get_movie_tv(self, ctx, *, movie_tv_search=None):
        """Outputs a movie or tv show's data formatted in a discord embed.
        
        Keyword Arguments:
        ctx             -- discord context object
        movie_tv_search -- string containing movie/show title followed by a
                           comma and the type e.g: Hannibal, tv 
        """
        if movie_tv_search is None:
            await ctx.send(
                'You must enter the title of a tv show or film followed by'
                ' the type. \nProper format:\nmedia title, type\ntype can be' 
                ' either: series or movie\nMovie Example: the clovehitch' 
                ' killer, movie\nTv Example: hannibal, series'
            )
        else:
            try:
                search_title, search_type = movie_tv_search.split(',')
            except ValueError:
                await ctx.send(
                    'Invalid search. Proper format:\nmedia title, type\ntype'
                    ' can be either: series or movie\nMovie Example: the'
                    ' clovehitch killer, movie\nTv Example: hannibal, series'
                )
            params = {}
            params['t'] = search_title
            params['type'] = search_type.strip()
            params['apikey'] = omdb_api_key

            # Query the OMDb API Asynchronously.
            async with aiohttp.ClientSession() as session:
                async with session.get(URL, params=params) as resp:
                    data_dict = await resp.json()    
            
            if 'Error' in data_dict.keys():
                await ctx.send(
                    'No show or film found with that title.'
                )
            else:
                media_embed = await self.create_embed(data_dict)
                await ctx.send(embed=media_embed)


def setup(bot):
    bot.add_cog(MovieTv(bot))