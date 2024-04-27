
import discord
from discord.ext import commands
import csv
import asyncio
import random
import time
import math

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

# Override the default help command
bot.remove_command('help')  # Remove the default help command


# Function to read money balances from the CSV file
def read_money_balances(filename):
    money_balances = {}
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            money_balances[row['Username']] = float(row['Money'])
    return money_balances

# Function to update money balances in the CSV file
def update_money_balance(filename, balances):
    with open(filename, 'w', newline='') as file:
        csv_writer = csv.DictWriter(file, fieldnames=['Username', 'Money'])
        csv_writer.writeheader()
        for username, money in balances.items():
            csv_writer.writerow({'Username': username, 'Money': money})

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

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


@bot.event
async def on_message(message):
    print(f'User: {message.author.name}, Message: {message.content}, Channel: {message.channel.name}')

    def update_money_balance(filename, username):
        money_balances = read_money_balances(filename)
        if username in money_balances:
            money_balances[username] += 1.00
        else:
            money_balances[username] = 1.00
        
        with open(filename, 'w', newline='') as file:
            csv_writer = csv.DictWriter(file, fieldnames=['Username', 'Money'])
            csv_writer.writeheader()
            for username, money in money_balances.items():
                csv_writer.writerow({'Username': username, 'Money': money})

    def user_sent_message(username):
        update_money_balance('/home/egglessnoob/Desktop/money.csv', username)

    user_sent_message(message.author.name)

    await bot.process_commands(message)


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
    embed.add_field(name="Additional Information", value="Please note this bot is in beta, if you find any bugs or glitches please use the $bug command.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def  sudo(ctx, *agreements):
    if "hack" in agreements and "watch" in agreements and "gay" in agreements and "porn" in agreements:
        await ctx.send("Executing command with sudo privileges... \n[gay porn.com](https://www.youtube.com/@BionicOctopus)")
        # Implement your command logic here
    else:
        pass

@bot.command()
async def money(ctx):
    username = ctx.author.name
    money_balances = read_money_balances('/home/egglessnoob/Desktop/money.csv')
    if username in money_balances:
        money_balance = money_balances[username]
        formatted_balance = "{:,.2f}".format(money_balance)  # Adding commas to the money balance
        await ctx.send(f'You have ${formatted_balance}')
    else:
        await ctx.send("You don't have any money balance yet.")

@bot.command()
async def send(ctx, recipient: discord.Member, amount: float):
    sender = ctx.author.name
    filename = '/home/egglessnoob/Desktop/money.csv'
    money_balances = read_money_balances(filename)

    if amount < 0:  # Check if amount is negative
        await ctx.send("You cannot send a negative amount of money.")
        return

    if sender not in money_balances:
        await ctx.send("You don't have any money balance yet.")
        return

    if money_balances[sender] < amount:
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

    if confirmation.content.lower() == '$deny': #yes
        await ctx.send("Transaction canceled.")
        return

    money_balances[sender] -= amount
    if money_balances[sender] >= 0:
        if recipient.name in money_balances:
            money_balances[recipient.name] += amount
        else:
            money_balances[recipient.name] = amount
        update_money_balance(filename, money_balances)
        await ctx.send(f"You've sent ${amount:.2f} to {recipient.name}.")
    else:
        await ctx.send("Transaction failed: Insufficient balance.")

@bot.command()
async def cf(ctx, *, args):
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

    # Check if the sender has enough money
    sender_money_balances = read_money_balances('/home/egglessnoob/Desktop/money.csv')
    if sender_username not in sender_money_balances or sender_money_balances[sender_username] < amount:
        await ctx.send("You don't have enough money to challenge.")
        return

    # Opponent
    opponent_username = opponent.name

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
            opponent_money_balances = read_money_balances('/home/egglessnoob/Desktop/money.csv')
            return message.content.lower() in ["$cf accept", "$cf deny"] and opponent_money_balances[opponent.name] >= amount

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
        import random
        result = random.randint(0, 1)

        # Determine the winner and update balances accordingly
        if result == 1:
            gif_message = await ctx.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXd3aXJ2bWt6M3cyaGhzdGx5MmduaWI2MzB6bHU2cHA0ejAza2p2MiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/RFjWmNVMXtACCxQ2yw/source.gif")
            sender_money_balances[sender_username] += amount
            sender_money_balances[opponent_username] -= amount
            time.sleep(4)
            await gif_message.delete()
            await ctx.send(f"Heads, {sender_username} wins!")
        else:
            gif_message = await ctx.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaTl0MXI0eW5uZWU0aWQwNWJla3pydm1heXRjdTRjaXpjbWo3dXl3YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JBDHHdpzI6PUBQdxEg/source.gif")
            sender_money_balances[sender_username] -= amount
            sender_money_balances[opponent_username] += amount
            time.sleep(4)
            await gif_message.delete()
            await ctx.send(f"Tails, {opponent_username} wins!")

        # Update balances in the CSV file
        update_money_balance('/home/egglessnoob/Desktop/money.csv', sender_money_balances)

@bot.command()
async def games(ctx):
    embed = discord.Embed(title="Games", description="List of available games", color=discord.Color.blue())
    embed.add_field(name="`$cf @username amount`", value="In this game you challenge another user to a coinflip.", inline=False)
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

    # Check if the sender has enough money
    sender_money_balances = read_money_balances('/home/egglessnoob/Desktop/money.csv')
    if sender_username not in sender_money_balances or sender_money_balances[sender_username] < amount:
        await ctx.send("You don't have enough money to challenge.")
        return

    # Opponent
    opponent_username = opponent.name

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
        opponent_money_balances = read_money_balances('/home/egglessnoob/Desktop/money.csv')
        return message.content.lower() in ["$ttt accept", "$ttt deny"] and opponent_money_balances[opponent.name] >= amount

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
            update_money_balance('/home/egglessnoob/Desktop/money.csv', sender_money_balances)
            return

        if all(cell != "-" for cell in board):
            await ctx.send("It's a draw!")
            return

        current_player_index = (current_player_index + 1) % 2
        current_player = players[current_player_index]
        current_symbol = symbols[current_player_index]
        await move_message.delete()
        await game_message.edit(content=f"{current_player.mention}, it's your turn.\n```\n{display_board(board)}\n```")


@bot.command()
async def shop(ctx):
    embed = discord.Embed(title="Shop", description="List of items for purchase.", color=discord.Color.blue())
    embed.add_field(name="`$buy temp_role`", value="This item gives you a cosmetic role. $100.00", inline=False)
    embed.add_field(name="`$buy temp_role1`", value="This item gives you a cosmetic role, and access to a private channel! $500.00", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, item_name: str):
    buyer = ctx.author.name
    filename = '/home/egglessnoob/Desktop/money.csv'
    items = {
        "temp_role": 100,  # Example item with price
        "temp_role1": 500,  # Add more items with their prices
        "item3": 15,
        # Add more items as needed
    }
    money_balances = read_money_balances(filename)

    if item_name not in items:
        await ctx.send("Sorry, that item is not available.")
        return

    item_price = items[item_name]

    if buyer not in money_balances:
        await ctx.send("You don't have any money balance yet.")
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

    money_balances[buyer] -= item_price
    if buyer in money_balances:
        money_balances[buyer] -= item_price
    else:
        money_balances[buyer] = -item_price

    # Update the money balance and add the item to the inventory or perform relevant actions
    update_money_balance(filename, money_balances)
    await ctx.send(f"You've purchased {item_name} for ${item_price:.2f}.")


bot.run('MTE3NTg5MDY0NDE5MTk1NzAxMw.GZtdjv.4039BrLsym-_rBJd1OV8W7GdSVysVomGA9xHC4')
