from __future__ import annotations

import os
import time
from io import BytesIO

from discord import (
    Embed,
    File,
    Interaction,
    Message,
    app_commands,
    ui,
    Attachment,
    Colour,
)
from discord.ext import commands
from openai import AsyncOpenAI

from .utils import gpt
from .utils.lists import ai_ban_words


class Download(ui.View):
    def __init__(self, url: str):
        super().__init__()
        self.add_item(ui.Button(label="Download your image here!", url=url))


class Ai(commands.Cog, name="Ai"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.openai_token: str = os.getenv("OPENAI_TOKEN")
        self.openai_gateway_url: str = os.getenv("CLOUDFLARE_AI_GATEWAY_URL")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.client.user:
            return

        if self.client.user.mentioned_in(message):
            name = message.author.nick if message.author.nick else message.author.name
            client = AsyncOpenAI(
                api_key=self.openai_token, base_url=self.openai_gateway_url
            )
            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": gpt.about_text
                        + f"when you answer someone, answer them by {name}",
                    },
                    {
                        "role": "user",
                        "content": message.content.strip(f"<@!{self.client.user.id}>"),
                    },
                ],
                model="gpt-4-1106-preview",
            )
            await message.channel.typing()
            await message.channel.send(chat_completion.choices[0].message.content)

    @app_commands.command(
        name="imagine", description="Generate an image using StabilityAI"
    )
    @app_commands.guild_only()
    async def imagine(self, interaction: Interaction, prompt: str) -> None:
        if any(word in prompt for word in ai_ban_words):
            await interaction.response.send_message(
                "Your prompt contains a banned word. Please try again."
            )
            return

        await interaction.response.send_message(
            content=f"**{prompt}** - {interaction.user.mention} <a:utility6:1174820977708904559>"
        )

        url: str = "https://mecha-muse.twizy.workers.dev/"
        data: dict = {"prompt": prompt}
        start_time = time.time()
        image_data = await self.client.session.post(url=url, json=data)

        if image_data.status == 200:
            self.client.log.info(
                f"Image generated generated by {interaction.user.name} with prompt: {prompt}"
            )

            image: bytes = await image_data.read()
            ray_id: str = image_data.headers["CF-RAY"].split("-")[0]

            try:
                with BytesIO(image) as image_binary:
                    image_file: File = File(fp=image_binary, filename=f"{ray_id}.png")

            except Exception as e:
                self.client.log.error(f"Error generating image: {e}")
                await interaction.edit_original_response(
                    f"An error occurred during generation. This has been reported to the developers - {interaction.user.mention}"
                )
                return
            elapsed_time = time.time() - start_time
            embed = Embed()
            embed.title = "Result for your prompt"
            embed.colour = Colour.blurple()
            embed.description = f"```{prompt}```"
            embed.set_image(url=f"attachment://{ray_id}.png")
            embed.set_footer(text=f"Took {elapsed_time:.2f}s")
            await interaction.edit_original_response(
                embed=embed,
                attachments=[image_file],
                view=Download(url=f"https://i.konikotaka.dev/{ray_id}.png"),
            )
        else:
            self.client.log.error(f"Error generating image: {image_data.status}")
            await interaction.edit_original_response(
                f"An error occurred during generation. This has been reported to the developers - {interaction.user.mention}"
            )

    @app_commands.command(
        name="describe", description="Describe an image using MicrosoftAI"
    )
    @app_commands.guild_only()
    async def describe(self, interaction: Interaction, photo: Attachment) -> None:
        await interaction.response.defer()
        url = f"{os.getenv('CLOUDFLARE_AI_URL')}/@cf/microsoft/resnet-50"
        headers = {"Authorization": f"Bearer {os.getenv('CLOUDFLARE_AI_TOKEN')}"}
        try:
            image_binary = await photo.read()
        except Exception as e:
            self.client.log.error(f"Error reading image: {e}")
            await interaction.edit_original_response(
                content="An error occurred while reading your image"
            )
            return
        if len(image_binary) > 4_000_000:
            await interaction.edit_original_response(
                content="Your image is too large. Please try again with an image smaller than 4MB"
            )
            return
        start_time = time.time()
        response = await self.client.session.post(
            url=url, headers=headers, data=image_binary
        )
        if response.status == 200:
            data = await response.json()
            image_description = data["result"]
            embed = Embed()
            embed.title = "Image Description"
            embed.colour = Colour.blurple()
            description = ""
            for i in image_description:
                description += f"Label: **{i['label']}** Score: **{round(i['score'] * 100, 2)}**\n\n"

            embed.description = description
            embed.set_image(url=photo.url)
            elapsed_time = time.time() - start_time
            embed.set_footer(text=f"Took {elapsed_time:.2f}s")
            await interaction.edit_original_response(embed=embed)
        else:
            self.client.log.error(
                f"Error describing image: {response.status} {response.reason}"
            )
            await interaction.edit_original_response(
                content="An error occurred while describing your image"
            )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Ai(client))