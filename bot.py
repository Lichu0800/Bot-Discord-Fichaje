import discord
from discord.ext import commands
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# ID del canal donde el bot puede enviar mensajes
ALLOWED_CHANNEL_ID = 1263863216627384392  # Reemplaza con el ID del canal permitido

# Diccionario para almacenar las horas restantes por usuario
user_data = {}

# Función para formatear horas y minutos
def format_timedelta(td, is_favor=False):
    total_seconds = abs(td.total_seconds())  # Absoluto para manejar tiempos a favor
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    
    if total_seconds < 60:
        # Si es menos de un minuto, lo mostramos como 1 minuto
        minutes = 1
    
    if is_favor:
        return f"{hours} horas y {minutes} minutos a favor de Tekinho"
    else:
        return f"{hours} horas y {minutes} minutos"

# Comando para añadir horas en formato HH:MM
@bot.command(name="addhoras")
async def add_hours(ctx, time_str: str):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return  # El bot solo responde en el canal permitido

    await ctx.message.delete()  # Borrar el mensaje original
    try:
        hours, minutes = map(int, time_str.split(":"))
    except ValueError:
        await ctx.send("El formato debe ser HH:MM", delete_after=10)
        return

    user_id = str(ctx.author.id)
    if user_id not in user_data:
        user_data[user_id] = {"remaining_time": timedelta(hours=0), "start_time": None, "favor_time": timedelta(hours=0)}

    # Si el usuario tiene horas a favor, restarlas primero
    added_time = timedelta(hours=hours, minutes=minutes)

    if user_data[user_id]["favor_time"] > timedelta(0):
        if added_time >= user_data[user_id]["favor_time"]:
            added_time -= user_data[user_id]["favor_time"]
            user_data[user_id]["favor_time"] = timedelta(0)
        else:
            user_data[user_id]["favor_time"] -= added_time
            added_time = timedelta(0)
        
    user_data[user_id]["remaining_time"] += added_time

    embed = discord.Embed(
        title="Horas Añadidas",
        description=f"Se han añadido {hours} horas y {minutes} minutos. Tiempo restante: {format_timedelta(user_data[user_id]['remaining_time'])}",
        color=discord.Color.green()
    )
    embed.set_footer(text="Bot by: Tekinho")
    embed.add_field(name="Solicitado por", value=ctx.author.display_name, inline=True)
    await ctx.send(embed=embed)

# Comando para quitar horas
@bot.command(name="removehoras")
async def remove_hours(ctx, time_str: str):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return  # El bot solo responde en el canal permitido

    await ctx.message.delete()  # Borrar el mensaje original
    try:
        hours, minutes = map(int, time_str.split(":"))
    except ValueError:
        await ctx.send("El formato debe ser HH:MM", delete_after=10)
        return

    user_id = str(ctx.author.id)
    if user_id not in user_data:
        user_data[user_id] = {"remaining_time": timedelta(hours=0), "start_time": None, "favor_time": timedelta(hours=0)}

    removed_time = timedelta(hours=hours, minutes=minutes)

    if user_data[user_id]["remaining_time"] >= removed_time:
        user_data[user_id]["remaining_time"] -= removed_time
    else:
        # Si la resta genera horas a favor
        remaining_deficit = removed_time - user_data[user_id]["remaining_time"]
        user_data[user_id]["remaining_time"] = timedelta(0)
        user_data[user_id]["favor_time"] += remaining_deficit

    embed = discord.Embed(
        title="Horas Removidas",
        description=f"Se han removido {hours} horas y {minutes} minutos. Tiempo restante: {format_timedelta(user_data[user_id]['remaining_time'])}",
        color=discord.Color.red()
    )
    embed.set_footer(text="Bot by: Tekinho")
    embed.add_field(name="Solicitado por", value=ctx.author.display_name, inline=True)
    await ctx.send(embed=embed)

# Comando para registrar la entrada
@bot.command(name="entrada")
async def entrada(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return  # El bot solo responde en el canal permitido

    await ctx.message.delete()  # Borrar el mensaje original
    user_id = str(ctx.author.id)
    if user_id not in user_data:
        user_data[user_id] = {"remaining_time": timedelta(hours=0), "start_time": None, "favor_time": timedelta(hours=0)}

    if user_data[user_id]["start_time"] is None:
        user_data[user_id]["start_time"] = datetime.now()
        embed = discord.Embed(
            title="Entrada Registrada",
            description="Has comenzado a fichar.",
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title="Error",
            description="Ya has fichado la entrada.",
            color=discord.Color.red()
        )

    embed.set_footer(text="Bot by: Tekinho")
    embed.add_field(name="Solicitado por", value=ctx.author.display_name, inline=True)
    await ctx.send(embed=embed)

# Comando para registrar la salida
@bot.command(name="salida")
async def salida(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return  # El bot solo responde en el canal permitido

    await ctx.message.delete()  # Borrar el mensaje original
    user_id = str(ctx.author.id)
    if user_id not in user_data or user_data[user_id]["start_time"] is None:
        embed = discord.Embed(
            title="Error",
            description="No has fichado la entrada.",
            color=discord.Color.red()
        )
    else:
        # Calcular las horas trabajadas
        start_time = user_data[user_id]["start_time"]
        worked_time = datetime.now() - start_time

        # Restar las horas trabajadas de las horas restantes
        remaining_time = user_data[user_id]["remaining_time"] - worked_time
        user_data[user_id]["start_time"] = None

        is_favor = remaining_time < timedelta(0)  # Ver si hay tiempo a favor
        if is_favor:
            user_data[user_id]["favor_time"] += abs(remaining_time)
            remaining_time = timedelta(0)

        embed = discord.Embed(
            title="Salida Registrada",
            description=f"Has fichado la salida. Tiempo trabajado: {format_timedelta(worked_time)}. Tiempo {'a favor' if is_favor else 'restante'}: {format_timedelta(user_data[user_id]['remaining_time'], is_favor)}",
            color=discord.Color.orange()
        )
        user_data[user_id]["remaining_time"] = remaining_time

    embed.set_footer(text="Bot by: Tekinho")
    embed.add_field(name="Solicitado por", value=ctx.author.display_name, inline=True)
    await ctx.send(embed=embed)

# Comando para mostrar las horas restantes o a favor
@bot.command(name="horasrestantes")
async def horas_restantes(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return  # El bot solo responde en el canal permitido

    await ctx.message.delete()  # Borrar el mensaje original
    user_id = str(ctx.author.id)
    if user_id in user_data:
        remaining_time = user_data[user_id]["remaining_time"]
        favor_time = user_data[user_id]["favor_time"]

        if favor_time > timedelta(0):
            description = f"Tiempo a favor: {format_timedelta(favor_time, True)}"
        else:
            description = f"Tiempo restante: {format_timedelta(remaining_time)}"

        embed = discord.Embed(
            title="Horas Restantes",
            description=description,
            color=discord.Color.purple()
        )
    else:
        embed = discord.Embed(
            title="Sin Datos",
            description="No tienes horas registradas.",
            color=discord.Color.red()
        )

    embed.set_footer(text="Bot by: Tekinho")
    embed.add_field(name="Solicitado por", value=ctx.author.display_name, inline=True)
    await ctx.send(embed=embed)

# Comando de ayuda personalizado
@bot.command(name="ayudah")
async def help_command(ctx):
    await ctx.message.delete()  # Borrar el mensaje original
    embed = discord.Embed(
        title="Ayuda",
        description="Lista de comandos disponibles:",
        color=discord.Color.blue()
    )
    embed.add_field(name="/addhoras", value="Añade horas al usuario. Formato: HH:MM", inline=False)
    embed.add_field(name="/removehoras", value="Remueve horas del usuario. Formato: HH:MM", inline=False)
    embed.add_field(name="/entrada", value="Marca la entrada del usuario.", inline=False)
    embed.add_field(name="/salida", value="Marca la salida del usuario y calcula las horas trabajadas.", inline=False)
    embed.add_field(name="/horasrestantes", value="Muestra las horas restantes o a favor del usuario.", inline=False)
    embed.set_footer(text="Bot by: Tekinho")

    await ctx.send(embed=embed)





#bot.run('') # PUT YOU DISCORD TOKEN
