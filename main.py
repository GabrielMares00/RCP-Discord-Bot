import aiohttp
import discord
import io
import requests

from discord.ext import commands

bot = commands.Bot(command_prefix="pcd.", case_insensitive=True)


def algo_to_int(algorithm_code):
    match algorithm_code:
        case "MD5":
            return 0
        case "SHA1":
            return 1
        case "SHA224":
            return 2
        case "SHA256":
            return 3
        case "SHA384":
            return 4
        case "SHA512":
            return 5
        case _:
            return -1


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def commands(ctx):
    await ctx.send("Prefix for all commands is pcd.\n"
                   "Example: pcd.commands will spawn this wall of text\n"

                   "----------------------------\n"
                   "Simple commands:\n"
                   "pcd.commands - shows this help text\n"
                   "pcd.algorithms - shows available algorithms to generate checksums with\n"
                   "pcd.parrot **message** - make the bot repeat your words\n"

                   "----------------------------\n"
                   "Checksum commands:\n"
                   "pcd.generateChecksum **algorithm** - generates a checksum for a file via a given algorithm\n"
                   "pcd.verifyChecksum **checksum** **algorithm** - verifies the checksum of a given file via a "
                   "checksum and the algorithm used for said checksum")


@bot.command()
async def algorithms(ctx):
    await ctx.send("Available algorithms: MD5, SHA1, SHA224, SHA256, SHA384, SHA512")


@bot.command()
async def generateChecksum(ctx, algorithm):
    algorithm_code = algo_to_int(algorithm.upper())

    if algorithm_code == -1:
        await ctx.send("Invalid algorithm. Use pcd.algorithms for a list of available algorithms")

    else:
        message_user = ctx.message.author.mention
        await ctx.send('{0}: Send a file to generate its checksum via algorithm {1}'.format(message_user, algorithm))

        message = await bot.wait_for("message")

        if message.attachments:
            file_url = str(message.attachments[0])

            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status != 200:
                        return await ctx.send('Could not download file...')

                    data = io.BytesIO(await response.read())

                    url = "https://setrofex.tk/checksum"
                    payload = {
                        'algorithm': algorithm_code
                    }
                    files = [('file_parameter', data)]
                    headers = {}

                    response = requests.request("POST", url, headers=headers, data=payload, files=files)
                    # print("DEBUG_PRINT: CHECKSUM {0}".format(response.text))

                    await ctx.send("{0}: The checksum generated via {1} for your file is: {2}".format(
                        message_user, algorithm, response.text))
        elif message.content == 'cancel':
            await ctx.send("Cancelling...")
        else:
            await ctx.send("I need a file to actually do this man")


@bot.command()
async def verifyChecksum(ctx, algorithm, checksum):
    algorithm_code = algo_to_int(algorithm.upper())

    if algorithm_code == -1:
        await ctx.send("Invalid algorithm. Use pcd.algorithms for a list of available algorithms")

    else:
        message_user = ctx.message.author.mention
        await ctx.send('{0}: Verifying with algorithm {1} checksum {2}'.format(message_user, algorithm, checksum))

        message = await bot.wait_for("message")

        if message.attachments:
            file_url = str(message.attachments[0])

            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status != 200:
                        return await ctx.send('Could not download file...')

                    data = io.BytesIO(await response.read())

                    url = "https://setrofex.tk/verify_checksum"
                    payload = {
                        'algorithm': algorithm_code,
                        'checksum': checksum
                    }
                    files = [('file_parameter', data)]
                    headers = {}

                    response = requests.request("POST", url, headers=headers, data=payload, files=files)
                    # print("DEBUG_PRINT: OK OR NOK {0}".format(response.text))

                    if response.text == "OK":
                        await ctx.send("{0}: The checksum matches your sent file".format(message_user))
                    else:
                        await ctx.send(
                            "{0}: Checksum DOES NOT match!"
                            " There can be multiple cause for this, like a corrupt file, a server error,"
                            " or you simply sent the wrong file".format(
                                message_user))
        elif message.content == 'cancel':
            await ctx.send("Cancelling...")
        else:
            await ctx.send("I need a file to actually do this man")


@bot.command()
async def parrot(ctx, *, arg):
    await ctx.send(arg)


bot.activity = discord.Game(name="It all starts with pcd.commands")
bot.run('insert your key here')
