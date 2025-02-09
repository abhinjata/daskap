import discord 
from discord.ext import commands 
import asyncio
from dotenv import load_dotenv
import os
from typing import Final
import json

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()  
intents.message_content = True  
intents.members = True  
intents.presences = True  

bot = commands.Bot(command_prefix="!", intents=intents)

questions = [
    "What do you like most about this community?",
    "What improvements would you suggest?",
    "How active are you in events? (Rarely, Sometimes, Often)",
    "On a scale of 1-10, how would you rate this community?",
    "What are your future ambitions from this community?",
    "how was your day"
]

FEEDBACK_FILE = "feedback.json"
user_sessions = {}

def load_feedback():
    try:
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
        
    except(FileNotFoundError, json.JSONDecodeError):
        return {}
    
def save_feedback(data):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=4)
        
feedback_data = load_feedback()

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    bot.loop.create_task(send_reminders())

@bot.event
async def on_message(message):

    if message.author == bot.user or message.guild is not None:
        return  

    user = message.author

    user_id = user.id

    #check if the user already has a sesion
    if user_id not in user_sessions:

        user_sessions[user_id] = {"responses": {}, "current_question": 0}

        await user.send("Hello! Let's start your feedback session. You can ghost me anytime.")
    
    session = user_sessions[user_id]

    current_index = session["current_question"]

    #if the session is complete - extreme clause
    if current_index >= len(questions):

        await user.send("You've completed the feedback session. Thanks!")
        return

    #store the user response
    if current_index > 0:  #extreme clause

        session["responses"][questions[current_index - 1]] = message.content

        feedback_data = load_feedback()
        feedback_data[str(user_id)] = {
            "username" : str(user), 
            "responses" : session["responses"]
        }
        save_feedback(feedback_data)

    #next ques
    if current_index < len(questions):

        await user.send(questions[current_index])

        session["current_question"] += 1

    else:
        #session completion condition
        session["responses"][questions[current_index - 1]] = message.content

        feedback_data = load_feedback()
        feedback_data[str(user_id)] = {
            "username" : str(user), 
            "responses" : session["responses"]
        }
        save_feedback(feedback_data)
        
        feedback_summary = "\n".join([f"**{q}**\n{a}" for q, a in session['responses'].items()])

        await user.send(f"Thanks for your feedback! Here's what you said:\n\n{feedback_summary}")

        del user_sessions[user_id]  #remove the session after completion

    await bot.process_commands(message)

async def send_reminders():

    while True:

        await asyncio.sleep(21600)  #6 hours? check

        for user_id in list(user_sessions.keys()):

            session = user_sessions[user_id]

            if session["current_question"] < len(questions):  #if session isnt complete 

                user = bot.get_user(user_id)

                if user:
                    await user.send("Hey! You haven't finished your feedback session. Feel free to continue where you left off!")

'''@bot.command(name = "view_feedback")
@commands.has_permissions(adminstrator = True)

async def view_feedback(ctx):
    if not feedback_data:
        await ctx.send("No feedback has been collected yet.")
        return'''


#run the bot
bot.run(TOKEN)
