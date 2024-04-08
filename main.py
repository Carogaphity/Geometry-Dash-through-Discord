import os, time
from dotenv import load_dotenv

import discord


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


game_states = []

intents = discord.Intents.default()
intents.message_content = True


import logging

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

client = discord.Client(intents=intents)


emoji_dict = {
    "🟦": "<:bg:1226622165236056226>",
    ".": "<:bg:1226622165236056226>",
    "^": "<:spike:1226622178712096860>",
    "🔺": "<:spike:1226622178712096860>",
    "⬛": "<:ground:1226622599111376948>",
    "-": "<:ground:1226622599111376948> ",
    "🟧": "<:player:1226622170554171403>",
    "🏁": ":pause_button:",
    " ": "???"
}


cmd = "GD-"


def create_level():

    global emoji_dict

    level = """
  🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🏁
  🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🏁
  🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🏁
  🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🏁
  🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🏁
  🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🏁
  🟦🟦🟧🟦🟦🟦🔺🔺🟦🟦🟦🟦🟦⬛⬛⬛⬛🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🏁
  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🏁
  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🏁
  """

    # Splits the level into rows
    rows = level.strip().split("\n")

    # Creates a list of lists, where each sublist is a row of emojis (string of chr)
    chr_list = []
    for string in rows:
        spritelist = [emoji_dict[char] for char in string if char in emoji_dict]
        chr_list.append(list(spritelist))

    # Finds player spawn position
    p_pos = [1, 1]
    for row in chr_list:
        if "<:player:1226622170554171403>" in row:
            p_pos = [row.index("<:player:1226622170554171403>"), chr_list.index(row)]
        chr_list[p_pos[0]][p_pos[1]] = "<:bg:1226622165236056226>"

        # return list of lists and player's default position
    return chr_list, p_pos


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_reaction_add(reaction, user):
    global game_states

    # Ignore reactions from the bot itself
    if user == client.user:
        return

    game_index = next(
        index for index, sublist in enumerate(game_states) if user.id in sublist
    )

    # Check if the reaction is related to an ongoing game
    if user.id in game_states[game_index]:

        # Check if the reaction is the jump reaction
        if str(reaction.emoji) == "\U0001F53C":

            # Set the jump variable in the game state
            game_states[game_index][1] = True

            # Remove the reaction so the user can react again
            await reaction.remove(user)


@client.event
async def on_message(message):
    global cmd
    global game_states

    if message.author == client.user:
        return
    if message.content.startswith(cmd + "play"):

        if (message.author.id not in a for a in game_states):
            # If not, create a new game state
            game_states.append([message.author.id, False])

        board, player_pos = create_level()
        new_frame = ""

        start_col = player_pos[0] - 2
        end_col = player_pos[0] + 4

        for row in board:
            new_frame += "".join(row[start_col:end_col]) + "\n"

        embed = discord.Embed(
            title="Geometry Dash", description=new_frame, color=discord.Color.green()
        )
        embed.add_field(name=f"Started by {message.author}", value="", inline=True)

        bot_message = await message.channel.send(embed=embed)
        await bot_message.add_reaction("\U0001F53C")

        play = True

        game_index = next(
            index
            for index, sublist in enumerate(game_states)
            if message.author.id in sublist
        )

        jumped = 0

        while play:

            time.sleep(0.4)

            # Checks if the player has ground under them``
            if board[player_pos[1] + 1][player_pos[0]] == "<:ground:1226622599111376948>":
                jumped = 0

            # If the player wants to jump and there's ground below them, jump.
            if (
                game_states[game_index][1]
                and board[player_pos[1] + 1][player_pos[0]] == "<:ground:1226622599111376948>"
            ):
                print("jumped")
                player_pos[1] -= 1
                jumped = 1
                game_states[game_index][1] = False

            # If player is not on ground and is not jumping, moves player down
            if board[player_pos[1] + 1][player_pos[0]] != "<:ground:1226622599111376948>" and jumped == 0:
                player_pos[1] += 1

            # Checks if the player touches a flag
            if board[player_pos[1]][player_pos[0]] == ":pause_button:":
                embed = discord.Embed(
                    title="Geometry Dash",
                    description="**You win!**",
                    color=discord.Color.green(),
                )
                embed.add_field(
                    name=f"Started by {message.author}", value="", inline=True
                )
                await bot_message.edit(embed=embed)
                await bot_message.remove_reaction("\U0001F53C", client.user)
                play = False
                break

            # Checks if the player crashes
            elif board[player_pos[1]][player_pos[0]] in ["<:spike:1226622178712096860>", "<:ground:1226622599111376948>"]:
                embed = discord.Embed(
                    title="Geometry Dash",
                    description="**You lose!**",
                    color=discord.Color.green(),
                )
                embed.add_field(
                    name=f"Started by {message.author}", value="", inline=True
                )
                await bot_message.edit(embed=embed)
                await bot_message.remove_reaction("\U0001F53C", client.user)
                play = False
                break

            # Changes player's printed position
            board[player_pos[1]][player_pos[0]] = "<:playerRotate:1226622172131364984>" if jumped != 0 else "<:player:1226622170554171403>"

            # Checks how far along a jump is at
            if jumped == 1:
                jumped = 2
            elif jumped == 2:
                jumped = 0

            # Defines which parts of the level should be printed
            start_col = player_pos[0] - 2
            end_col = player_pos[0] + 4

            new_frame = ""
            for row in board:
                new_frame += "".join(row[start_col:end_col]) + "\n"

            embed = discord.Embed(
                title="Geometry Dash",
                description=new_frame,
                color=discord.Color.green(),
            )
            embed.add_field(name=f"Started by {message.author}", value="", inline=True)

            await bot_message.edit(embed=embed)

            # Deletes old player model
            board[player_pos[1]][player_pos[0]] = "<:bg:1226622165236056226>"

            # Moves player on x-axis
            player_pos[0] += 1

            # Defines framerate

    elif message.content.startswith(cmd + "changePrefix"):
        cmd = str(message.content).replace(cmd + "changePrefix ", "")
        if cmd == "" or " " in cmd or len(cmd) > 3:
            await message.channel.send("Invalid prefix!")
            return
        else:
            await message.channel.send(f"Prefix changed to `{cmd}`!")

    elif message.content.startswith(cmd + "help"):
        await message.channel.send(
            "# Commands\n - `changePrefix`: Changes the prefix command.\n - `Play:` Starts a game."
        )


client.run(TOKEN)
