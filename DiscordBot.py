from dotenv import load_dotenv
import os
import re
import random
import unicodedata
import mojimoji
import discord
from discord.ext import commands
from discord.commands import Option


class GameStats:
    def __init__(self):
        self.row = 3
        self.connect = self.row
        self.fields = [[0] * self.row for i in range(self.row)]
        self.squareCount = self.row * self.row
        self.turn = 0
        self.isMatch = False
        self.playerNames = []
        self.playerIds = []
        self.turnPlayer = 0

    def Reset(self):
        self.fields = [[0] * self.row for i in range(self.row)]
        self.isMatch = False
        self.turn = 0
        self.squareCount = self.row * self.row
        self.playerNames = []
        self.playerIds = []
        self.turnPlayer = 0


load_dotenv()
gameStats = GameStats()
TOKEN = os.getenv("TOKEN")
status = "/play"
statustype = discord.ActivityType.watching
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Ready")
    await bot.change_presence(activity=discord.Activity(name=status, type=statustype))


@bot.event
async def on_message(message):
    if (
        not gameStats.isMatch
        or not message.author.id == gameStats.playerIds[gameStats.turnPlayer]
    ):
        return
    else:
        result = int(re.sub(r"\D", "", unicodedata.normalize("NFKC", message.content)))
        if result > 0 and result <= gameStats.squareCount:
            index = divmod(result - 1, gameStats.row)
            if gameStats.fields[index[0]][index[1]] != 0:
                await message.channel.send("そのマスには既に置かれています")
                return
            gameStats.fields[index[0]][index[1]] = gameStats.turnPlayer + 1
            await message.channel.send(DrawField())
            gameStats.turn += 1
            if LineCheck() != 0:
                await message.channel.send(
                    f"{gameStats.playerNames[gameStats.turnPlayer]}さんの勝利です！"
                )
                gameStats.Reset()
                return
            if gameStats.turn == gameStats.squareCount:
                await message.channel.send("引き分けです！")
                gameStats.Reset()
                return
            if len(gameStats.playerNames) < 2:
                await message.channel.send(f"コンピューターのターンです")
                pos = ReachCheck()
                if pos == None:
                    while True:
                        x = random.randint(0, gameStats.row - 1)
                        y = random.randint(0, gameStats.row - 1)
                        if gameStats.fields[y][x] == 0:
                            pos = y, x
                            break
                gameStats.fields[pos[0]][pos[1]] = 2
                await message.channel.send(DrawField())
                gameStats.turn += 1
                if LineCheck() != 0:
                    await message.channel.send("コンピューターの勝利です！")
                    gameStats.Reset()
                    return
                if gameStats.turn == gameStats.squareCount:
                    await message.channel.send("引き分けです！")
                    gameStats.Reset()
                    return
                await message.channel.send(f"{gameStats.playerNames[0]}さんのターンです")
            else:
                gameStats.turnPlayer += 1
                if gameStats.turnPlayer >= len(gameStats.playerNames):
                    gameStats.turnPlayer = 0
                await message.channel.send(
                    f"{gameStats.playerNames[gameStats.turnPlayer]}さんのターンです"
                )


async def get_players(ctx):
    return [
        user.display_name
        for user in bot.get_channel(ctx.interaction.channel_id).members
        if user.display_name.startswith(ctx.value) and not user.bot
    ]


@bot.slash_command(description="三目並べを開始します")
async def play(
    ctx,
    player: Option(
        str, "対戦相手を指定してください。指定しない場合、コンピューターが相手になります。", autocomplete=get_players
    ) = "",
    square: Option(int, "何マス×何マスでプレイするか指定してください。指定しない場合、3×3になります。") = 3,
):
    if square <= 0:
        await force_end(ctx, square)
        return
    if not player == "":
        playerInUsers = False
        for user in bot.get_channel(ctx.interaction.channel_id).members:
            if player == user.display_name:
                playerInUsers = True
                break
        if not playerInUsers:
            await ctx.respond(f"{player}という名前のユーザーが存在しません")
            return
        if player == ctx.author.display_name:
            await ctx.respond("【注意】己との対戦になります")
    gameStats.row = square
    gameStats.connect = square
    gameStats.Reset()
    gameStats.isMatch = True
    gameStats.playerNames.append(ctx.author.display_name)
    gameStats.playerIds.append(ctx.author.id)
    if not player == "":
        gameStats.playerIds.append(
            [user.id for user in bot.users if user.display_name == player][0]
        )
        gameStats.playerNames.append(player)

    await ctx.respond(
        f"{square}×{square}マスで始めます。\n{ctx.author.display_name}さん、置く場所を1~{gameStats.squareCount}で指定してください"
    )
    textField = ""
    loopCount = 0
    for i in range(len(gameStats.fields)):
        for j in range(len(gameStats.fields[i])):
            if loopCount % gameStats.row == 0:
                textField += "\n"
            loopCount += 1
            if loopCount < 10:
                textField += mojimoji.han_to_zen(f"{loopCount}")
            else:
                textField += "／"
    await ctx.send(textField)


@bot.slash_command(description=f"{gameStats.row}目並べを終了します")
async def end(ctx):
    await ctx.respond(f"{gameStats.row}目並べを終了しました")
    gameStats.Reset()


async def force_end(ctx, square):
    if not square == 0:
        await ctx.respond(f"{square}目並べに失敗しました。正の値目並べを開始してください。")
    else:
        await ctx.respond(
            f"{square}x{square}マスで始めます。おはよう{ctx.author.display_name} お前の勝ちだよ"
        )
    return


def DrawField():
    textField = ""
    loopCount = 0
    for i in range(len(gameStats.fields)):
        for j in range(len(gameStats.fields[i])):
            if loopCount % gameStats.row == 0:
                textField += "\n"
            loopCount += 1

            if gameStats.fields[i][j] == 1:
                textField += "〇"
            elif gameStats.fields[i][j] == 2:
                textField += "✕"
            else:
                if loopCount < 10:
                    textField += mojimoji.han_to_zen(f"{loopCount}")
                else:
                    textField += mojimoji.han_to_zen(f"／")
    return textField


def ReachCheck():
    for i in reversed(range(1, 3)):
        for y in range(gameStats.row):
            if (
                gameStats.fields[y].count(i) == gameStats.connect - 1
                and 0 in gameStats.fields[y]
            ):
                if i != 0:
                    return y, gameStats.fields[y].index(0)

        for x in range(gameStats.row):
            column = [c[x] for c in gameStats.fields]
            if column.count(i) == gameStats.connect - 1 and 0 in column:
                if i != 0:
                    return column.index(0), x

        diagonal = [gameStats.fields[n][n] for n in range(gameStats.row)]
        if diagonal.count(i) == gameStats.connect - 1 and 0 in diagonal:
            index = diagonal.index(0)
            return index, index
        diagonal = [
            gameStats.fields[n][gameStats.row - 1 - n] for n in range(gameStats.row)
        ]
        if diagonal.count(i) == gameStats.connect - 1 and 0 in diagonal:
            index = diagonal.index(0)
            return index, gameStats.row - 1 - index


def LineCheck():
    winner = 0
    for i in range(1, 3):
        for x in range(gameStats.row):
            column = [c[x] for c in gameStats.fields]
            if column.count(i) == gameStats.connect:
                winner = i
        for y in range(gameStats.row):
            if gameStats.fields[y].count(i) == gameStats.connect:
                winner = i

        diagonal = [gameStats.fields[n][n] for n in range(gameStats.row)]
        if diagonal.count(i) == gameStats.connect:
            winner = i
        diagonal = [
            gameStats.fields[n][gameStats.row - 1 - n] for n in range(gameStats.row)
        ]
        if diagonal.count(i) == gameStats.connect:
            winner = i
    return winner


bot.run(TOKEN)
