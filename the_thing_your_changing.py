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