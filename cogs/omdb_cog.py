import discord
from discord.ext import commands
import aiohttp

from api_keys.omdb_auth import OMDB_API_KEY

BASE_URL = 'https://www.omdbapi.com/'

embed_field_settings = {
    'Plot': False,
    'Year': True,
    'Runtime': True,
    'imdbRating': True,
    'Director': True,
    'Writer': False,
    'Genre': False,
    'Language': False,
    'Actors': False
}


class OMDBCog(commands.Cog):
    """A module with movie related commands.

    Methods:
    get_movie   -- outputs a movie's data formatted in a discord embed
    get_series  -- outputs a series' data formatted in a discord embed
    get_episode -- outputs an episode's data formatted in a discord embed
    get_season  -- outputs a season's data formatted in a discord embed
    """

    def __init__(self, bot):
        self.bot = bot

    async def create_embed(self, data_dict):
        """Returns a discord embed object.

        Arguments:
        data_dict -- dictionary containing series or film metadata
        """
        media_embed = discord.Embed(
            title=data_dict['Title'],
            colour=0xffae42
        )

        for key, value in embed_field_settings.items():
            media_embed.add_field(
                name=key,
                value=data_dict[key],
                inline=embed_field_settings[key]
            )

        media_embed.set_image(url=data_dict['Poster'])
        media_embed.set_footer(
            text='Source: The Open Movie Database'
                 ' API - http://www.omdbapi.com/'
        )
        return media_embed

    async def send_request(self, ctx, params):
        """Makes a GET request to the OMDB API and handles the response.

        Arguments:
        ctx    -- a discord context object
        params -- a dictionary of query parameters
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, params=params) as resp:
                data_dict = await resp.json()

        if data_dict['Response'] == 'False':
            await ctx.send('Your search did not return any results.')
        else:
            media_embed = await self.create_embed(data_dict)
            await ctx.send(embed=media_embed)

    # Commands:

    @commands.command(aliases=['movie'])
    async def get_movie(self, ctx, *, search=None):
        """Outputs a movie's data formatted in a discord embed.

        Arguments:
        ctx -- discord context object

        Keyword Arguments:
        search -- string containing movie title
        """
        if search is None:
            await ctx.send('You must enter the title of a movie.')
        else:
            params = {}
            params['t'] = search.strip()
            params['type'] = 'movie'
            params['apikey'] = OMDB_API_KEY

            await self.send_request(ctx, params)

    @commands.command(aliases=['series'])
    async def get_series(self, ctx, *, search=None):
        """Outputs a series' data formatted in a discord embed.

        Arguments:
        ctx -- discord context object

        Keyword Arguments:
        search -- string containing series' title
        """
        if search is None:
            await ctx.send('You must enter the title of a series.')
        else:
            params = {}
            params['t'] = search.strip()
            params['type'] = 'series'
            params['apikey'] = OMDB_API_KEY

            await self.send_request(ctx, params)

    @commands.command(aliases=['episode', 'ep'])
    async def get_episode(self, ctx, *, search=None):
        """Outputs an episode's data formatted in a discord embed.

        Arguments:
        ctx -- discord context object

        Keyword Arguments:
        search -- string containing episode title
        """
        if search is None:
            await ctx.send(
                'You must enter the **title** of an episode followed by t'
                ' **season number** and **episode number**. \n\nFor example,'
                ' if you wanted True Detective S01 EP8, you\'d type:\n\n'
                ' $episode True Detective, 1, 8. It **must** be in this order.'
            )
        else:
            try:
                search_title, search_season, search_episode = search.split(',')
            except ValueError:
                await ctx.send(
                    'Invalid search. Proper format:\nepisode title, season'
                    ' number, episode number. \n\nFor example, if you wanted'
                    ' True Detective S01 EP8, you\'d type:\n\n $episode True'
                    ' Detective, 1, 8. It **must** be in this order.'
                )
            params = {}
            params['t'] = search_title.strip()
            params['episode'] = search_episode.strip()
            params['season'] = search_season.strip()
            params['apikey'] = OMDB_API_KEY

            await self.send_request(ctx, params)

    @commands.command(aliases=['season'])
    async def get_season(self, ctx, *, search=None):
        """Outputs a season's data formatted in a discord embed.

        Arguments:
        ctx -- discord context object

        Keyword Arguments:
        search -- string containing season title
        """
        if search is None:
            await ctx.send(
                'You must enter the **title** of an series followed by the'
                ' **season number**\n\nFor example, if you wanted True'
                ' Detective S01, you\'d type:\n\n $episode True Detective, 1.'
                ' It **must** be in this order.'
            )
        else:
            try:
                search_title, search_season = search.split(',')
            except ValueError:
                await ctx.send(
                    'Invalid search. Proper format:\nseries title, season'
                    ' number.\n\nFor example, if you wanted True Detective'
                    ' S01, you\'d type:\n\n $episode True Detective, 1. It'
                    ' **must** be in this order.'
                )
            params = {}
            params['t'] = search_title.strip()
            params['season'] = search_season.strip()
            params['apikey'] = OMDB_API_KEY

            async with aiohttp.ClientSession() as session:
                async with session.get(BASE_URL, params=params) as resp:
                    data_dict = await resp.json()

            await ctx.send(data_dict)

            media_embed = discord.Embed(
                title=data_dict['Title'],
                colour=0xffae42
            )

            media_embed.add_field(
                name='Season',
                value=data_dict['Season'],
                inline=True
            )

            media_embed.add_field(
                name='Total Seasons',
                value=data_dict['totalSeasons'],
                inline=False
            )

            for episode in data_dict['Episodes']:
                media_embed.add_field(
                    name=episode['Title'],
                    value=f'EP: {episode["Episode"]}',
                    inline=True
                )

                media_embed.add_field(
                    name='Released',
                    value=episode['Released'],
                    inline=True
                )

                media_embed.add_field(
                    name='IMDB Rating',
                    value=episode['imdbRating'],
                    inline=True
                )

            # for key, value in embed_field_settings.items():
            #     media_embed.add_field(
            #         name=key,
            #         value=data_dict[key],
            #         inline=embed_field_settings[key]
            #     )

            # media_embed.set_image(url=data_dict['Poster'])
            media_embed.set_footer(
                text='Source: The Open Movie Database'
                     ' API - http://www.omdbapi.com/'
            )

            await ctx.send(embed=media_embed)


def setup(bot):
    bot.add_cog(OMDBCog(bot))
