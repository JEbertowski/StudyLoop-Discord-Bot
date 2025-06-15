import discord
from discord.ext import commands
import random
import json
import os
from fpdf import FPDF
import fitz
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")




flashcards = {}  # key = user_id, value = list of {"q": ..., "a": ...}
active_flashcards = {}  # key = user_id, value = currently active card

def save_flashcards():
    with open("flashcards.json", "w") as f:
        json.dump(flashcards, f, indent=4)

def load_flashcards():
    global flashcards
    try:
        with open("flashcards.json", "r") as f:
            flashcards = json.load(f)
    except FileNotFoundError:
        flashcards = {}
load_flashcards()

# Set up the bot's intents
intents = discord.Intents.default()
intents.message_content = True

# Create the bot instance with a command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Event that triggers when the bot connects
@bot.event
async def on_ready():
    print(f"📚 StudyLoop is online as {bot.user}!")

# Simple test command to confirm the bot is working
@bot.command()
async def hello(ctx):
    await ctx.send("Hey there! I’m StudyLoop, your flashcard study buddy!")

@bot.command()
async def addcard(ctx, *, content: str):
    try:
        parts = content.split("|")

        if len(parts) < 2 or len(parts) > 3:
            await ctx.send("❌ Use the format: `!addcard question | answer | [optional tag]`")
            return

        question = parts[0].strip()
        answer = parts[1].strip()
        tag = parts[2].strip().lower() if len(parts) == 3 else "general"

        user_id = str(ctx.author.id)

        if user_id not in flashcards:
            flashcards[user_id] = []

        flashcards[user_id].append({"q": question, "a": answer, "tag": tag})
        save_flashcards()

        await ctx.send(f"✅ Flashcard added!\n**Q:** {question}\n**A:** {answer}\n🏷️ Tag: `{tag}`")

    except Exception as e:
        await ctx.send("❌ Something went wrong while adding the flashcard.")
        print(f"Error in !addcard: {e}")

@bot.command()
async def viewcards(ctx, tag: str = None, limit: int = 10):
    user_id = str(ctx.author.id)

    if user_id not in flashcards or not flashcards[user_id]:
        await ctx.send("📭 You have no flashcards yet.")
        return

    tag = tag.lower() if tag else None
    pool = [card for card in flashcards[user_id] if tag is None or card.get("tag", "general") == tag]

    if not pool:
        await ctx.send(f"❌ No flashcards found for tag `{tag}`.")
        return

    response = f"📘 **Your Flashcards ({len(pool)})**:\n"
    for i, card in enumerate(pool, start=1):
        if i > limit:
            break

        if tag and card.get("tag") != tag:
            continue

        if "choices" in card and "correct" in card:
            options = "\n".join(
                [f"    {chr(97 + idx)}. {choice}" for idx, choice in enumerate(card["choices"])]
            )
            correct_letter = card["correct"]
            response += f"\n`{i}.` **Q:** {card['q']} | 🏷️ `{card.get('tag', 'general')}`\n{options}\n*Correct: {correct_letter}*"
        else:
            response += f"\n`{i}.` **Q:** {card['q']} | **A:** {card['a']} | 🏷️ `{card.get('tag', 'general')}`"

    if len(response) > 2000:
        await ctx.send("⚠️ Too many cards to display. (Feature coming soon: export to file!)")
    else:
        await ctx.send(response)

@bot.command()
async def study(ctx, tag: str = None):
    user_id = str(ctx.author.id)

    if user_id not in flashcards or not flashcards[user_id]:
        await ctx.send("📭 You have no flashcards to study.")
        return

    # Filter by tag if one is provided
    tag = tag.lower() if tag else None
    pool = [card for card in flashcards[user_id] if tag is None or card.get("tag", "general") == tag]

    if not pool:
        await ctx.send(f"❌ No flashcards found for tag `{tag}`.")
        return

    card = random.choice(pool)
    active_flashcards[user_id] = card

    await ctx.send(f"🧠 **Study Time!**\n**Q:** {card['q']}\n🏷️ Tag: `{card.get('tag', 'general')}`\n_Reply with `!reveal` to see the answer._")

@bot.command()
async def reveal(ctx):
    user_id = str(ctx.author.id)

    if user_id not in active_flashcards:
        await ctx.send("❌ No active flashcard. Use `!study` first.")
        return

    answer = active_flashcards[user_id]["a"]
    await ctx.send(f"📘 **A:** {answer}")

    # Optionally clear the active flashcard after revealing
    del active_flashcards[user_id]

@bot.command()
async def deletecard(ctx, index: int):
    user_id = str(ctx.author.id)

    if user_id not in flashcards or not flashcards[user_id]:
        await ctx.send("📭 You have no flashcards to delete.")
        return

    if index < 1 or index > len(flashcards[user_id]):
        await ctx.send(f"❌ Invalid index. Use a number from 1 to {len(flashcards[user_id])}.")
        return

    removed = flashcards[user_id].pop(index - 1)
    save_flashcards()
    await ctx.send(f"🗑️ Deleted flashcard #{index}:\n**Q:** {removed['q']}\n**A:** {removed['a']}")

@bot.command()
async def clearcards(ctx):
    user_id = str(ctx.author.id)

    if user_id not in flashcards or not flashcards[user_id]:
        await ctx.send("📭 You have no flashcards to clear.")
        return

    flashcards[user_id] = []
    save_flashcards()
    await ctx.send("🧼 All your flashcards have been deleted.")

@bot.command()
async def viewtags(ctx):
    user_id = str(ctx.author.id)

    if user_id not in flashcards or not flashcards[user_id]:
        await ctx.send("📭 You have no flashcards yet.")
        return

    tags = sorted(set(card.get("tag", "general") for card in flashcards[user_id]))
    tag_list = ", ".join(f"`{tag}`" for tag in tags)

    await ctx.send(f"🏷️ **Tags in your flashcards:**\n{tag_list}")

# @bot.command()
# async def exportcards(ctx, tag: str = None):
#     user_id = str(ctx.author.id)
#
#     if user_id not in flashcards or not flashcards[user_id]:
#         await ctx.send("📭 You have no flashcards to export.")
#         return
#
#     tag = tag.lower() if tag else None
#     cards = [card for card in flashcards[user_id] if tag is None or card.get("tag", "general") == tag]
#
#     if not cards:
#         await ctx.send(f"❌ No flashcards found for tag `{tag}`.")
#         return
#
#     filename = f"{user_id}_flashcards.txt"
#     with open(filename, "w", encoding="utf-8") as f:
#         for i, card in enumerate(cards, start=1):
#             f.write(f"{i}. Q: {card['q']}\n   A: {card['a']}\n   Tag: {card.get('tag', 'general')}\n\n")
#
#     await ctx.send("📄 Here are your exported flashcards:", file=File(filename))
#
#     # Clean up the file after sending
#     os.remove(filename)

@bot.command()
async def cleartag(ctx, tag: str):
    user_id = str(ctx.author.id)
    tag = tag.lower()

    if user_id not in flashcards or not flashcards[user_id]:
        await ctx.send("📭 You have no flashcards to modify.")
        return

    original_count = len(flashcards[user_id])
    flashcards[user_id] = [card for card in flashcards[user_id] if card.get("tag", "general") != tag]

    if len(flashcards[user_id]) == original_count:
        await ctx.send(f"❌ No flashcards found for tag `{tag}`.")
        return

    save_flashcards()
    await ctx.send(f"🧹 Cleared all flashcards tagged `{tag}`.")

@bot.command()
async def upload(ctx):
    if not ctx.message.attachments:
        await ctx.send("❌ Please attach a PDF file with the `!upload` command.")
        return

    attachment = ctx.message.attachments[0]

    if not attachment.filename.lower().endswith(".pdf"):
        await ctx.send("❌ Only PDF files are supported.")
        return

    file_path = f"temp_{ctx.author.id}.pdf"
    await attachment.save(file_path)

    # Extract text using PyMuPDF
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        os.remove(file_path)
    except Exception as e:
        await ctx.send("❌ Failed to read the PDF.")
        print(f"PDF error: {e}")
        return

    if not text.strip():
        await ctx.send("📄 The PDF appears to be empty.")
        return

    # Basic Q: A: line parser
    lines = text.splitlines()
    imported = 0
    user_id = str(ctx.author.id)

    if user_id not in flashcards:
        flashcards[user_id] = []

    question = ""
    answer = ""
    imported = 0
    skipped = 0

    for line in lines:
        line = line.strip()

        # Detect question
        if line and (line[0].isdigit() or line.lower().startswith("q")) and "?" in line:
            question = line
            answer = ""

        # Detect answer
        elif line.lower().startswith("a.") or line.lower().startswith("answer:"):
            answer = line.split(".", 1)[-1].strip() if "." in line else line.split(":", 1)[-1].strip()

            if question and answer:
                flashcards[user_id].append({
                    "q": question,
                    "a": answer,
                    "tag": "imported"
                })
                imported += 1
                question = ""
                answer = ""
            else:
                skipped += 1

        # Handle random/unsupported lines
        elif line:
            skipped += 1
        # MCQ = Multiple Choice Questions
        # MCQ parsing block – DO NOT INDENT FURTHER
        mcq_question = ""
        mcq_choices = {}
        mcq_answer = ""

        for i in range(len(lines)):
            line = lines[i].strip()

            if (line[0].isdigit() or line.lower().startswith("q")) and "?" in line:
                mcq_question = line
                mcq_choices = {}
                mcq_answer = ""

                j = i + 1
                while j < len(lines):
                    lookahead = lines[j].strip()

                    if lookahead.lower().startswith(("a.", "b.", "c.", "d.")):
                        choice_letter = lookahead[0].lower()
                        choice_text = lookahead[2:].strip()
                        mcq_choices[choice_letter] = choice_text

                    elif lookahead.lower().startswith("answer:"):
                        mcq_answer = lookahead.split(":", 1)[-1].strip().lower()
                        break

                    j += 1

                if mcq_question and mcq_choices and mcq_answer in mcq_choices:
                    flashcards[user_id].append({
                        "q": mcq_question,
                        "choices": [mcq_choices[k] for k in sorted(mcq_choices.keys())],
                        "correct": mcq_answer,
                        "tag": "imported"
                    })
                    imported += 1
                    skipped += (j - i - len(mcq_choices) - 1)

        # 🔽 Attempt to detect MCQ blocks
        mcq_question = ""
        mcq_choices = {}
        mcq_answer = ""

        for i in range(len(lines)):
            line = lines[i].strip()

    save_flashcards()

    if imported:
        response = f"✅ Imported `{imported}` flashcards from the PDF."
        if skipped:
            response += f"\n⚠️ Skipped `{skipped}` line(s) that couldn’t be parsed."
        response += "\nUse `!viewcards imported` to see them."
        await ctx.send(response)
    else:
        await ctx.send("⚠️ No flashcards were created. Make sure the PDF is in a supported format.")

@bot.command()
async def study_mcq(ctx, tag: str = "imported"):
    user_id = str(ctx.author.id)

    if user_id not in flashcards:
        await ctx.send("📭 You don't have any flashcards yet.")
        return

    pool = [
        card for card in flashcards[user_id]
        if card.get("tag", "general") == tag and "choices" in card and "correct" in card
    ]

    if not pool:
        await ctx.send(f"❌ No multiple choice flashcards found with tag `{tag}`.")
        return

    # Pick a random card
    card = random.choice(pool)
    active_flashcards[user_id] = card  # Store current question for checking later

    # Build choices display
    choices = "\n".join(
        [f"{chr(97 + idx)}. {choice}" for idx, choice in enumerate(card["choices"])]
    )

    await ctx.send(
        f"🧠 **Study Time!**\n"
        f"**Q:** {card['q']}\n"
        f"{choices}\n\n"
        f"_Reply with `!answer a/b/c/...` to answer._"
    )

@bot.command()
async def answer(ctx, choice: str):
    user_id = str(ctx.author.id)

    if user_id not in active_flashcards:
        await ctx.send("❌ No active question. Use `!study_mcq` to begin.")
        return

    card = active_flashcards[user_id]
    correct = card.get("correct", "").lower()
    choice = choice.lower()

    if choice == correct:
        await ctx.send(f"✅ Correct! **{choice}** was the right answer.")
    else:
        await ctx.send(f"❌ Incorrect. You answered **{choice}**, but the correct answer was **{correct}**.")

    del active_flashcards[user_id]  # Clear active card after answering

@bot.command()
async def exportcards(ctx):
    user_id = str(ctx.author.id)

    if user_id not in flashcards or not flashcards[user_id]:
        await ctx.send("📭 You have no flashcards to export.")
        return

    filename = f"flashcards_{user_id}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for i, card in enumerate(flashcards[user_id], start=1):
            f.write(f"{i}. Q: {card['q']}\n")

            if 'a' in card:  # Normal flashcard
                f.write(f"A: {card['a']}\n")
            elif 'choices' in card and 'correct' in card:  # MCQ flashcard
                for idx, choice in enumerate(card["choices"]):
                    letter = chr(97 + idx)  # a, b, c, ...
                    f.write(f"{letter}. {choice}\n")
                f.write(f"Correct: {card['correct']}\n")

            f.write(f"Tag: {card.get('tag', 'general')}\n\n")

    await ctx.send(file=discord.File(filename))
    os.remove(filename)

@bot.command()
async def exportpdf(ctx):
    from fpdf import FPDF

    user_id = str(ctx.author.id)
    if user_id not in flashcards or not flashcards[user_id]:
        await ctx.send("📭 You have no flashcards to export.")
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for i, card in enumerate(flashcards[user_id], start=1):
        pdf.cell(0, 10, f"{i}. Q: {card['q']}", ln=True)

        if "choices" in card and "correct" in card:
            if isinstance(card["choices"], dict):
                for letter, text in card["choices"].items():
                    pdf.cell(0, 10, f"   {letter}. {text}", ln=True)
                pdf.cell(0, 10, f"Correct: {card['correct']}", ln=True)
        else:
            pdf.cell(0, 10, f"A: {card['a']}", ln=True)

        pdf.cell(0, 10, f"Tag: {card.get('tag', 'general')}", ln=True)
        pdf.cell(0, 10, "", ln=True)

    filename = f"{ctx.author.id}_flashcards.pdf"
    pdf.output(filename)
    await ctx.send(file=discord.File(filename))
    os.remove(filename)

@bot.command(name="commands")
async def show_commands(ctx):
    help_text = """
📘 **StudyLoop Help Menu**

**Flashcard Commands:**
• `!addcard question | answer | [optional tag]` – Add a new flashcard manually  
• `!viewcards [tag]` – View your flashcards (optionally filter by tag)  
• `!clearcards` – Delete all your flashcards  

**Study Commands:**
• `!study [tag]` – Study flashcards one by one  
• `!reveal` – Reveal the answer to the current flashcard  
• `!study_mcq [tag]` – Study multiple-choice flashcards (auto-check answer)  
• `!answer a/b/c/...` – Submit your answer for MCQ  

**Import/Export:**
• `!upload` – Upload a PDF of flashcards to import  
• `!exportcards` – Export flashcards as text  
• `!exportpdf` – Export flashcards as a PDF file  
"""
    await ctx.send(help_text)

# Run the bot using the token
bot.run(TOKEN)
