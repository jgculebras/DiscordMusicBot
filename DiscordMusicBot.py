import requests
import random
import numpy as np
import asyncio
import mysql.connector
import discord
from discord import app_commands
from discord.ext import commands
import wavelink
from wavelink.ext import spotify

user = ""
password = ""
spotifyClientId = ""
spotifyClientSecret = ""
apiSpotify = ""
bottoken = ""

def _getAuthorsListened(id):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        cursor = connection.cursor()
        mySql_select_query = """select songAuthor, COUNT(timesListen) from userListenSong where userId = %s group by songAuthor order by Count(timesListen) DESC LIMIT 5"""

        record = (str(id),)
        cursor.execute(mySql_select_query, record)
        result = cursor.fetchall()
        return result

    except mysql.connector.Error as error:
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def _getSongsListened(id):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        cursor = connection.cursor()
        mySql_select_query = """Select songName, timesListen FROM userListenSong WHERE userId = %s and timesListen > 0 order by timesListen DESC LIMIT 5"""

        record = (str(id),)
        cursor.execute(mySql_select_query, record)
        result = cursor.fetchall()
        return result

    except mysql.connector.Error as error:
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def _insertOneMore(title, author, users):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        for i in users:
             if i != 1065070645454589992:
                 cursor = connection.cursor()

                 mysql_update_query = """INSERT INTO userListenSong(songName, songAuthor, userId, timesListen) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE timesListen=timesListen+1"""

                 record = (title, author, str(i), 1)
                 cursor.execute(mysql_update_query, record)

                 connection.commit()

                 cursor.close()

    except mysql.connector.Error as error:
        print("Error in one less sql", error)
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def _insertOneLess(title, author, users):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        for i in users:
             if i != 1065070645454589992:
                 cursor = connection.cursor()

                 mysql_update_query = """INSERT INTO userListenSong(songName, songAuthor, userId, timesListen) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE timesListen=timesListen-1"""

                 record = (title, author, str(i), -1)
                 cursor.execute(mysql_update_query, record)

                 connection.commit()

                 cursor.close()

    except mysql.connector.Error as error:
        print("Error in one less sql", error)
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def _votePlaylist(playlistName, userId):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        cursor = connection.cursor()

        mysql_select_query = """SELECT playlistId FROM Playlists WHERE playlistName = %s"""

        record = (playlistName,)
        cursor.execute(mysql_select_query, record)
        resultPlaylist = cursor.fetchall()

        if resultPlaylist != []:
            mysql_select_query = """SELECT voted FROM userVote WHERE userId = %s"""

            record = (str(userId),)
            cursor.execute(mysql_select_query, record)
            result = cursor.fetchall()

            if result == [] or result[0][0] == 0:
                mysql_update_query = """INSERT INTO userVote(userId, voted) VALUES (%s, %s) ON DUPLICATE KEY UPDATE voted=%s"""

                record = (str(userId), 1, 1)
                cursor.execute(mysql_update_query, record)

                connection.commit()

                cursor.close()

                cursor = connection.cursor()

                mysql_update_query = """UPDATE Playlists SET Stars = Stars + 1 WHERE playlistName = %s"""

                record = (playlistName,)

                cursor.execute(mysql_update_query, record)

                connection.commit()

                return "OK"

            else:

                return "NV"

        else:

            return "NP"


    except mysql.connector.Error as error:
        print("Error in fav sql", error)
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def _getPlaylistSongs(playlistName, guildId):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        cursor = connection.cursor()
        mySql_select_query = """Select songName from PlaylistHasSong WHERE playlistId = (Select playlistId FROM Playlists p WHERE p
.playlistName = %s and p.playlistGuild = %s) ORDER BY RAND()"""

        record = (playlistName, str(guildId))
        cursor.execute(mySql_select_query, record)
        result = cursor.fetchall()
        return result

    except mysql.connector.Error as error:
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def _addPlaylistSong(playlistName, guildId, songName, songLength, songUrl, songAuthor):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO PlaylistHasSong (playlistId, songName, songLength, songUrl, songAuthor) SELECT playlistId, %s, %s, %s, %s FROM Playlists p WHERE p.playlistName = %s and p.playlistGuild = %s"""

        record = (songName, songLength, songUrl, songAuthor, playlistName, str(guildId))
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        if cursor.rowcount > 0:
            return "Inserted"
        else:
            return "Not Inserted"

    except mysql.connector.Error as error:
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def _insertSong(title, length, uri, author):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        cursor = connection.cursor()

        mySql_insert_query = """INSERT INTO Songs(songName, songLength, songUrl, songAuthor) VALUES (%s, %s, %s, %s)"""

        record = (title, length, uri, author)
        cursor.execute(mySql_insert_query, record)
        connection.commit()

        return 0

    except mysql.connector.Error as error:
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def _listPlaylists():
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        cursor = connection.cursor()
        mySql_select_query = """Select playlistName, Stars from Playlists ORDER BY Stars DESC, RAND()"""

        cursor.execute(mySql_select_query)
        result = cursor.fetchall()
        return result

    except mysql.connector.Error as error:
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")



def _createPlaylist(playlistName, playlistGuild):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='botDiscord',
                                             user=user,
                                             password=password)

        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO Playlists (playlistName, playlistGuild, Stars)
                                VALUES (%s, %s, %s)"""

        record = (playlistName, str(playlistGuild), 0)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        return "Inserted"

    except mysql.connector.Error as error:
        return error


    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

async def last_callback(interaction):
    await interaction.message.edit(view = None)

    vc = interaction.guild.voice_client
    if vc:
        if not vc.is_playing():
            return await interaction.channel.send("Nothing is playing.")
        if vc.itt == 0:
            return await vc.stop()
        else:
            vc.itt -= 2
        await vc.seek(vc.track.length * 1000)

        if vc.is_paused():
            await vc.resume()
    else:
        await interaction.channel.send("The bot is not connected to a voice channel.")

async def skip_callback(interaction):
    await interaction.message.edit(view = None)

    vc = interaction.guild.voice_client
    if vc:
        if not vc.is_playing():
            return await interaction.channel.send("Nothing is playing.")

        if vc.position < vc.track.duration / 1.5:
            _insertOneLess(vc.track.title, vc.track.author, np.intersect1d([user.id for user in vc.users[vc.itt]], [member.id for member in vc.channel.members]))

        if vc.itt == len(vc.queue) - 1:
            return await vc.stop()


        await vc.seek(vc.track.length * 1000)


        if vc.is_paused():
            await vc.resume()
    else:
        await interaction.channel.send("The bot is not connected to a voice channel.")

async def play_callback(interaction):
    vc = interaction.guild.voice_client

    if vc:
        if not vc.is_playing():
            return await interaction.channel.send("Nothing is playing.")

        if vc.is_paused():
            view = discord.ui.View(timeout=vc.track.length - vc.position - 5)

            if vc.itt != 0:
                button1 = discord.ui.Button(
                    label="⏮️",
                    style=discord.ButtonStyle.secondary,
                    custom_id="button1"
                )
                view.add_item(button1)
                button1.callback = last_callback

            button2 = discord.ui.Button(
                label="⏭️ ",
                style=discord.ButtonStyle.secondary,
                custom_id="button2"
            )

            button3 = discord.ui.Button(
                label="⏸️",
                style=discord.ButtonStyle.secondary,
                custom_id="button3"
            )

            view.add_item(button3)
            view.add_item(button2)

            await interaction.response.send_message(content="Resuming Song...", ephemeral=True, delete_after=5)

            newMessage = await vc.messages[vc.itt].edit(view=view)

            button2.callback = skip_callback
            button3.callback = pause_callback

            await vc.resume()


    else:
        await interaction.channel.send("The bot is not connected to a voice channel.")

async def pause_callback(interaction):
    vc = interaction.guild.voice_client

    if vc:
        if not vc.is_playing():
            return await interaction.channel.send("Nothing is playing.")

        if not vc.is_paused():
            await vc.pause()
            view = discord.ui.View(timeout=None)

            if vc.itt != 0:
                button1 = discord.ui.Button(
                    label="⏮️",
                    style=discord.ButtonStyle.secondary,
                    custom_id="button1"
                )
                view.add_item(button1)
                button1.callback = last_callback

            button2 = discord.ui.Button(
                label="⏭️ ",
                style=discord.ButtonStyle.secondary,
                custom_id="button2"
            )

            button3 = discord.ui.Button(
                label="▶️",
                style=discord.ButtonStyle.secondary,
                custom_id="button3"
            )

            view.add_item(button3)
            view.add_item(button2)

            newMessage = await vc.messages[vc.itt].edit(view=view)

            await interaction.response.send_message(content="Pausing Song...", ephemeral=True, delete_after=5)

            button2.callback = skip_callback
            button3.callback = play_callback

    else:
        await interaction.channel.send("The bot is not connected to a voice channel.")


class CustomPlayer(wavelink.Player):

    def __init__(self, ctx):
        super().__init__()
        self.itt = 0
        self.users = {}
        self.queue = []
        self.messages = []
        self.ctx = ctx


client = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="!help"))
    client.loop.create_task(connect_nodes())


async def connect_nodes():
    await client.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=client,
        host='127.0.0.1',
        port=2333,
        password='youshallnotpass',
        spotify_client=spotify.SpotifyClient(client_id=spotifyClientId, client_secret=spotifyClientSecret)
)


@client.event
async def on_wavelink_track_end(player: CustomPlayer, track: wavelink.Track, reason):
    _insertOneMore(track.title, track.author, np.intersect1d([user.id for user in player.users[player.itt]], [member.id for member in player.channel.members]))
    player.itt += 1
    if not player.itt == len(player.queue):
        next_track = player.queue[player.itt]
        await player.play(source=next_track, start=5000, end=next_track.length - 5000)

        _insertSong(next_track.title, next_track.length, next_track.uri, next_track.author)

        string = ""

        if next_track.length > 120:
            string = "**" + str(int(next_track.length / 60)) + ":"
        elif next_track.length > 60:
            string = "**1:"
        else:
            string = "**"
        if string == "**":
            string += str(int(next_track.length % 60)) + "s**"
        else:
            string += str(int(next_track.length % 60)).zfill(2) + "**"

        embed = discord.Embed(title="Playing Now", color=0x808080)
        embed.add_field(name="```💿 Track```", value=f"**[{next_track.title}]({next_track.uri})**", inline=False)
        embed.add_field(name="```⏱️ Duration```", value=f"**{string}**", inline=False)

        view = discord.ui.View(timeout=next_track.length - 10)

        if player.itt != 0:
            button1 = discord.ui.Button(
                label="⏮️",
                style=discord.ButtonStyle.secondary,
                custom_id="button1"
            )
            view.add_item(button1)
            button1.callback = last_callback

        button2 = discord.ui.Button(
            label="⏭️ ",
            style=discord.ButtonStyle.secondary,
            custom_id="button2"
        )

        button3 = discord.ui.Button(
            label="⏸️",
            style=discord.ButtonStyle.secondary,
            custom_id="button3"
        )

        view.add_item(button3)
        view.add_item(button2)

        message = await player.ctx.send(embed=embed, view=view)

        if player.itt == len(player.messages):
            player.messages.append(message)
        else:
            player.messages[player.itt] = message

        player.users[player.itt] = player.channel.members

        button2.callback = skip_callback
        button3.callback = pause_callback

        await player.messages[player.itt - 1].edit(view=None)


@client.event
async def on_wavelink_websocket_closed(player: wavelink.Player, reason, code):
    if player.is_playing:
        await player.destroy()

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and after.channel is None and member.id == 1065070645454589992:
        vc = member.guild.voice_client
        await vc.disconnect()

@client.command()
async def getGuilds(ctx):
    user = ctx.author

    for guild in user.mutual_guilds:
        perms = guild.get_member(user.id).guild_permissions
        if perms.administrator:
            await ctx.send(f"You are an admin in {guild.name}")
        else:
            await ctx.send(f"You are not an admin in {guild.name}")

@client.command()
async def help(ctx):
    embed = discord.Embed(title="Bot Help", color=0x507CA5)

    embed.add_field(name="```Track Commands```", value="", inline=False)

    embed.add_field(name="[!p !play, !Play, !P] *{Song}*", value="Play a song if queue is empty or queue it if a song is already playing.", inline=False)
    embed.add_field(name="!skip", value="Skip the playing song to the next one in the queue.", inline=False)
    embed.add_field(name="!pause", value="Pause the playing song.", inline=False)
    embed.add_field(name="!resume", value="Resume the song that was paused.", inline=False)

    embed.add_field(name="```Playlists Commands```", value="", inline=False)

    embed.add_field(name="!cp *{Playlist name}*", value="Create a playlist with a name.", inline=False)
    embed.add_field(name="!pls", value="List all the playlists created.", inline=False)
    embed.add_field(name="!aps *{Playlist name}* *{Song}*", value="Add a song to the playlist.", inline=False)
    embed.add_field(name="!pp *{Playlist name}*", value="Play the playlist.", inline=False)
    embed.add_field(name="!pll *{Playlist name}*", value="Get list of songs in a playlist.", inline=False)

    embed.add_field(name="```Utils Commands```", value="", inline=False)

    embed.add_field(name="!msl", value="Get your most played songs.", inline=False)
    embed.add_field(name="!mal", value="Get your most played authors.", inline=False)
    embed.add_field(name="!ads", value="Get information about how to advertise", inline=False)
    embed.add_field(name="!premium", value="Get information about premium.", inline=False)


    await asyncio.sleep(0.5)

    await ctx.send(embed=embed)

@client.command()
async def connect(ctx):
    vc = ctx.voice_client
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        embed = discord.Embed(title="Please join a voice channel.", color=0xff0000)
        return await ctx.send(embed=embed)

    if not vc:
        custom_player = CustomPlayer(ctx)
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)


@client.command()
async def disconnect(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
    else:
        embed = discord.Embed(title="The bot is not connected to a channel.", color=0xff0000)
        return await ctx.send(embed=embed)

@client.command()
async def msl(ctx):
    user = ctx.author

    result = _getSongsListened(user.id)

    if len(result) > 0:
        embed = discord.Embed(title=f"Most played songs.", color=0xffff00)

        for song in result:
            embed.add_field(name="", value=f"- {song[0]} played {song[1]} times.", inline=False)

        await ctx.send(embed=embed)

    else:
        await ctx.send("No songs played yet.")

@client.command()
async def mal(ctx):
    user = ctx.author

    result = _getAuthorsListened(user.id)

    if len(result) > 0:
        embed = discord.Embed(title=f"Most played authors.", color=0xffff00)

        for author in result:
            embed.add_field(name="", value=f"- {author[0]} played {author[1]} times.", inline=False)

        await ctx.send(embed=embed)

    else:
        await ctx.send("No songs played yet.")

@client.command()
async def fav(ctx, *, playlistName:str):
    # Check if user ID has already voted.
    # If OK add fav to playlist
    result = _votePlaylist(playlistName, ctx.author.id)

    if result == "NV":
        await ctx.send("You can't vote yet.")
    elif result == "NP":
        await ctx.send(f"No playlist with name {playlistName}.")
    elif result == "OK":
        await ctx.send(f"Voted submited to {playlistName}.") #It now has x stars.
    else:
        await ctx.send("Error.")

@client.command()
async def pls(ctx):
    # Search in database all playlists in the guild.
    result = _listPlaylists()
    if len(result) > 0:
        embed = discord.Embed(title="Playlists.", color=0x2d572c)
        for playlist in result:
            embed.add_field(name="", value=f"`{playlist[0]} - {playlist[1]} ✮`", inline=False)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="No Playlists.", color=0xff0000)
        return await ctx.send(embed=embed)

@client.command()
async def cp(ctx, playlistName: str):
    # Insert in database playlist name.
    result = _createPlaylist(playlistName, ctx.guild.id);
    if result == "Inserted":
        await ctx.send(f"Playlist with name {playlistName} created.")
    elif result.errno == 1062:
        await ctx.send(f"Playlist with name {playlistName} already created in this guild.")
    else:
        await ctx.send(f"Error {result.errno}.")

@client.command()
async def aps(ctx, playlistName: str, *, song: wavelink.YouTubeTrack):
    # Add song to database.
    result = _addPlaylistSong(playlistName, ctx.guild.id, song.title, song.length, song.uri, song.author)
    if result == "Inserted":
        await ctx.send(f"Song with name {song.title} added to Playlist {playlistName}.")
    else:
        await ctx.send(result)

@client.command()
async def pll(ctx, *, playlistName: str):
    result = _getPlaylistSongs(playlistName, ctx.guild.id)

    if len(result) > 0:

        embed = discord.Embed(title=f"Songs in playlist {playlistName}.", color=0xffff00)

        for song in result:
            embed.add_field(name="", value=f"- {song[0]}", inline=False)

        await ctx.send(embed=embed)

    else:
        await ctx.send("No playlist songs")

@client.command()
async def pp(ctx, *, playlistName: str):
    # Search in database all songs within the playlist.
    result = _getPlaylistSongs(playlistName, ctx.guild.id)

    if len(result) > 0:
        vc = ctx.voice_client

        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            embed = discord.Embed(title="Please join a voice channel.", color=0xff0000)
            return await ctx.send(embed=embed)

        if not vc:
            custom_player = CustomPlayer(ctx)
            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
        for song in result:
            await play(ctx, search=await wavelink.YouTubeTrack.search(query=song[0], return_first=True))

@client.command()
async def testSpotify(ctx, *, search):

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': apiSpotify,
    }

    params = {
        'q': '',
        'type': 'track',
        'market': 'ES',
        'limit': '1',
        'offset': '0',
    }

    params["q"] = "track:" + str(search)

    response = requests.get('https://api.spotify.com/v1/search', params=params, headers=headers)

    if response.status_code == 200:
        if "spotify" in response.json()["tracks"]["items"][0]["external_urls"] and response.json()["tracks"]["items"][0]["external_urls"]["spotify"] != "":
            url = response.json()["tracks"]["items"][0]["external_urls"]["spotify"]

            track = await spotify.SpotifyTrack.search(query=url, return_first=True)

            embed = discord.Embed(title="Playing Now", color=0x808080)
            embed.add_field(name="```💿 Track```", value=f"**[{track.title}]({track.uri})**", inline=False)
            embed.add_field(name="```⏱️ Duration```", value=f"**---**", inline=False)
            embed.set_thumbnail(url=response.json()["tracks"]["items"][0]["album"]["images"][0]["url"])

            await ctx.send(embed=embed)

# Add tree command ¿?
@client.command(pass_context = True, aliases=['p', 'Play', 'P'])
async def play(ctx, *, search: wavelink.YouTubeTrack):
    vc = ctx.voice_client

    if not vc:
        custom_player = CustomPlayer(ctx)
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)

    if vc.is_playing():

        vc.queue.append(search)

    else:
        vc.queue.append(search)
        await vc.play(source=search, start=10000, end=search.length - 10000)

        _insertSong(search.title, search.length, search.uri, search.author)

        string = ""

        if search.length > 120:
            string = "**" + str(int(search.length / 60)) + ":"
        elif search.length > 60:
            string = "**1:"
        else:
            string = "**"
        if string == "**":
            string += str(int(search.length % 60)) + "s**"
        else:
            string += str(int(search.length % 60)).zfill(2) + "**"


        embed = discord.Embed(title="Playing Now", color=0x808080)
        embed.add_field(name="```💿 Track```", value=f"**[{search.title}]({search.uri})**", inline=False)
        embed.add_field(name="```⏱️ Duration```", value=f"**{string}**", inline=False)

        view = discord.ui.View(timeout=search.length - 10)

        if vc.itt != 0:
            button1 = discord.ui.Button(
                label="⏮️",
                style=discord.ButtonStyle.secondary,
                custom_id="button1"
            )
            view.add_item(button1)
            button1.callback = last_callback

        button2 = discord.ui.Button(
            label="⏭️ ",
            style=discord.ButtonStyle.secondary,
            custom_id="button2"
        )

        button3 = discord.ui.Button(
            label="⏸️",
            style=discord.ButtonStyle.secondary,
            custom_id="button3"
        )

        view.add_item(button3)
        view.add_item(button2)

        message = await ctx.send(embed=embed, view=view)

        if vc.itt == len(vc.messages):
            vc.messages.append(message)
        else:
            vc.messages[vc.itt] = message

        vc.users[vc.itt] = vc.channel.members
        print(vc.channel.members)

        button3.callback = pause_callback
        button2.callback = skip_callback

@client.command()
async def skip(ctx):
    vc = ctx.voice_client

    if vc:
        if not vc.is_playing():
            return await ctx.send("Nothing is playing.")

        if vc.position < vc.track.duration / 1.5:
            _insertOneLess(vc.track.title, vc.track.author, np.intersect1d([user.id for user in vc.users[vc.itt]], [member.id for member in vc.channel.members]))

        if vc.itt == len(vc.queue) - 1:
            return await vc.stop()

        await vc.seek(vc.track.length * 1000)
        if vc.is_paused():
            await vc.resume()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@client.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc:
        if vc.is_playing() and not vc.is_paused():
            await vc.pause()
        else:
            await ctx.send("Nothing is playing.")
    else:
        await ctx.send("The bot is not connected to a voice channel")


@client.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc:
        if vc.is_paused():
            await vc.resume()
        else:
            await ctx.send("Nothing is paused.")
    else:
        await ctx.send("The bot is not connected to a voice channel")

client.run(bottoken)
