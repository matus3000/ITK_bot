import os
import discord
from discord.ext import commands

TOKEN = os.getenv('TOKEN')
TEST_GUILD = 395970901377548288
TEST_CHANNEL = 1047976941371789345

TK_GUILD = int(os.getenv('TK_GUILD'))
TK_BOT_CHANNEL = 1196192125075869847
TK_EVENT_CHANNEL = 1196192077692805160


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guild_scheduled_events = True

bot = commands.Bot(command_prefix='!', intents=intents)

create_vc_prefix = '🎧🎙'

created_channels = []

guilds_role_update = {TEST_GUILD:[[1196092507294027896, 1196092603838500865], TEST_CHANNEL], TK_GUILD:[[1039656097843265621,1032737020499476530], TK_BOT_CHANNEL]}
guilds_event_update = {TEST_GUILD: TEST_CHANNEL, TK_GUILD: TK_EVENT_CHANNEL}

def get_next_channel_position(channel: discord.VoiceChannel):
    if (channel.category is not None and len(channel.category.channels) > 0):
        return channel.category.channels[len(channel.category.channels) - 1].position + 1
    return 0

import typing
type int_vector = typing.List[int]


def get_tracked_roles_per_guild(guild_id: int) -> int_vector:
    return guilds_role_update[guild_id][0]

def get_channel_for_role_tracking_per_guild(guild_id: int) -> int:
    return guilds_role_update[guild_id][1]

def get_channel_for_event_tracking_per_guild(guild_id: int) -> int:
    return guilds_event_update[guild_id]

@bot.event
async def on_member_update(before: discord.Member, after):
    guild = before.guild
    tracked_roles_id = get_tracked_roles_per_guild(guild.id)
    print(tracked_roles_id)
    channel_id = get_channel_for_role_tracking_per_guild(guild.id)
    if (tracked_roles_id is None or len(tracked_roles_id) == 0):
        return
    removed_roles = []
    added_roles = []
    old_roles_id = list(map(lambda x: x.id, before.roles))
    print(old_roles_id)
    new_roles_id = list(map(lambda x: x.id, after.roles))
    print(new_roles_id)
    for old_role in before.roles:
        if tracked_roles_id.__contains__(old_role.id) and not new_roles_id.__contains__(old_role.id):
            removed_roles.append(old_role)
            print('1')
    for new_role in after.roles:
        if tracked_roles_id.__contains__(new_role.id) and not old_roles_id.__contains__(new_role.id):
            added_roles.append(new_role)
            
    if (len(added_roles) == 0 and len(removed_roles) == 0):
        return
    message = f'{before.display_name} '
    if (len(added_roles) > 0):
        message += f'- has been given following roles {", ".join(list(map(lambda x: x.name, added_roles)))}'
    if (len(removed_roles) > 0):
        message += f'- has been removed from following roles {", ".join(list(map(lambda x: x.name, removed_roles)))}'
    channel = guild.get_channel(channel_id)
    await channel.send(message)

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if (before.channel is not None and before.channel.id in created_channels):
        print(f"Before.id {before.channel.id}, members {len(before.channel.members)}")
        if (len(before.channel.members) == 0):
            print("Removing")
            created_channels.remove(before.channel.id)
            await before.channel.delete()
    if (after.channel is not None and after.channel.name.startswith(create_vc_prefix)):
        guild = member.guild
        position = get_next_channel_position(after.channel)
        category = after.channel.category
        print(f"After channel position {after.channel.position}")
        created_channel = await guild.create_voice_channel(name=f"{member.display_name}'s channel",
                                                            bitrate=guild.bitrate_limit, 
                                                            position = position,
                                                            category = category)
        created_channels.append(created_channel.id)
        await member.move_to(channel=created_channel)
        print(f"Created channel {created_channel.id}")

@bot.event
async def on_scheduled_event_user_add(event: discord.ScheduledEvent, user: discord.User):
    channel_id = get_channel_for_event_tracking_per_guild(event.guild.id)
    msg = f"+ User '{user.display_name}' with discord name: '{user.name}' joined event {event.name} - {event.url}"
    channel = event.guild.get_channel(channel_id)
    await channel.send(msg)
    return 0

@bot.event
async def on_scheduled_event_user_remove(event, user):
    channel_id = get_channel_for_event_tracking_per_guild(event.guild.id)
    msg = f"- User '{user.display_name}' with discord name: '{user.name}' left event {event.name} - {event.url}"
    channel = event.guild.get_channel(channel_id)
    await channel.send(msg)
    return 0

bot.run(TOKEN)