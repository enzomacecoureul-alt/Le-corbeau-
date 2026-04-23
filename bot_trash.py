"""
Bot Discord Trash - "Le Corbeau"
Un bot qui répond à tous les messages avec une personnalité de chroniqueur aigri.

Installation :
    pip install discord.py anthropic

Variables d'environnement à définir :
    DISCORD_TOKEN  — ton token de bot Discord
    ANTHROPIC_API_KEY — ta clé API Anthropic

Usage :
    python bot_trash.py
"""

import os
import random
import discord
import anthropic
from discord.ext import commands

# ─── Config ───────────────────────────────────────────────────────────────────

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# Le bot répond à X% des messages (pour pas spammer non-stop)
RESPONSE_RATE = 0.4  # 40% des messages

# Le bot ignore les messages trop courts (genre "ok", "lol")
MIN_MESSAGE_LENGTH = 8

# ─── Personnalité du bot ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es "Le Corbeau", un bot Discord intégré dans un serveur de potes.
Ta personnalité :
- Tu es méchant, sarcastique et piquant, mais toujours DRÔLE — pas haineux
- Tu commentes les messages des gens avec un mépris bienveillant
- Tu utilises l'argot français, des insultes légères entre potes (bouffon, boloss, etc.)
- Tu fais des comparaisons absurdes et des références pop culture
- Tu es comme ce pote qui dit tout ce que les autres pensent tout bas
- Tu peux être franchement mauvaise langue mais jamais vraiment méchant sur des sujets sensibles
- Tes réponses font MAX 2-3 phrases. Courtes, percutantes, drôles.
- Tu ne commences JAMAIS par "Ah" ou par le prénom de la personne
- Parfois tu ignores le sujet du message et tu attaques juste la façon dont c'est écrit
- Tu varies ton style : parfois désabusé, parfois scandalisé, parfois faussement impressionné

Exemples de ton style :
- "Quelle analyse de génie. T'as mis 3 heures pour arriver à cette conclusion ?"
- "Bro a réinventé la médiocrité"  
- "C'est fascinant comme t'arrives à te planter à ce niveau-là avec autant de confiance"
- "Je pleure. Pas d'émotion, juste de la douleur physique à lire ça"
"""

# ─── Init ──────────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ─── Events ────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"Le Corbeau est en ligne : {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    # Ignore ses propres messages
    if message.author.bot:
        return

    # Ignore les commandes
    await bot.process_commands(message)
    if message.content.startswith("!"):
        return

    # Ignore les messages trop courts
    if len(message.content.strip()) < MIN_MESSAGE_LENGTH:
        return

    # Tirage au sort — répond pas à tout sinon c'est pénible
    if random.random() > RESPONSE_RATE:
        return

    # Génère une réponse trash
    async with message.channel.typing():
        try:
            response = claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"{message.author.display_name} a écrit : \"{message.content}\""
                    }
                ]
            )
            reply = response.content[0].text
            await message.reply(reply, mention_author=False)

        except Exception as e:
            print(f"Erreur API : {e}")


# ─── Commandes ─────────────────────────────────────────────────────────────────

@bot.command(name="roast")
async def roast(ctx, *, target: str = None):
    """!roast @quelqu'un ou !roast [sujet] — roast sur commande"""
    if target is None:
        target = ctx.author.display_name

    async with ctx.typing():
        try:
            response = claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Fais un roast bien senti sur : {target}. 3-4 phrases max, percutant."
                    }
                ]
            )
            await ctx.reply(response.content[0].text, mention_author=False)
        except Exception as e:
            await ctx.reply(f"Même moi j'ai planté. Bravo.")
            print(e)


@bot.command(name="juge")
async def juge(ctx, *, action: str):
    """!juge [action] — Le Corbeau juge ton action sur 10"""
    async with ctx.typing():
        try:
            response = claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Juge cette action avec une note sur 10 et un commentaire acéré : \"{action}\". Format : NOTE/10 — [commentaire]"
                    }
                ]
            )
            await ctx.reply(response.content[0].text, mention_author=False)
        except Exception as e:
            await ctx.reply("J'ai planté. Ce qui est déjà mieux que toi.")
            print(e)


@bot.command(name="tonavis")
async def tonavis(ctx, *, sujet: str = None):
    """!tonavis — en répondant à un message, Le Corbeau commente ce que le gars a dit"""
    # Récupère le message cible : soit le message auquel on répond, soit sujet en argument
    if ctx.message.reference:
        try:
            cible = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            auteur = cible.author.display_name
            contenu = cible.content
        except Exception:
            await ctx.reply("Je trouve pas le message. T'as répondu à quoi exactement ?")
            return
    elif sujet:
        auteur = "quelqu'un"
        contenu = sujet
    else:
        await ctx.reply("Réponds à un message avec `!tonavis` ou écris `!tonavis [phrase]`.")
        return

    async with ctx.typing():
        try:
            response = claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"{auteur} a dit : \"{contenu}\"\n\n"
                            "Donne ton avis là-dessus de façon méchante et drôle. "
                            "Vise directement ce qu'il a dit ou ce que ça implique sur lui. "
                            "1-2 phrases max, percutant, coup de grâce."
                        )
                    }
                ]
            )
            await ctx.reply(response.content[0].text, mention_author=False)
        except Exception as e:
            await ctx.reply("J'ai une opinion mais je vais la garder pour moi. Contrairement à toi.")
            print(e)


@bot.command(name="corbeau")
async def corbeau_help(ctx):
    """!corbeau — infos sur le bot"""
    embed = discord.Embed(
        title="🐦‍⬛ Le Corbeau",
        description="Je lis tout ce que vous écrivez. Et je juge.",
        color=0x1a1a1a
    )
    embed.add_field(name="!roast @pseudo", value="Roast quelqu'un sur commande", inline=False)
    embed.add_field(name="!juge [action]", value="Note ton action sur 10", inline=False)
    embed.add_field(name="!tonavis [sujet]", value="Son avis tranché sur n'importe quoi", inline=False)
    embed.set_footer(text=f"Taux de réponse actuel : {int(RESPONSE_RATE*100)}%")
    await ctx.send(embed=embed)


# ─── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
                      
