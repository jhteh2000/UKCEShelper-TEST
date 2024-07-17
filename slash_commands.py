import discord, asyncio, datetime
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from daily_courses_posting import post_daily_course
from transport_clearing import clear_transport
from driver import launch_driver
from zoneinfo import ZoneInfo


class MCGame(app_commands.Group):
    def __init__(self):
        super().__init__(name="mc", description="MissionChief")

    @app_commands.command(name="test", description="This is a test command")
    @app_commands.checks.has_any_role(
        "UKCES Administration", "UKCES Team Leaders", "UKCES Co-Administration"
    )
    async def slash(self, interaction: discord.Interaction, message: str):
        match message:
            case "1":
                await interaction.response.send_message(
                    "[TEST] :white_check_mark: A posted on B"
                )
            case "2":
                await interaction.response.send_message(
                    "[TEST] :warning: Error posting A on B"
                )
            case "3":
                await interaction.response.send_message(
                    "[TEST] :white_check_mark: Daily courses have been posted successfully :white_check_mark:"
                )
            case "4":
                await interaction.response.send_message(
                    "[TEST] :warning: There are some errors in posting the daily courses :warning:"
                )
            case "browser":
                await interaction.response.send_message("[TEST] Opening browser...")

                try:
                    driver = await launch_driver()
                    await interaction.channel.send(content="Browser opened")
                except:
                    await interaction.channel.send(content="Failed to open browser")

                await asyncio.sleep(10)

                try:
                    driver.quit()
                    await interaction.channel.send(content="Browser closed")
                except:
                    await interaction.channel.send(content="Failed to close browser")

                await interaction.channel.send(content="Test complete")
            case _:
                await interaction.response.send_message(
                    f"[TEST] The message you have entered is: {message}"
                )

    @app_commands.command(name="postcourse", description="Post daily courses")
    @app_commands.describe(days="Day to post", services="Service to post")
    @app_commands.choices(
        days=[
            Choice(name="Monday", value=1),
            Choice(name="Tuesday", value=2),
            Choice(name="Wednesday", value=3),
            Choice(name="Thursday", value=4),
            Choice(name="Friday", value=5),
            Choice(name="Saturday", value=6),
            Choice(name="Sunday", value=7),
        ],
        services=[
            Choice(name="EMS", value=1),
            Choice(name="Police", value=2),
            Choice(name="Fire", value=3),
            Choice(name="Lifeboat", value=4),
            Choice(name="ALL", value=5),
        ],
    )
    @app_commands.checks.has_any_role(
        "UKCES Administration", "UKCES Team Leaders", "Education Team"
    )
    async def post_course(
        self, interaction: discord.Interaction, days: Choice[int], services: Choice[int]
    ):
        await interaction.response.send_message(
            f"Posting {days.name} {services.name} courses..."
        )
        if services.name == "ALL":
            await interaction.channel.send("Posting EMS...")
            await post_daily_course(interaction, days.name, "EMS")
            await asyncio.sleep(2)

            await interaction.channel.send("Posting Police...")
            await post_daily_course(interaction, days.name, "Police")
            await asyncio.sleep(2)

            await interaction.channel.send("Posting Fire...")
            await post_daily_course(interaction, days.name, "Fire")
            await asyncio.sleep(2)

            await interaction.channel.send("Posting Lifeboat...")
            await post_daily_course(interaction, days.name, "Lifeboat")
        else:
            await post_daily_course(interaction, days.name, services.name)

    @app_commands.command(name="cleartp", description="Clear transport")
    @app_commands.describe(mission_url="Link of the mission for clearing transport")
    @app_commands.checks.has_any_role(
        "UKCES Administration", "UKCES Team Leaders", "UKCES Co-Administration"
    )
    async def clear_transport(self, interaction: discord.Interaction, mission_url: str):
        await interaction.response.send_message(
            "[EARLY STAGE] This currently only works for patient transport and only if all the units are offline\nClearing transport..."
        )
        # mission_url = mission_url.replace("police.", "")
        await clear_transport(interaction, mission_url)


class AutoTasks(commands.GroupCog, name="auto", description="Auto Tasks"):
    def __init__(self):
        self.auto_tasks_status = {"Daily courses posting": False}
        self.post_course_interaction = None
        self.post_course_task.stop()
        pass

    @app_commands.command(name="status", description="All auto tasks status")
    @app_commands.checks.has_any_role(
        "UKCES Administration", "UKCES Team Leaders", "UKCES Co-Administration"
    )
    async def status(self, interaction: discord.Interaction):
        status_message = "```\n"
        status_message += "----------------------------------------\n"
        status_message += "          Auto Tasks Status\n"
        status_message += "----------------------------------------\n"
        for task, status in self.auto_tasks_status.items():
            status_message += f"{task}: {'On' if status else 'Off'}\n"
        status_message += "```\n"
        await interaction.response.send_message(status_message)

    @app_commands.command(
        name="postcourse", description="Auto post daily courses on midnight"
    )
    @app_commands.choices(
        option=[Choice(name="off", value=0), Choice(name="on", value=1)]
    )
    @app_commands.checks.has_any_role(
        "UKCES Administration", "UKCES Team Leaders", "Education Team"
    )
    async def post_course(self, interaction: discord.Interaction, option: Choice[int]):
        if option.name == "on":
            if self.post_course_task.is_running():
                await interaction.response.send_message(
                    "Auto daily courses posting is already ON."
                )
            else:
                await interaction.response.send_message("Auto daily courses posting ON")
                self.auto_tasks_status["Daily courses posting"] = True
                self.post_course_interaction = interaction
                self.post_course_task.start()
        else:
            if self.post_course_task.is_running():
                await interaction.response.send_message(
                    "Auto daily courses posting OFF"
                )
                self.auto_tasks_status["Daily courses posting"] = False
                self.post_course_task.stop()
            else:
                await interaction.response.send_message(
                    "Auto daily courses posting is already OFF."
                )

    timezone = ZoneInfo("Europe/London")
    post_course_schedule = datetime.time(hour=0, minute=0, tzinfo=timezone)

    @tasks.loop(time=post_course_schedule)
    async def post_course_task(self):
        interaction = self.post_course_interaction

        today = datetime.datetime.now().strftime("%A")
        await interaction.channel.send(f"Auto posting {today} courses...")

        await interaction.channel.send(":ambulance: Posting EMS...")
        await post_daily_course(interaction, today, "EMS")
        await asyncio.sleep(2)

        await interaction.channel.send(":police_car: Posting Police...")
        await post_daily_course(interaction, today, "Police")
        await asyncio.sleep(2)

        await interaction.channel.send(":fire_engine: Posting Fire...")
        await post_daily_course(interaction, today, "Fire")
        await asyncio.sleep(2)

        await interaction.channel.send(":motorboat: Posting Lifeboat...")
        await post_daily_course(interaction, today, "Lifeboat")
