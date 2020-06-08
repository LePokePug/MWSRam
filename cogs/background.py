
# Lib
from asyncio import sleep
from datetime import datetime
from os.path import exists
from pickle import dump

# Site
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.ext.commands.cog import Cog
from discord.ext.tasks import loop

# Local
from utils.classes import Bot


class BackgroundTasks(Cog):
    """Background loops"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.dblpy = self.bot.connect_dbl()
        self.savetofile.start()
        self.status_change.start()

    @loop(seconds=60)
    async def status_change(self):
        if self.bot.TimeZone != "UTC":
            hour = str(datetime.now().hour)
            minute = str(datetime.now().minute)
            if len(hour) == 1:
                hour = "0" + hour
            if len(minute) == 1:
                minute = "0" + minute
            time = f"{hour}:{minute}"
        else:
            utchour = str(datetime.utcnow().hour)
            utcminute = str(datetime.utcnow().minute)
            if len(utchour) == 1:
                utchour = "0" + utchour
            if len(utcminute) == 1:
                utcminute = "0" + utcminute
            time = f"{utchour}:{utcminute}"

        if self.bot.univ.Inactive >= 5:
            status = Status.idle
        else:
            status = Status.online

        if self.bot.debug_mode:
            activity = Activity(type=ActivityType.playing, name="IN DEBUG MODE")
        elif self.bot.univ.DisableSaving:
            activity = Activity(type=ActivityType.listening, name=f"SAVING DISABLED")
        else:
            activity = Activity(
                type=ActivityType.watching,
                name=f"{self.bot.command_prefix}help | {self.bot.tz}: {time}"
            )

        await self.bot.change_presence(status=status, activity=activity)

    @loop(seconds=60)
    async def savetofile(self):
        hour = str(datetime.now().hour)
        minute = str(datetime.now().minute)
        date = str(str(datetime.now().date().month) + "/" + str(datetime.now().date().day) + "/" + str(
            datetime.now().date().year))
        if len(hour) == 1:
            hour = "0" + hour
        if len(minute) == 1:
            minute = "0" + minute
        time = f"{hour}:{minute}, {date}"

        if not exists(f"{self.bot.cwd}\\Serialized\\data.pkl") and not self.bot.univ.DisableSaving:
            self.bot.univ.DisableSaving = True
            print(
                f"[{time} || Unable to save] data.pkl not found. Replace file before shutting down. Saving disabled."
            )
            return

        elif exists(f"{self.bot.cwd}\\Serialized\\data.pkl") and self.bot.univ.DisableSaving:
            self.bot.univ.DisableSaving = False
            print(f"[{time}] Saving re-enabled.")
            return

        if not self.bot.univ.DisableSaving:
            print("Saving...", end="\r")
            with open(f"{self.bot.cwd}\\Serialized\\data.pkl", "wb") as f:
                try:
                    data = {
                        "VanityAvatars": self.bot.univ.VanityAvatars,
                        "Blacklists": self.bot.univ.Blacklists,
                        "Closets": self.bot.univ.Closets,
                        "ServerBlacklists": self.bot.univ.ServerBlacklists,
                        "ChangelogCache": self.bot.univ.ChangelogCache
                    }

                    dump(data, f)
                except Exception as e:
                    print(f"[{time} || Unable to save] Pickle dumping Error:", e)

            self.bot.univ.Inactive = self.bot.univ.Inactive + 1
            print(f"[VPP: {time}] Saved data.")

    @status_change.before_loop
    async def wait(self):
        await self.bot.wait_until_ready()
        await sleep(60)

def setup(bot: Bot):
    bot.add_cog(BackgroundTasks(bot))
