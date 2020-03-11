import math

import discord
from discord.ext import commands
import aiohttp

from owmkey import API_KEY

DEGREE_SYMBOL = u'\N{DEGREE SIGN}'

URL = 'https://api.openweathermap.org/data/2.5/weather?'


class Weather(commands.Cog):
    """A module with weather related commands."""

    def __init__(self, bot):
        self.bot = bot

    async def covt_ms_mph(self, speed):
        """Accepts a speed in m/s and returns it in mph."""
        speed = 2.23694 * speed
        return speed

    async def covt_kelvin_farenheit(self, temp):
        """"Accepts a temperature in kelvin and returns it 
        in farenheit.
        """
        temp = (9/5 * (temp - 273.15)) + 32
        return temp

    async def covt_celsius_farenheit(self, temp):
        """"Accepts a temperature in calsius and returns it 
        in farenheit.
        """
        temp = (9/5) * temp + 32
        return temp

    async def covt_windchill(self, windchill, units):
        """Because the speed and temperature need to be converted to 
        mph and fareheit respectively, this function accepts
        a winchill measurement and converts it back to the original 
        unit measurement."""
        if units == 'standard':
            windchill = (5/9 * (windchill - 32)) + 273.15
        elif units == 'metric':
            windchill = 5/9 * (windchill - 32)
        else:
            pass
        windchill = '%.2f' % windchill
        return float(windchill)

    async def calc_windchill(self, temp, speed):
        """Accepts a speed, temperature and unit of measurement. It 
        then calculates windchill based on what the unit of 
        measurement is.
        """
        windchill = 'n/a'
        if speed > 3 and temp <= 50:
            windchill = (13.12 + 0.6215*temp - 11.37*math.pow(speed, 0.16) 
                         + 0.3965*temp*math.pow(speed, 0.16))
        return windchill

    async def set_units(self, units='standard'):
        """Accepts a measurement system and assigns global variables 
        represneting temperature and wind speed measurement their
        corresponding identifiers.
        """
        unit_list = []
        if units == 'standard':
            unit_list.append('K')
            unit_list.append('m/s')
        elif units == 'metric':
            unit_list.append(f'{DEGREE_SYMBOL}C')
            unit_list.append('m/s')
        else:
            unit_list.append(f'{DEGREE_SYMBOL}F')
            unit_list.append('mph')
        return unit_list

    async def create_embed(self, dict, unit_list):
        """Accepts a dictionary of weather data from an owm api query
        and formats it into a discord embed.
        """
        title = (f'Showing the current weather for {dict["name"]},' 
                 f' {dict["sys"]["country"]}')
        weather_embed = discord.Embed(title=title,
                                      colour=0xd3d3d3)
        weather_embed.add_field(name='Description',
                                value=dict['weather'][0]['description'],
                                inline=True)
        weather_embed.add_field(name='Temperature',
                                value=f'{dict["main"]["temp"]}{unit_list[0]}',
                                inline=True)
        try:
            weather_embed.add_field(name='Feels Like',
                                    value=f'{dict["windchill"]}',
                                    inline=False)
        except KeyError:
            print('No windchill.')               
        weather_embed.add_field(name='Humidity',
                                value=f'{dict["main"]["humidity"]}%',
                                inline=False)
        weather_embed.add_field(name='Cloudiness',
                                value=f'{dict["clouds"]["all"]}%',
                                inline=False)
        weather_embed.add_field(name='Wind Speed',
                                value=f'{dict["wind"]["speed"]}{unit_list[1]}',
                                inline=False)
        weather_embed.set_image(url=f'https://openweathermap.org/img/w/'
                                    f'{dict["weather"][0]["icon"]}.png')
        weather_embed.set_footer(text='Weather data provided by OWM:'
                                      'https://openweathermap.org/api')
        return weather_embed
        
    async def create_param_dict(self, query_params, context):
        """ Accepts a list of parameters and a discord context object 
        and creates a parameter dict for a owm api query.
        """
        params = {}

        if len(query_params) > 3:
            await context.send('Too many parameters. \nProper format:'
                               '\ncity, country, units \nor \ncity,' 
                               ' country')
        elif len(query_params) == 3:
            params['q'] = f'{query_params[0]},{query_params[1]}'
            params['units'] = query_params[2]
            params['APPID'] = API_KEY
        elif len(query_params) == 2:
            params['q'] = f'{query_params[0]},{query_params[1]}'
            params['APPID'] = API_KEY
            # url = (f'https://api.openweathermap.org/data/2.5/weather?q='
            #        f'{query_params[0]},{query_params[1]}&APPID={API_KEY}')
        else:
            await context.send('Too few parameters. \nProper format:'
                               '\ncity, country, units \nor \ncity,' 
                               ' country')
        return params

    @commands.command(aliases=['temperature', 'temp'])
    async def get_temp(self, ctx, *, location=None):
        """Accepts a location and displays its current weather 
        conditions if it's a valid location.
        """
        if location is None:
            await ctx.send('I don\'t recall there being a location with no' 
                           ' name. Try again, but actually enter a' 
                           ' location, baka!',
                           delete_after=4)
        else:
            try:
                query_params = location.split(',')
                query_params = [param.strip() for param in query_params]
            except ValueError:
                await ctx.send('**Invalid search. \nProper format:** \ncity,' 
                               ' country, units \nor \ncity, country')
            
            print(query_params)

            params = await self.create_param_dict(query_params, ctx)
            await ctx.send(params)
            async with aiohttp.ClientSession() as session:
                async with session.get(url=URL, params=params) as resp:
                    data_dict = await resp.json()
                    await ctx.send(resp.url)
                    await ctx.send(data_dict)

            if 'message' in data_dict.keys():
                if data_dict['message'] == 'city not found':
                    await ctx.send('No city found with that name.')
            else:
                if 'units' in params.keys():
                    units = await self.set_units(params['units'])
                    if params['units'] == 'imperial':
                        windchill = await self.calc_windchill(
                            data_dict['main']['temp'],
                            data_dict['wind']['speed']
                        )
                    else:
                        windchill = await self.calc_windchill(
                            await self.covt_celsius_farenheit(                    
                                data_dict['main']['temp']),
                            await self.covt_ms_mph(
                                data_dict['wind']['speed'])
                        )
                    if windchill == 'n/a':
                        pass
                    else:
                        windchill = await self.covt_windchill(windchill, 
                                                              params['units'])
                        data_dict['windchill'] = windchill
                else:
                    units = await self.set_units()
                    windchill = await self.calc_windchill(
                        await self.covt_kelvin_farenheit(
                            data_dict["main"]["temp"]),
                        await self.covt_ms_mph(
                            data_dict['wind']['speed'])
                    ) 
                    if windchill == 'n/a':
                        pass
                    else:
                        windchill = await self.covt_windchill(windchill)
                        data_dict['windchill'] = windchill
                weather_embed = await self.create_embed(data_dict, units)
                await ctx.send(embed=weather_embed)


def setup(bot):
    bot.add_cog(Weather(bot))