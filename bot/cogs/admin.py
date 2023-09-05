from discord import Embed
from discord.ext import commands


class Admin(commands.Cog, name="Admin"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="reload", hidden=True)
    async def reload(self, ctx, extension=None):
        if extension is None:
            for cog in self.client.extensions.copy():
                await self.client.unload_extension(cog)
                await self.client.load_extension(cog)
            print(f"Reload Command Executed by {ctx.author}")
            embed = Embed(
                title="Cog Reload 🔃",
                description="I have reloaded all the cogs successfully ✅",
                color=0x00FF00,
                timestamp=ctx.message.created_at,
            )
            embed.add_field(name="Requested by:", value=f"<@!{ctx.author.id}>")
            await ctx.send(embed=embed)
        else:
            print(
                f"Reloaded: {str(extension).upper()} COG - Command Executed by {ctx.author}"
            )
            await self.client.unload_extension(f"cogs.{extension}")
            await self.client.load_extension(f"cogs.{extension}")
            embed = Embed(
                title="Cog Reload 🔃",
                description=f"I have reloaded the **{str(extension).upper()}** cog successfully ✅",
                color=0x00FF00,
                timestamp=ctx.message.created_at,
            )
            embed.add_field(name="Requested by:", value=f"<@!{ctx.author.id}>")
            await ctx.send(embed=embed)

    @commands.command(name="sync", hidden=True)
    async def sync(self, ctx: commands.Context):
        await self.client.tree.sync()
        print(f"Sync Command Executed by {ctx.author}")
        embed = Embed(
            title="Command Sync 🌳",
            description="Successfully Synced Commands ✅",
            color=0x00FF00,
            timestamp=ctx.message.created_at,
        )
        await ctx.send(embed=embed)

    @commands.command(name="purge", hidden=True)
    async def purge(self, ctx: commands.Context, amount: int, reason: str = None):
        if amount <= 0:
            await ctx.send("Please specify a positive number of messages to delete.")
            return
        try:
            amount += 1
            await ctx.channel.purge(limit=amount, reason=reason)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("An error occurred while purging messages.", ephemeral=True)
            return
        message = await ctx.send("I have purged those messages for you.")
        await message.delete(delay=3)


async def setup(client):
    await client.add_cog(Admin(client))
