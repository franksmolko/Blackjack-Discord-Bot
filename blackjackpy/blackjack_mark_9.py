'''
Token: MTA3NTIyMTgxNzY0OTc5MTA5OA.GxJAGR.L_hrYxo3f5ZZQj_9dmJjswQZAVYyPiQNoJqt0I
Invite: https://discord.com/api/oauth2/authorize?client_id=1075221817649791098&permissions=534723950656&scope=bot
'''

import discord 
from discord.ext import commands
import random
import sqlite3


bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

#Instantiate database table if not already instantiated.

@bot.event
async def on_ready():
    db = sqlite3.connect('points.db')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
        user TEXT,
        points INTEGER
        )
        ''')
    print("Bot activated!")


#Create menu class. Contains functions to draw cards, hold, have dealer draw cards

class Menu(discord.ui.View):
    def __init__(self, member, wager):
        super().__init__()
        self.cards = [
            {"name": "Ace_clubs", "value": 11},
            {"name": "Ace_diamonds", "value": 11},
            {"name": "Ace_hearts", "value": 11},
            {"name": "Ace_spades", "value": 11},
            {"name": "King_clubs", "value": 10},
            {"name": "King_diamonds", "value": 10},
            {"name": "King_hearts", "value": 10},
            {"name": "King_spades", "value": 10},
            {"name": "Queen_clubs", "value": 10},
            {"name": "Queen_diamonds", "value": 10},
            {"name": "Queen_hearts", "value": 10},
            {"name": "Queen_spades", "value": 10},
            {"name": "Jack_clubs", "value": 10},
            {"name": "Jack_diamonds", "value": 10},
            {"name": "Jack_hearts", "value": 10},
            {"name": "Jack_spades", "value": 10},
            {"name": "10_clubs", "value": 10},
            {"name": "10_diamonds", "value": 10},
            {"name": "10_hearts", "value": 10},
            {"name": "10_spades", "value": 10},
            {"name": "9_clubs", "value": 9},
            {"name": "9_diamonds", "value": 9},
            {"name": "9_hearts", "value": 9},
            {"name": "9_spades", "value": 9},
            {"name": "8_clubs", "value": 8},
            {"name": "8_diamonds", "value": 8},
            {"name": "8_hearts", "value": 8},
            {"name": "8_spades", "value": 8},
            {"name": "7_clubs", "value": 7},
            {"name": "7_diamonds", "value": 7},
            {"name": "7_hearts", "value": 7},
            {"name": "7_spades", "value": 7},
            {"name": "6_clubs", "value": 6},
            {"name": "6_diamonds", "value": 6},
            {"name": "6_hearts", "value": 6},
            {"name": "6_spades", "value": 6},
            {"name": "5_clubs", "value": 5},
            {"name": "5_diamonds", "value": 5},
            {"name": "5_hearts", "value": 5},
            {"name": "5_spades", "value": 5},
            {"name": "4_clubs", "value": 4},
            {"name": "4_diamonds", "value": 4},
            {"name": "4_hearts", "value": 4},
            {"name": "4_spades", "value": 4},
            {"name": "3_clubs", "value": 3},
            {"name": "3_diamonds", "value": 3},
            {"name": "3_hearts", "value": 3},
            {"name": "3_spades", "value": 3},
            {"name": "2_clubs", "value": 2},
            {"name": "2_diamonds", "value": 2},
            {"name": "2_hearts", "value": 2},
            {"name": "2_spades", "value": 2}
        ]

        #Creates instance variables (lines 91-108)
        
        self.member = member
        self.wager = wager
        self.db = sqlite3.connect('points.db')
        self.cursor = self.db.cursor()
        self.points = self.check_db()
        
        self.playerCardList = []
        self.dealerCardList = []

        self.playerHand = 0
        self.dealerHand = 0
    
        self.dealerCardList.append("?")

        self.player_cards = ''
        self.dealer_cards = ''
        
        #Creates the initial default embed of the game.
        
        self.model = discord.Embed(title= None, colour=discord.Colour.blurple())
        self.model.add_field(name = "Your Cards:", value = self.player_cards)
        self.model.add_field(name = "Your Hand:", value = self.playerHand) 
        self.model.add_field(name = "Dealer Hand:", value = self.dealerHand)
        self.model.add_field(name = "Dealer Cards:", value = self.dealer_cards)
        
        # First two cards drawn for player and dealer
        
        for i in range(2):
            first_playerCard = random.choice(self.cards)
            self.playerHand += first_playerCard["value"]
            self.cards.remove(first_playerCard)
            self.playerCardList.append(first_playerCard["name"])
        
            
        self.first_dealerCard = random.choice(self.cards)
        self.cards.remove(self.first_dealerCard)

        self.second_dealerCard = random.choice(self.cards)
        self.dealerHand += self.second_dealerCard["value"]
        self.cards.remove(self.second_dealerCard)
        self.dealerCardList.append(self.second_dealerCard["name"])
        
        self.gameRunning = True
        
    def check_db(self):
        self.cursor.execute('SELECT * FROM main WHERE user = ?', (str(self.member.id),))
        result = self.cursor.fetchone()
        if result == None:
            self.cursor.execute('INSERT INTO main (user, points) VALUES (?, ?)',
            (str(self.member.id), 0))
            self.db.commit()
            return 0
        else:
            points = result[1]
            return points

    #Win and Lose update database. If the player wins then their wager is added to their current points, if they lose their wager is subtracted from their current points.

    def win(self):
        if self.points > 0:
            self.cursor.execute('UPDATE main SET points = ? WHERE user = ?', (self.points+self.wager, str(self.member.id)))
            self.db.commit()
        else:
            self.cursor.execute('UPDATE main SET points = ? WHERE user = ?', (self.points+10, str(self.member.id)))
            self.db.commit()
        self.cursor.close()
        self.db.close()
        

    def lose(self):
        if self.points > 0:
            self.cursor.execute('UPDATE main SET points = ? WHERE user = ?', (self.points-self.wager, str(self.member.id)))
            self.db.commit()
            self.cursor.close()
            self.db.close()

        
    #Updates fields of menu embed. Used in hit and stand functions each time a card is drawn.

    def update_fields(self):
        self.model.set_field_at(0, name = "Your Cards:", value = self.player_cards, inline=False)
        self.model.set_field_at(1, name = "Your Hand:", value = self.playerHand, inline=False) 
        self.model.set_field_at(2, name = "Dealer Hand:", value = self.dealerHand, inline=False)
        self.model.set_field_at(3, name = "Dealer Cards:", value = self.dealer_cards, inline=False)

    #Hit button. Each time the player hits, a card is randomly selected from the dictionary above. The selected card is added to the player's total score and removed from the current dictionary to avoid replacement and simulate an accurate game.

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.gameRunning:
            return
        
        playerCard = random.choice(self.cards)
        self.cards.remove(playerCard)
        try:

            if playerCard["name"].startswith('Ace'):
                if playerCard["value"] + self.playerHand > 21:
                    self.playerHand += 1
                else:
                    self.playerHand += playerCard["value"]
            else:
                self.playerHand += playerCard["value"]
        
            self.playerCardList.append(playerCard["name"])

            self.player_cards = " ".join(self.playerCardList)
            self.dealer_cards = " ".join(self.dealerCardList)

            if self.playerHand < 21:
                self.update_fields()
                await interaction.response.edit_message(embed=self.model)
            elif self.playerHand == 21:
                self.model.title="You Win!"
                self.model.colour=discord.Colour.green()
                await interaction.message.delete()
                await self.end(interaction)
                self.win()
                self.stop()
            else:
                self.model.title="Player Bust!"
                self.model.colour=discord.Colour.red()
                await interaction.message.delete()
                await self.end(interaction)
                self.lose()
                self.stop()
        except Exception as e:
            print(e)


    async def end(self, interaction: discord.Interaction):
        self.update_fields()
        await interaction.channel.send(embed=self.model)

    #Stand functionality of embed. Once the player clicks stand, the dealer draws until they either win, bust, or land on a value greater than or equal to 17.

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.gameRunning:
            return
        
        self.dealerCardList.pop(0)
        self.dealerCardList.insert(0, self.first_dealerCard["name"])
        self.dealerHand += self.first_dealerCard["value"]

        while self.gameRunning == True:

            self.player_cards = " ".join(self.playerCardList)
            self.dealer_cards = " ".join(self.dealerCardList)

            if self.dealerHand > self.playerHand and self.dealerHand <= 21:
                self.gameRunning = False
                self.model.title="Dealer Wins!"
                self.model.colour=discord.Colour.red()
                await interaction.message.delete()
                await self.end(interaction)
                self.lose()
                self.stop()
            elif self.dealerHand >= 17:
                self.gameRunning = False
                if self.dealerHand > 21:
                    self.model.title="Dealer Bust!"
                    self.model.colour=discord.Colour.green()
                    await interaction.message.delete()
                    await self.end(interaction)
                    self.win()
                    self.stop()
                elif self.dealerHand < self.playerHand:
                    self.model.title="You Win!"
                    self.model.colour=discord.Colour.green()
                    await interaction.message.delete()
                    await self.end(interaction)
                    self.win()
                    self.stop()
                elif self.dealerHand == self.playerHand:
                    self.model.title="It's a Tie!"
                    self.model.colour=discord.Colour.blurple()
                    await interaction.message.delete()
                    await self.end(interaction)
                    self.stop()
            else:
                dealerCard = random.choice(self.cards)
                self.cards.remove(dealerCard)
                if dealerCard["name"].startswith("Ace"):
                    if self.dealerHand + dealerCard["value"] > 21:
                        self.dealerHand += 1
                    else:
                        self.dealerHand += dealerCard["value"]
                else:
                    self.dealerHand += dealerCard["value"]
                    self.dealerCardList.append(dealerCard["name"])

                    
                    

#Begins the game of Blackjack. Handles initial win cases for dealer/player blackjack as well.

@bot.command() 
async def bet(ctx, wager: int):
    view = Menu(ctx.author, wager)
    points = view.check_db()
    if points - wager < 0:
        await ctx.reply("You do not have enough points to make that wager.")
        return
        
    if ctx.author.nick != None:
        menu = discord.Embed(title=f"Match Begun. Good luck, {ctx.author.nick}!", colour=discord.Colour.blurple())
    else:
        menu = discord.Embed(title=f"Match Begun. Good luck, {ctx.author}!", colour=discord.Colour.blurple())

    if view.playerHand == 21 and view.dealerHand == 21:
        menu.title = "It's a Tie!"
        menu.colour = discord.Colour.blurple()
        menu.add_field(name = "Your Hand:", value = view.playerHand)
        menu.add_field(name = "Dealer Hand:", value = view.dealerHand + view.first_dealerCard["value"])
        await ctx.reply(embed=menu)
        return
    
    elif view.playerHand == 21:
        menu.title = "Player Blackjack!"
        menu.colour = discord.Colour.green()
        menu.add_field(name = "Your Hand:", value = view.playerHand)
        menu.add_field(name = "Dealer Hand:", value = view.dealerHand)
        await ctx.reply(embed=menu)
        view.win()
        return
    
    elif view.dealerHand + view.first_dealerCard["value"] == 21:
        menu.title = "Dealer Blackjack!"
        menu.colour = discord.Colour.red()
        menu.add_field(name = "Your Hand:", value = view.playerHand)
        menu.add_field(name = "Dealer Hand:", value = view.dealerHand + view.first_dealerCard["value"])
        await ctx.reply(embed=menu)
        view.lose()
        return
        

    else:
        menu.add_field(name = "Your Hand:", value = view.playerHand)
        menu.add_field(name = "Dealer Hand:", value = view.dealerHand)
        await ctx.reply(embed=menu)
        await ctx.send(view=view) 


#Queries database to reply to user with amount of points they currently have.

@bot.command()
async def points(ctx):
    member = ctx.author
    db = sqlite3.connect('points.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM main WHERE user = ?', (str(member.id),))
    result = cursor.fetchone()
    if result == None:
        cursor.execute('INSERT INTO main (user, points) VALUES (?, ?)', (str(member.id), 0))
        db.commit()
        points = 0
    else:
        points = result[1]

    await ctx.reply(f'You have {points} points' if points != 1 else f'You have {points} point')

bot.run("********************************")
