import random
from inspect import getsourcelines
from typing import Literal
import asyncio

import upsidedown
from discord import app_commands, Embed, Member
from discord.ext import commands


class Fun(commands.Cog, name="Fun"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.hybrid_command(
        name="cosmo", help="Get a random Photo of Cosmo the Cat", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def cosmo_photo(self, ctx: commands.Context) -> None:
        """
        Get a random photo of Cosmo the Cat from the twizy.dev API
        """
        async with self.client.session.get("https://api.twizy.dev/cosmo") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Cosmo!")

    @commands.hybrid_command(
        name="bczs",
        help="Get a random photo of Pat and Ash's cats",
        with_app_command=True,
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def bczs_photos(self, ctx: commands.Context) -> None:
        """
        Get a random photo of Pat and Ash's cats from the twizy.dev API
        """
        async with self.client.session.get("https://api.twizy.dev/bczs") as response:
            if response.status == 200:
                photo = await response.json()
                await ctx.send(photo["photoUrl"])
            else:
                await ctx.send("Error getting photo of Pat and Ash's cats!")

    @commands.hybrid_command(
        name="meme", help="Get a random meme!", with_app_command=True
    )
    @commands.guild_only()
    async def get_meme(self, ctx: commands.Context) -> None:
        """
        Get a random meme from the meme-api.com API
        """
        async with self.client.session.get("https://meme-api.com/gimme") as response:
            if response.status == 200:
                meme = await response.json()
                await ctx.send(meme["url"])
            else:
                await ctx.send("Error getting meme!")

    @commands.hybrid_command(
        name="gcattalk", help="Be able to speak with G Cat", with_app_command=True
    )
    @commands.guild_only()
    @app_commands.guild_only()
    async def gcat_talk(self, ctx: commands.Context, *, message: str) -> None:
        """
        Translate your message into G Cat's language
        """
        up_down = upsidedown.transform(message)
        await ctx.send(up_down)

    @commands.hybrid_command(name="waifu", aliases=["getwaifu"])
    @commands.guild_only()
    @app_commands.guild_only()
    async def get_waifu(
        self,
        ctx: commands.Context,
        category: Literal["waifu", "neko", "shinobu", "megumin", "bully", "cuddle"],
    ) -> None:
        """
        Get a random waifu image from the waifu API
        """
        response = await self.client.session.get(
            f"https://api.waifu.pics/sfw/{category}"
        )
        if response.status == 200:
            waifu = await response.json()
            await ctx.send(waifu["url"])
        else:
            await ctx.send("Error getting waifu!")

    @commands.command(name="inspect")
    async def inspect(self, ctx, *, command_name: str) -> None:
        """
        Print a link and the source code of a command
        """
        cmd = self.client.get_command(command_name)
        if cmd is None:
            return
        module = cmd.module
        saucelines, startline = getsourcelines(cmd.callback)
        url = (
            "<https://github.com/alexraskin/WiseOldManBot/blob/main/bot"
            f'{"/".join(module.split("."))}.py#L{startline}>\n'
        )
        sauce = "".join(saucelines)
        sanitized = sauce.replace("`", "\u200B`")
        if len(url) + len(sanitized) > 1950:
            sanitized = sanitized[: 1950 - len(url)] + "\n[...]"
        await ctx.send(url + f"```python\n{sanitized}\n```")

    @commands.command(name="cat", description="Get a random cat image")
    async def cat(self, ctx: commands.Context):
        """
        Get a random cat image from the catapi
        """
        base_url = "https://cataas.com"
        response = await self.client.session.get(f"{base_url}/cat?json=true")
        if response.status != 200:
            return await ctx.send("Error getting cat!")
        response = await response.json()
        url = response["url"]
        await ctx.send(f"{base_url}{url}")

    @commands.hybrid_command(name="roll", description="Roll a dice with NdN")
    @commands.guild_only()
    @app_commands.guild_only()
    async def roll(self, ctx: commands.Context, dice: str) -> Embed:
        """
        Roll a dice
        """
        dice = dice.strip()
        try:
            rolls, limit = map(int, dice.split("d"))
        except Exception:
            return await ctx.send("Format has to be in NdN!\n(e.g. 1d20)")
        result = ", ".join(str(random.randint(1, limit)) for r in range(rolls))
        embed = Embed(
            title="🎲 Roll Dice",
            description=f"{ctx.author.name} threw a **{result}** ({rolls}-{limit})",
            color=0x2ECC71,
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="8ball", description="Ask the magic 8ball a question")
    @commands.guild_only()
    @app_commands.guild_only()
    async def eight_ball(self, ctx: commands.Context, question: str) -> Embed:
        """
        Ask the magic 8ball a question
        """
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes – definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        embed = Embed(
            title="🎱 8ball",
            description=f"Question: {question}\nAnswer: {random.choice(responses)}",
            color=0x2ECC71,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"{ctx.author}")
        await ctx.send(embed=embed)
  
    @commands.hybrid_command(name="reverse", description="Reverse a string")
    @commands.guild_only()
    @app_commands.guild_only()
    async def reverse(self, ctx: commands.Context, string: str) -> Embed:
        """
        Reverse a string
        """
        embed = Embed(
            title="🔁 Reverse",
            description=f"String: {string}\nReversed: {string[::-1]}",
            color=0x2ECC71,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"{ctx.author}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="say", description="Make the bot say something")
    @commands.guild_only()
    @app_commands.guild_only()
    async def say(self, ctx: commands.Context, message: str) -> None:
        """
        Make the bot say something
        """
        await ctx.send(message)
    
    @commands.hybrid_command(name="embed", description="Make the bot say something in an embed")
    @commands.guild_only()
    @app_commands.guild_only()
    async def _embed(self, ctx: commands.Context, message: str) -> Embed:
        """
        Make the bot say something in an embed
        """
        embed = Embed(
            title="📝 Embed",
            description=f"{message}",
            color=0x2ECC71,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"{ctx.author}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="hug", description="Hug someone")
    @commands.guild_only()
    @app_commands.guild_only()
    async def hug(self, ctx: commands.Context, member: Member) -> Embed:
        """
        Hug someone
        """
        embed = Embed(
            title="🫂 Hug",
            description=f"{ctx.author.mention} hugged {member.mention} 😊",
            color=0x2ECC71,
            timestamp=ctx.message.created_at
        )
        embed.set_image(url="https://media.tenor.com/b3Qvt--s_i0AAAAC/hugs.gif")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="slap", description="Slap someone")
    @commands.guild_only()
    @app_commands.guild_only()
    async def slap(self, ctx: commands.Context, member: Member) -> Embed:
        """
        Slap someone
        """
        embed = Embed(
            title="👊 Slap",
            description=f"{ctx.author.mention} slapped {member.mention} 😡",
            color=0x2ECC71,
            timestamp=ctx.message.created_at
        )
        embed.set_image(url="https://media.tenor.com/XiYuU9h44-AAAAAC/anime-slap-mad.gif")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="slots", description="Play the slots")
    @commands.guild_only()
    @app_commands.guild_only()
    async def slots(self, ctx: commands.Context) -> Embed:
      emojis = ["🍒", "🍊", "🍋", "🍇", "🍉", "🍎"]
      embed = Embed(title="🎰 Slot Machine", color=0x00ff00)
      embed.add_field(name="⠀★彡 𝚂𝙻𝙾𝚃 𝙼𝙰𝙲𝙷𝙸𝙽𝙴 ★彡\n", value=f"{random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)}\n\n")
      message = await ctx.reply(embed=embed)
      # Spin the slots
      for _ in range(3):
          await asyncio.sleep(1)  # Delay for a second to simulate spinning
          slot1 = random.choice(emojis)
          slot2 = random.choice(emojis)
          slot3 = random.choice(emojis)
          
          # Update the embed with spinning slots
          embed.set_field_at(0, name="⠀★彡 𝚂𝙻𝙾𝚃 𝙼𝙰𝙲𝙷𝙸𝙽𝙴 ★彡\n", value=f"{slot1} {slot2} {slot3}\n\n")
          await message.edit(embed=embed)
          print("hello3")
      
      # Check if the player wins or loses
      if slot1 == slot2 == slot3:
          result = "You won! 🎉"
      else:
          result = "You lost. 💥"
      
      # Update the embed with the final result
      embed.set_field_at(0, name="⠀★彡 𝚂𝙻𝙾𝚃 𝙼𝙰𝙲𝙷𝙸𝙽𝙴 ★彡\n", value=f"\n{slot1} {slot2} {slot3}\n\n{result}")
      await message.edit(embed=embed)
      print("hello4")
  
    @commands.hybrid_command(name="coinflip", description="Flip a coin")
    @commands.guild_only()
    @app_commands.guild_only()
    async def coinflip(self, ctx: commands.Context) -> Embed:
      result = random.choice(["Heads", "Tails"])
      embed = Embed(
            title="🪙 Coinflip",
            description=f"{ctx.author.mention} flipped a coin and got **{result}**",
            color=0x2ECC71,
            timestamp=ctx.message.created_at
        )
      await ctx.send(embed=embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Fun(client))
