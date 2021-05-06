import discord
from discord.ext import commands
import aiohttp

import animeQueryTemplate
import mangaQueryTemplate
from cogs.extra_funcs import format_date
from cogs.extra_funcs import list_to_str

URL = 'https://graphql.anilist.co'
FOOTER = ('Source: The AniList API - '
          'https://github.com/AniList/ApiV2-GraphQL-Docs')


class Weeb(commands.Cog):
    """A module with anime/manga related commands.
    
    Methods:
    query_anilist_api -- queries AniList's API and returns the 
                         results in a dict
    format_date       -- returns a date formatted in mm-dd-yyyy
    """

    def __init__(self, bot):
        self.bot = bot
    
    async def query_anilist_api(self, var_dict, query_type):
        """Queries AniList's API and returns a the results in a dict.
        
        Keyword Arguments:
        var_dict   -- dict containing name of media to be queried
        query_type -- string representing type of query (anime or manga) 
        """
        if query_type == 'anime':
            json_param = {
                'query': animeQueryTemplate.anime_query,
                'variables': var_dict
            }
        else:
            json_param = {
                'query': mangaQueryTemplate.manga_query,
                'variables': var_dict
            }

        # Query the AniList API Asynchronously.
        async with aiohttp.ClientSession() as session:
            resp = await session.post(URL, json=json_param)
            data_dict = await resp.json()
        return data_dict

    async def format_dict_data(self, data_dict):
        """Returns a dict with the metadata about the media formatted.
        
        Keyword Arguments:
        media_dict -- the dict containing media's metadata
        """
        data_dict['duration'] = f'{data_dict["duration"]} mins'

        data_dict['startDate'] = format_date(data_dict['startDate'])
        data_dict['endDate'] = format_date(data_dict['endDate'])

        data_dict['description'] = (
            data_dict['description'].replace('<br>', '')
        )

        data_dict['genres'] = list_to_str(data_dict['genres'])

        data_dict['averageScore'] = f'{data_dict["averageScore"]}%'
        
        data_dict['mediaLink'] = (
            f'<https://anilist.co/anime/{data_dict["id"]}/>'
        )
        return data_dict

    async def create_embed(self, data_dict, media_type):
        """Returns an embed object of either anime or manga metadata
        
        Keyword Arguments:
        data_dict  -- the dict containing media's metadata
        media_type -- string representing type of media (anime or manga)
        """
        embed = discord.Embed(
            title=data_dict['title']['romaji'], 
            colour=0x0000ff
        )
        if media_type == 'anime':
            embed.add_field(
                name='Type:',
                value=data_dict['format'],
                inline=True
            )
            embed.add_field(
                name='Episodes:',
                value=data_dict['episodes'],
                inline=True
            )
            embed.add_field(
                name='Duration:',
                value=data_dict['duration'],
                inline=True
            )
        else:
            embed.add_field(
                name='Chapters:',
                value=data_dict['chapters'],
                inline=True
            )
            embed.add_field(
                name='Volumes:',
                value=data_dict['volumes'],
                inline=True
            )
        embed.add_field(
            name='Status:',
            value=data_dict['status'],
            inline=True
        )
        embed.add_field(
            name='Average Rating:',
            value=data_dict['averageScore'],
            inline=True
        )
        embed.add_field(
            name='Start:',
            value=data_dict['startDate'],
            inline=True
        )
        embed.add_field(
            name='End:',
            value=data_dict['endDate'],
            inline=True
        )
        embed.add_field(
            name='Genres:',
            value=data_dict['genres'],
            inline=False
        )
        embed.add_field(
            name='English:',
            value=data_dict['title']['english'],
            inline=False
        )
        embed.add_field(
            name='Native:',
            value=data_dict['title']['native'],
            inline=False
        )
        embed.add_field(
            name='Synopsis:',
            value=data_dict['description'],
            inline=False
        )
        embed.add_field(
            name='More Info:',
            value=data_dict['mediaLink'],
            inline=False
        )
        embed.set_image(
            url=data_dict['coverImage']['large']
        )  
        embed.set_footer(text=FOOTER)
        return embed

    @commands.command(aliases=['anime', 'ganime'])
    async def get_anime(self, ctx, *, anime_search=None):
        """Outputs an anime's data formatted in a discord embed.
        
        Keyword Arguments:
        ctx          - discord context object
        anime_search - string containing name of anime to be searched
        """
        if anime_search is None:
            await ctx.send(
                'The title of the anime cannot be left blank.'
            )
        else:
            variables = {}
            variables['search'] = anime_search
                
            # Call a method to query the AniList API.
            # Harcoded param is the type of query and will never change.
            data_dict = await self.query_anilist_api(
                variables, 
                'anime'
            )
            if 'errors' in data_dict.keys():
                await ctx.send(
                    'No anime found with that title.'
                )
            else:
                data_dict = data_dict['data']['Media']
                data_dict = await self.format_dict_data(data_dict)

                # Hardcoded param is media type and will never change.
                anime_embed = await self.create_embed(data_dict, "anime")
                await ctx.send(embed=anime_embed)
    
    @commands.command(aliases=['manga', 'gmanga'])
    async def get_manga(self, ctx, *, manga_search=None):
        """Outputs a manga's data formatted in a discord embed.
        
        Keyword Arguments:
        ctx          - discord context object
        anime_search - string containing name of manga to be searched
        """
        if manga_search is None:
            await ctx.send(
                'The title of the manga cannot be left blank.'
            )
        else:            
            variables = {}
            variables['search'] = manga_search
            
            # Call a method to query the AniList API.
            # Harcoded param is the type of query and will never change.
            data_dict = await self.query_anilist_api(
                variables, 
                'manga'
            )
            if 'errors' in data_dict.keys():
                await ctx.send(
                    'No manga found with that title.'
                )
            else:
                data_dict = data_dict['data']['Media']
                data_dict = await self.format_dict_data(data_dict)

                # Hardcoded param is media type and will never change.
                manga_embed = await self.create_embed(data_dict, "manga")
                await ctx.send(embed=manga_embed)


def setup(bot):
    bot.add_cog(Weeb(bot))