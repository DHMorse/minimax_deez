import discord
from discord.ext import commands
import csv
import json
import os
import asyncio
import random
import time
import math
import requests
from PIL import Image, ImageDraw, ImageFont
import re

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

CACHE_DIR = '/home/egglessnoob/Desktop/profile_pictures_cache'
# Global variable for the file path
MONEY_JSON_FILEPATH = '/home/egglessnoob/Desktop/money.json'
LICHESS_JSON_FILEPATH = '/home/egglessnoob/Desktop/lichess_accounbts.json'
LICHESS_API_URL = 'https://lichess.org/api/user/'

# Override the default help command
bot.remove_command('help')  # Remove the default help command


# Function to load money data from money.json
def load_money_data():
    try:
        with open(MONEY_JSON_FILEPATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Function to save money data to money.json
def save_money_data(money_data):
    with open(MONEY_JSON_FILEPATH, 'w') as f:
        json.dump(money_data, f, indent=4)

# Function to read money balances from money.json
def read_money_balances():
    return load_money_data()

# Function to update money balance in money.json
def update_money_balance(money_balances):
    save_money_data(money_balances)

# Event listener for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    print(f'User: {message.author.name}, Message: {message.content}, Channel: {message.channel.name}')
    
    # Reload money data from JSON
    money_data = load_money_data()

    user_id = str(message.author.id)

    # Increment user's money by 1
    money_data.setdefault(user_id, 0)  # Set default value to 0 if user ID doesn't exist
    money_data[user_id] += 1

    save_money_data(money_data)

    await bot.process_commands(message)

@bot.command()
async def money(ctx):
    # Reload money data from JSON
    money_data = load_money_data()

    user_id = str(ctx.author.id)
    money = money_data.get(user_id, 0)
    formatted_balance = "{:,.2f}".format(money)  # Adding commas to the money balance
    await ctx.send(f'You have ${formatted_balance}')

# Command to send money to another user
@bot.command()
async def send(ctx, recipient: discord.Member, amount: float):
    sender_id = str(ctx.author.id)
    recipient_id = str(recipient.id)
    
    # Load money balances
    money_balances = load_money_data()

    if amount < 0:  # Check if amount is negative
        await ctx.send("You cannot send a negative amount of money.")
        return

    if sender_id not in money_balances:
        await ctx.send("You don't have any money balance yet.")
        return

    if money_balances[sender_id] < amount:
        await ctx.send("You don't have enough money to send.")
        return

    await ctx.send(f"To continue with your transaction of ${amount:.2f} to {recipient.name}, type `$confirm` or `$deny`.")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ['$confirm', '$deny']

    try:
        confirmation = await bot.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Timed out. Transaction canceled.")
        return

    if confirmation.content.lower() == '$deny':
        await ctx.send("Transaction canceled.")
        return

    money_balances[sender_id] -= amount
    money_balances[recipient_id] = money_balances.get(recipient_id, 0) + amount
    update_money_balance(money_balances)
    await ctx.send(f"You've sent ${amount:.2f} to {recipient.name}.")


timeout_counts = {}

# Function to read timeout_counts from the CSV file
def read_timeout_counts(filename):
    timeout_counts = {}
    try:
        with open(filename, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                timeout_counts[int(row['user_id'])] = int(row['count'])
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty dictionary
        pass
    return timeout_counts

# Function to update timeout_counts in the CSV file
def update_timeout_counts(filename, counts):
    with open(filename, 'w', newline='') as file:
        csv_writer = csv.DictWriter(file, fieldnames=['user_id', 'count'])
        csv_writer.writeheader()
        for user_id, count in counts.items():
            csv_writer.writerow({'user_id': user_id, 'count': count})

# Load timeout_counts when the bot starts up
timeout_counts = read_timeout_counts('/home/egglessnoob/Desktop/timeout_counts.csv')

@bot.command()
async def bug(ctx, *, message):
    # Replace 'hard_coded_user_id' with the user ID you want to DM
    user = await bot.fetch_user(746842205347381338)
    # Send a DM to the hardcoded user
    await user.send(f"Bug report from {ctx.author.display_name}: {message}")
    await ctx.message.add_reaction("✅")

@bot.event
async def on_member_update(before, after):
    global timeout_counts
    if before.timed_out_until is None:
        if after.timed_out_until is not None:
            print(f"****Member {after} was timed out!****")
            if after.id in timeout_counts:
                timeout_counts[after.id] += 1
            else:
                timeout_counts[after.id] = 1
            
            if timeout_counts[after.id] == 5:
                print(f'{after} has been timed out 5 times.')
                # Give the user a role here
                role = discord.utils.get(after.guild.roles, name="Gay🏳️‍🌈Baby👶Jail⛓️")
                if role:
                    await after.add_roles(role)
                    timeout_counts[after.id] = 0
                else:
                    print("We couldn't find the role")

            # Save timeout_counts to the CSV file after each update
            update_timeout_counts('/home/egglessnoob/Desktop/timeout_counts.csv', timeout_counts)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency is {latency}ms')

# Command to display help
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Bot Commands", description="List of available commands", color=discord.Color.blue())
    embed.add_field(name="`$money`", value="This command allows you to check your balance.", inline=False)
    embed.add_field(name="`$send @username amount`", value="This command allows you to send money to other users.", inline=False)
    embed.add_field(name="`$cf @username amount`", value="This command allows you to challenge another user to a coinflip. You can ping Eli Bot, and play against him!", inline=False)
    embed.add_field(name="`$shop`", value="This command allows you to see all the items you can buy!", inline=False)
    embed.add_field(name="`$games`", value="This command allows you to see the list of available games.", inline=False)
    embed.add_field(name="`$bug your_message`", value="This command allows you to report any bugs you find to me. When the bot adds the check mark reaction that means that your message got sent.", inline=False)
    embed.add_field(name="`$ping`", value="This command allows you to check the latency of the bot.", inline=False)
    embed.add_field(name="Additional Information", value="Please note this bot is in beta, if you find any bugs or glitches please use the `$bug message` command.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def  sudo(ctx, *agreements):
    async def confirm_action(ctx):
        def check(message):
            return (
                message.author == ctx.author
                and message.content.lower() == '$confirm'
                and message.author.guild_permissions.administrator
            )

        try:
            await ctx.send("Are you sure? Type `$confirm` to confirm.")
            confirmation = await bot.wait_for('message', check=check, timeout=30)
            return True
        except asyncio.TimeoutError:
            await ctx.send("Confirmation timed out.")
            return False
    if "hack" in agreements and "watch" in agreements and "gay" in agreements and "porn" in agreements:
        await ctx.send("Executing command with sudo privileges... \n[gay porn.com](https://www.youtube.com/@BionicOctopus)")
        # Implement your command logic here
    elif ctx.author.guild_permissions.administrator:
        if "lol" in agreements:
            if await confirm_action(ctx):
                await ctx.send("You have access to the **MOST POEWRFUL** *lol* out there! Use it wisely.")
        elif "ban" in agreements:
            # Check if there is a user mentioned
            if len(ctx.message.mentions) == 1:
                user_to_ban = ctx.message.mentions[0]
                # Check if the bot has permissions to ban members
                if ctx.guild.me.guild_permissions.ban_members:
                    try:
                        if await confirm_action(ctx):
                            # Ban the user
                            await ctx.guild.ban(user_to_ban, reason="Banned by sudo command")
                            await ctx.send(f"User {user_to_ban.mention} has been banned.")
                    except Exception as e:
                        await ctx.send(f"{user_to_ban.mention} was too poweruful to ban because {e}")
        elif "kick" in agreements:
            # Check if there is a user mentioned
            if len(ctx.message.mentions) == 1:
                user_to_kick = ctx.message.mentions[0]
                # Check if the bot has permissions to ban members
                if ctx.guild.me.guild_permissions.ban_members:
                    try:
                        if await confirm_action(ctx):
                            await ctx.guild.kick(user_to_kick, reason="Kicked by sudo command")
                            await ctx.send(f"User {user_to_kick.mention} has been kicked.")
                    except Exception as e:
                        await ctx.send(f"{user_to_kick.mention} was too poweruful to kick because {e}")
        elif "remove" in agreements:
            # Check if there is a user mentioned and a valid amount provided
            if len(ctx.message.mentions) == 1:
                user_to_remove = ctx.message.mentions[0]
                amount_index = agreements.index("remove") + 1
                if amount_index < len(agreements):
                    amount_str = agreements[amount_index]
                    try:
                        if await confirm_action(ctx):
                            amount = float(amount_str.replace(',', ''))
                            # Update the user's money balance here
                            user_id = str(user_to_remove.id)
                            money_data = load_money_data()
                            if user_id in money_data:
                                if money_data[user_id] >= amount:
                                    money_data[user_id] -= amount
                                    save_money_data(money_data)
                                    await ctx.send(f"Successfully removed {amount:.2f} from {user_to_remove.mention}'s account.")
                                else:
                                    await ctx.send(f"{user_to_remove.mention} doesn't have enough money.")
                            else:
                                await ctx.send(f"{user_to_remove.mention} doesn't have a money account.")
                        else:
                            await ctx.send(f"{user_to_remove.mention} doesn't have a money account.")
                    except ValueError:
                        await ctx.send("Invalid amount provided.")
                else:
                    await ctx.send("No amount provided.")
            else:
                await ctx.send("You need to mention a user to remove money from.")
        elif "add" in agreements:
            # Check if there is a user mentioned and a valid amount provided
            if len(ctx.message.mentions) == 1:
                user_to_add = ctx.message.mentions[0]
                amount_index = agreements.index("add") + 1
                if amount_index < len(agreements):
                    amount_str = agreements[amount_index]
                    try:
                        if await confirm_action(ctx):
                            amount = float(amount_str.replace(',', ''))
                            # Update the user's money balance here
                            user_id = str(user_to_add.id)
                            money_data = load_money_data()
                            if user_id in money_data:
                                money_data[user_id] += amount
                                save_money_data(money_data)
                                await ctx.send(f"Successfully added {amount:.2f} from {user_to_add.mention}'s account.")
                            else:
                                await ctx.send(f"{user_to_add.mention} doesn't have a balance")
                    except ValueError:
                        await ctx.send("Invalid amount provided.")
                else:
                    await ctx.send("No amount provided.")
            else:
                await ctx.send("You need to mention a user to add money.")
        elif "money" in agreements:
            # Check if there is a user mentioned
            if len(ctx.message.mentions) == 1:
                user_to_check = ctx.message.mentions[0]
                user_id = str(user_to_check.id)
                money_data = load_money_data()
                if user_id in money_data:
                    await ctx.send(f"{user_to_check.mention} has ${money_data[user_id]:,.2f} in their account.")
                else:
                    await ctx.send(f"{user_to_check.mention} doesn't have a money account.")
            else:
                await ctx.send("You need to mention a user to check their money balance.")
        elif "help" in agreements:
            embed = discord.Embed(title="Sudo Help", description="List of sudo commands.", color=discord.Color.blue())
            embed.add_field(name="`$sudo lol`", value="This command allows you to use the most powerful lol, **in existence!**", inline=False)
            embed.add_field(name="`$sudo ban @username`", value="This command allows you to ban a member, with only a command.", inline=False)
            embed.add_field(name="`$sudo kick @username`", value="This command allows you to kick a member, with only a command.", inline=False)
            embed.add_field(name="`$sudo remove amount @username`", value="This command allows you to remove an amount of money from a user's account.", inline=False)
            embed.add_field(name="`$sudo add amount @username`", value="This command allows you to add an amount of money from a user's account.", inline=False)
            embed.add_field(name="`$sudo money @username`", value="This command allows you to check the balance of a user.", inline=False)
            await ctx.send(embed=embed)


@bot.command()
async def cf(ctx, *, args):
    # Split the arguments
    args = args.split()

    # Check if there are enough arguments
    if len(args) < 2:
        await ctx.send("Please provide both an opponent and an amount.")
        return

    # Check if the first argument is a valid member
    try:
        opponent = await commands.MemberConverter().convert(ctx, args[0])
    except commands.errors.MemberNotFound:
        await ctx.send("Please provide a valid member.")
        return

    # Check if the second argument is a valid amount
    try:
        amount = float(args[1])
    except ValueError:
        await ctx.send("Please enter a valid amount.")
        return

    # Check if the amount is positive
    if amount <= 0:
        await ctx.send("Please enter a positive amount.")
        return

    # Sender
    sender = ctx.author
    sender_username = sender.name
    sender_id = str(sender.id)

    # Load money balances
    sender_money_balances = load_money_data()

    # Check if the sender has enough money
    if sender_id not in sender_money_balances or sender_money_balances[sender_id] < amount:
        await ctx.send("You don't have enough money to challenge.")
        return

    # Opponent
    opponent_username = opponent.name
    opponent_id = str(opponent.id)

    # Check if the opponent is Eli Bot
    if opponent_username == "Eli Bot":
        await ctx.send("Eli Bot automatically accepts the challenge.")
        accept_challenge = True
    else:
        # Send challenge message
        challenge_message = await ctx.send(f"{opponent.mention}, {sender_username} has challenged you to a coin flip for ${amount:.2f}. Do you accept? (Respond with `$cf accept` or `$cf deny`)")

        # Wait for opponent's response
        def check_acceptance(message):
            if message.author != opponent:
                return False
            opponent_money_balances = load_money_data()
            return message.content.lower() in ["$cf accept", "$cf deny"] and opponent_money_balances[opponent_id] >= amount

        try:
            acceptance_message = await bot.wait_for('message', timeout=30.0, check=check_acceptance)
        except asyncio.TimeoutError:
            await ctx.send(f"{opponent.mention} didn't respond in time. Challenge canceled.")
            return

        if acceptance_message.content.lower() == "$cf deny":
            await ctx.send(f"{opponent.mention} has denied the challenge. Challenge canceled.")
            return

        accept_challenge = True

    if accept_challenge:
        # Generate a random number (0 or 1) for the coin flip
        result = random.randint(0, 1)

        # Determine the winner and update balances accordingly
        if result == 1:
            gif_message = await ctx.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXd3aXJ2bWt6M3cyaGhzdGx5MmduaWI2MzB6bHU2cHA0ejAza2p2MiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/RFjWmNVMXtACCxQ2yw/source.gif")
            sender_money_balances[sender_id] += amount
            sender_money_balances[opponent_id] -= amount
            time.sleep(4)
            await gif_message.delete()
            await ctx.send(f"Heads, {sender_username} wins!")
        else:
            gif_message = await ctx.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaTl0MXI0eW5uZWU0aWQwNWJla3pydm1heXRjdTRjaXpjbWo3dXl3YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JBDHHdpzI6PUBQdxEg/source.gif")
            sender_money_balances[sender_id] -= amount
            sender_money_balances[opponent_id] += amount
            time.sleep(4)
            await gif_message.delete()
            await ctx.send(f"Tails, {opponent_username} wins!")

        # Update balances in the JSON file
        update_money_balance(sender_money_balances)


@bot.command()
async def games(ctx):
    embed = discord.Embed(title="Games", description="List of available games", color=discord.Color.blue())
    embed.add_field(name="`$cf @username amount`", value="In this game you challenge another user to a coinflip.", inline=False)
    embed.add_field(name="`$chess time increment amount`", value="In this game you challenge another user to a game of chess.", inline=False)
    embed.add_field(name="`$bj amount`", value="This game is black jack. (Coming soon!)", inline=False)
    embed.add_field(name="`$ttt @username amount`", value="In this game you challenge another user to a game of Tic Tac Toe.", inline=False)
    embed.add_field(name="`$connent4 @username amount`", value="In this game you challenge another user to a game of connect 4. (Coming soon!)", inline=False)
    embed.add_field(name="Additional Information", value="All games can be played with Eli Bot! Just ping him in the @username section of the command.", inline=False)
    await ctx.send(embed=embed)

# Function to display the Tic Tac Toe board
def display_board(board):
    numbers = [str(i + 1) if cell == "-" else cell for i, cell in enumerate(board)]
    return "\n".join([" | ".join(numbers[i:i+3]) for i in range(0, 9, 3)])

# Function to check if a player has won
def check_win(board, mark):
    # Check rows
    for row in board:
        if all(cell == mark for cell in row):
            return True

    # Check columns
    for col in range(3):
        if all(board[row][col] == mark for row in range(3)):
            return True

    # Check diagonals
    if all(board[i][i] == mark for i in range(3)) or all(board[i][2 - i] == mark for i in range(3)):
        return True

    return False

# Command to initiate a Tic Tac Toe game
@bot.command()
async def ttt(ctx, *, args):
    board = ["-" for _ in range(9)]
    # Split the arguments
    args = args.split()

    # Check if there are enough arguments
    if len(args) < 2:
        return

    # Check if the first argument is a valid member
    try:
        opponent = await commands.MemberConverter().convert(ctx, args[0])
    except commands.errors.MemberNotFound:
        await ctx.send("Please provide a valid member.")
        return

    # Check if the second argument is a valid amount
    if args[1].lower() == 'nan':
        await ctx.send("Please enter a valid amount.")
        return

    # Check if the second argument is a valid amount
    try:
        amount = float(args[1])
    except ValueError:
        await ctx.send("Please enter a valid amount.")
        return

    # Check if the amount is positive
    if amount <= 0:
        await ctx.send("Please enter a positive amount.")
        return

    # Sender
    sender = ctx.author
    sender_username = sender.name

    # Sender's information
    sender_id = str(sender.id)
    sender_money_balances = read_money_balances()  # Load money balances

    # Load money balances
    sender_money_balances = load_money_data()

    # Check if the sender has enough money
    if sender_id not in sender_money_balances or sender_money_balances[sender_id] < amount:
        await ctx.send("You don't have enough money to challenge.")
        return

    # Opponent
    opponent_username = opponent.name
    opponent_id = str(opponent.id)

    # Check if the opponent is Eli Bot
    if opponent_username == "Eli Bot":
        await ctx.send("You challenged Eli Bot! Let's play.")

        # Send initial message with the board
        await ctx.send('To play this game type the number of the space you want to move. You have 30 seconds to make a move before the game is cancelled.')
        game_message = await ctx.send(f"{sender_username}, it's your turn.\n```\n{display_board(board)}\n```")

        # Play against Eli Bot
        while True:
            # Human player's move
            def check_move(msg):
                return msg.author == sender and msg.content.isdigit() and 1 <= int(msg.content) <= 9 and board[int(msg.content) - 1] == "-"

            try:
                move_message = await bot.wait_for('message', timeout=60.0, check=check_move)
            except asyncio.TimeoutError:
                await ctx.send("Time's up! Game canceled.")
                return

            position = int(move_message.content) - 1
            board[position] = 'X'

            await game_message.edit(content=f"{sender_username} has placed X at position {position + 1}.\n```\n{display_board(board)}\n```")

            if check_win([board[i:i+3] for i in range(0, 9, 3)], 'X'):
                await ctx.send(f"{sender_username} wins!")
                return

            if all(cell != "-" for cell in board):
                await ctx.send("It's a draw!")
                return

            # Eli Bot's move
            eli_move = random.choice([i for i, cell in enumerate(board) if cell == "-"])
            board[eli_move] = 'O'

            await game_message.edit(content=f"Eli Bot has placed O at position {eli_move + 1}.\n```\n{display_board(board)}\n```")

            if check_win([board[i:i+3] for i in range(0, 9, 3)], 'O'):
                await ctx.send("Eli Bot wins!")
                return

            if all(cell != "-" for cell in board):
                await ctx.send("It's a draw!")
                return

    if opponent_username == sender_username:
        await ctx.send("You can't challenge yourself.")
        return

    # Send challenge message
    challenge_message = await ctx.send(f"{opponent.mention}, {sender_username} has challenged you to a game of Tic Tac Toe for ${amount:.2f}. Do you accept? (Respond with `$ttt accept` or `$ttt deny`)")

    # Wait for opponent's response
    def check_acceptance(message):
        if message.author != opponent:
            return False
        opponent_money_balances = load_money_data()
        return message.content.lower() in ["$ttt accept", "$ttt deny"] and opponent_money_balances[str(opponent.id)] >= amount

    try:
        acceptance_message = await bot.wait_for('message', timeout=30.0, check=check_acceptance)
    except asyncio.TimeoutError:
        await ctx.send(f"{opponent.mention} didn't respond in time. Challenge canceled.")
        return

    if acceptance_message.content.lower() == "$ttt deny":
        await ctx.send(f"{opponent.mention} has denied the challenge. Challenge canceled.")
        return

    # Initialize the Tic Tac Toe board
    #board = ["-" for _ in range(9)]

    # Set up the game
    players = [sender, opponent]
    symbols = ['X', 'O']
    current_player_index = random.randint(0, 1)
    current_player = players[current_player_index]
    current_symbol = symbols[current_player_index]

    # Send initial message with the board
    await ctx.send('To play this game type the number of the space you want to move. You have 30 seconds to make a move before the game is cancelled.')
    game_message = await ctx.send(f"{current_player.mention}, it's your turn.\n```\n{display_board(board)}\n```")
    

    # Play the game
    while True:
        def check_move(msg):
            return msg.author == current_player and msg.content.isdigit() and 1 <= int(msg.content) <= 9 and board[int(msg.content) - 1] == "-"

        try:
            move_message = await bot.wait_for('message', timeout=60.0, check=check_move)
        except asyncio.TimeoutError:
            await ctx.send("Time's up! Game canceled.")
            return

        position = int(move_message.content) - 1
        board[position] = current_symbol

        await game_message.edit(content=f"{current_player.mention} has placed {current_symbol} at position {position + 1}.\n```\n{display_board(board)}\n```")

        if check_win([board[i:i+3] for i in range(0, 9, 3)], current_symbol):
            await ctx.send(f"{current_player.mention} wins!")
            sender_money_balances[sender_username] += amount if current_player == sender else -amount
            sender_money_balances[opponent_username] += amount if current_player == opponent else -amount
            update_money_balance(sender_money_balances)
            return

        if all(cell != "-" for cell in board):
            await ctx.send("It's a draw!")
            return

        current_player_index = (current_player_index + 1) % 2
        current_player = players[current_player_index]
        current_symbol = symbols[current_player_index]
        await move_message.delete()
        await game_message.edit(content=f"{current_player.mention}, it's your turn.\n```\n{display_board(board)}\n```")

# Function to load Lichess account data from JSON file
def load_lichess_data():
    try:
        with open(LICHESS_JSON_FILEPATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Function to save Lichess account data to JSON file
def save_lichess_data(lichess_data):
    with open(LICHESS_JSON_FILEPATH, 'w') as f:
        json.dump(lichess_data, f, indent=4)

# Function to add user's Lichess account to data
def add_lichess_account(user_id, account_name):
    lichess_data = load_lichess_data()
    lichess_data[str(user_id)] = account_name
    save_lichess_data(lichess_data)

# Function to check if Lichess account exists
def check_lichess_account_exists(account_name):
    response = requests.get(f"{LICHESS_API_URL}{account_name}")
    return response.status_code == 200

# Command to add user's Lichess account
@bot.command()
async def lichess(ctx, account_name):
    try:
        # Check if the account name is provided
        if not account_name:
            await ctx.send("Please provide your Lichess account name.")
            return

        # Check if the Lichess account exists
        if not check_lichess_account_exists(account_name):
            await ctx.send("The provided Lichess account does not exist.")
            return

        # Add user's Lichess account to data
        add_lichess_account(ctx.author.id, account_name)
        await ctx.send(f"Your Lichess account '{account_name}' has been added successfully.")

    except Exception as e:
        print(f"Line 655 an error occurred: {e}")

@bot.command()
async def chess(ctx, time: int, increment: int, amount: float):
    try:
        # Check if the user has a linked Lichess account
        lichess_data = load_lichess_data()
        user_id = str(ctx.author.id)
        if user_id not in lichess_data:
            await ctx.send("You need to link your Lichess account before creating a game. You can do that by using the `$lichess username` command.")
            return
        try:
            # Check if time, increment, and amount are valid
            if time <= 0 or increment < 0 or amount <= 0:
                await ctx.send("Time should be in minutes, increment should be in seconds, amount should be in dollars, and all numbers must be positive numbers.")
                return

            if time > 10:
                await ctx.send('The maximum amount of time allowed is 10 minutes.')
                return
            
            if increment > 5:
                await ctx.send('The maximum amount of increment allowed is 5 seconds.')
                return

            # Check if the user has enough money
            user_id = str(ctx.author.id)
            money_balances = read_money_balances()
            if user_id not in money_balances or money_balances[user_id] < amount:
                await ctx.send("You don't have enough money to play.")
                return

            time = time * 60

            # Generate game link
            game_link = generate_game_link(time, increment)

            # Send game link to users
            await ctx.send(f"{ctx.author.mention} has initiated a chess game. Type `$accept` to join the game.")

            # Wait for opponent's response
            def check_acceptance(message):
                return message.content.lower() == "$accept" and message.author != ctx.author

            try:
                acceptance_message = await bot.wait_for('message', check=check_acceptance, timeout=30)
                opponent = acceptance_message.author

                # Check if the opponent has a linked Lichess account
                opponent_id = str(opponent.id)
                if opponent_id not in lichess_data:
                    await ctx.send(f"{opponent.mention} you need to link your Lichess account before joining the game. You can do that by using the `$lichess username` command.")
                    return

                await ctx.send(f"Click here to play chess: {game_link}")
                game_id = game_link.split('/')[-1]
                print(game_id)
                result = get_game_result(game_id)
                print(result)

                #take the game result and update the money balances
                if result == "1-0":
                    money_balances[user_id] += amount
                    money_balances[opponent_id] -= amount
                    update_money_balance(money_balances)
                    await ctx.send(f"{ctx.author.mention} has won the game!")
                elif result == "0-1":
                    money_balances[user_id] -= amount
                    money_balances[opponent_id] += amount
                    update_money_balance(money_balances)
                    await ctx.send(f"{opponent.mention} has won the game!")
                else:
                    await ctx.send("The game ended in a draw.")

            except asyncio.TimeoutError:
                await ctx.send("No one accepted the game. The game has been cancelled.")

        except Exception as e:
            print(f"Line 720 an error occurred: {e}")
    except Exception as e:
        print(f"Line 722 an error occurred: {e}")
        return None

def generate_game_link(time_control, increment):
    try:
        # Use Lichess API to create a new game
        response = requests.post('https://lichess.org/api/challenge/open', 
                                data={'clock.limit': str(time_control), 'clock.increment': str(increment)})
        
        # Check if the request was successful
        if response.status_code == 200:
            # Extract game ID from response
            game_id = response.json()['challenge']['id']
            
            # Generate link using game ID
            game_link = f"https://lichess.org/{game_id}"
            return game_link
        else:
            print(f"Line 740 Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Line 743 an error occurred: {e}")
        return None

game_is_not_over = True

def get_game_result(game_id):
    global game_is_not_over
    while game_is_not_over:
        try:
            time.sleep(5)
            url = f"https://lichess.org/game/export/{game_id}"
            response = requests.get(url)
            if response.status_code == 200:
                # Parse PGN format
                pgn_data = response.text
                
                # Check for termination
                termination_match = re.search(r"\[Termination \"(.*?)\"\]", pgn_data)
                if termination_match:
                    termination = termination_match.group(1)
                    if termination != "Unterminated":
                        result_match = re.search(r"\[Result \"(.*?)\"\]", pgn_data)
                        if result_match:
                            result = result_match.group(1)
                            game_is_not_over = False
                            return result
                    else:
                        print("Game still in progress. Waiting for update...")
                else:
                    print("Game result not finalized yet. Waiting for update...")
            else:
                print("Failed to retrieve game data")
        except Exception as e:
            print(f"An error occurred: {e}")

@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="Shop", description="List of items for purchase.", color=discord.Color.blue())
    embed.add_field(name="`$buy role_1k`", value="This item gives you a cosmetic role, and access to a private channel! $1000.00", inline=False)
    embed.add_field(name="`$buy role_10k`", value="This item gives you a cosmetic role, and access to a private channel! $10,000.00", inline=False)
    embed.add_field(name="`$buy role_100k`", value="This item gives you a cosmetic role, and access to a private channel! $100,000.00", inline=False)
    embed.add_field(name="`$buy role_1m`", value="This item gives you a cosmetic role, and access to a private channel! $1,000,000.00", inline=False)
    embed.add_field(name="`$buy role_1b`", value="This item gives you a cosmetic role, and access to a private channel! $1,000,000,000.00", inline=False)
    embed.add_field(name="`$buy role_1t`", value="This item gives you a cosmetic role, and access to a private channel! $1,000,000,000,000.00", inline=False)
    await ctx.send(embed=embed)

# Define your role IDs here
role_ids = {
    "role_1k": 1235445271920508998,  # Replace with actual role ID
    "role_10k": 1235445595695747123,  # Replace with actual role ID
    "role_100k": 1235445963280224308,  # Replace with actual role ID
    "role_1m": 1235446849876525137,  # Replace with actual role ID
    "role_1b": 1235448562460917780,  # Replace with actual role ID
    "role_1t": 1235448860457828443,  # Replace with actual role ID
    # Add more role IDs as needed
}

@bot.command()
async def buy(ctx, item_name: str):
    buyer = str(ctx.author.id)
    print(buyer)
    items = {
        "role_1k": 1000,  # Example item with price
        "role_10k": 10000,  # Add more items with their prices
        "role_100k": 100000,
        "role_1m": 1000000,
        "role_1b": 1000000000,
        "role_1t": 1000000000000,
        # Add more items as needed
    }

    money_balances = read_money_balances()  # Load money balances
    print(money_balances)

    if buyer not in money_balances:
        await ctx.send("You don't have any money balance yet.")
        return

    item_price = items.get(item_name)
    if item_price is None:
        await ctx.send("Sorry, that item is not available.")
        return

    if money_balances[buyer] < item_price:
        await ctx.send("You don't have enough money to buy this item.")
        return

    await ctx.send(f"To confirm your purchase of {item_name} for ${item_price:.2f}, type `$confirm` or `$deny`.")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ['$confirm', '$deny']

    try:
        confirmation = await bot.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Timed out. Purchase canceled.")
        return

    if confirmation.content.lower() == '$deny':
        await ctx.send("Purchase canceled.")
        return

    # Grant role
    role_id = role_ids.get(item_name)
    role = ctx.guild.get_role(role_id)
    try:
        await ctx.author.add_roles(role)
        money_balances[buyer] -= item_price
        # Update the money balance and add the item to the inventory or perform relevant actions
        update_money_balance(money_balances)
        await ctx.send(f"You've purchased {item_name} for ${item_price:.2f} and received the corresponding role.")
    except:
        await ctx.send("Role not found. Please contact server administrator; or use the $bug command.")

@bot.command()
async def leaderboard(ctx):
    # Load money balances from JSON
    with open(MONEY_JSON_FILEPATH, 'r') as f:
        money_balances = json.load(f)
    
    # Sort the money balances dictionary by values (money) in descending order
    sorted_money_balances = dict(sorted(money_balances.items(), key=lambda item: item[1], reverse=True))
    
    # Create an empty image with desired dimensions
    image_width = 600
    image_height = 770
    background_color = (54,57,62)  # Darkish grey background
    image = Image.new("RGB", (image_width, image_height), background_color)
    
    # Load font with larger size
    font_size = 30
    font = ImageFont.truetype("arial.ttf", font_size)
    
    # Initialize drawing context
    draw = ImageDraw.Draw(image)
    
    # Load profile pictures and draw them with ranks and money balances
    count = 0
    y_offset = 10
    for user_id, money_balance in sorted_money_balances.items():
        # Skip the user with ID 1175890644191957013
        if user_id == '1175890644191957013':
            continue
        
        user = bot.get_user(int(user_id))
        if user is not None:
            count += 1
            
            # Check if profile picture is in cache
            profile_picture_path = os.path.join(CACHE_DIR, f"{user.id}.png")
            if os.path.exists(profile_picture_path):
                profile_picture = Image.open(profile_picture_path)
            else:
                # Download profile picture
                if user.avatar is None:
                    # Handle default profile picture
                    profile_picture = Image.open("/home/egglessnoob/Desktop/defualt.png")  # Provide path to your default profile picture
                else:
                    profile_picture_response = requests.get(user.avatar.url, stream=True)
                    profile_picture_response.raise_for_status()
                    profile_picture = Image.open(profile_picture_response.raw)
                
                # Save profile picture to cache
                profile_picture.save(profile_picture_path)
            
            # Resize profile picture to fit
            profile_picture = profile_picture.resize((70, 70))
            # Draw profile picture
            image.paste(profile_picture, (10, y_offset))
            # Determine color based on rank
            if count == 1:
                rank_color = (255, 215, 0)  # Gold color
            elif count == 2:
                rank_color = (192, 192, 192)  # Silver color
            elif count == 3:
                rank_color = (205, 127, 50)  # Bronze color
            else:
                rank_color = (255, 255, 255)  # White color
            # Draw user's rank, username, and money balance with appropriate color and larger dots
            draw.text((100, y_offset + 10), f"•  #{count} • {user.name}", fill=rank_color, font=font)
            draw.text((390, y_offset + 10), "${:,.2f}".format(money_balance), fill=(255, 255, 255), font=font)  # White color for money balance with commas
            # Increment y_offset for next user
            y_offset += 75
        if count == 10:
            break
    
    # Save the image
    image.save("leaderboard_image.png")
    
    # Create an embed
    embed = discord.Embed(title="Money Leaderboard", color=0x282b30)
    embed.set_image(url="attachment://leaderboard_image.png")
    
    # Send the embed with the image file
    await ctx.send(embed=embed, file=discord.File("leaderboard_image.png"))

#damn brit
#bot.run("MTIzMDk2MjI2OTc0ODQ2NTY2Ng.G99PQ1.04Ch0VvwZbQqS0ZnbPKMjjAra8t2dHv38M9BQ0")

#eli bot
bot.run('MTE3NTg5MDY0NDE5MTk1NzAxMw.GZtdjv.4039BrLsym-_rBJd1OV8W7GdSVysVomGA9xHC4')
