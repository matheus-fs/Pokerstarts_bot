import os
import discord
from discord.ext.commands import Bot
import datetime as dt
from keep_alive import keep_alive
from replit import db
from discord.ext import commands
from discord.utils import get
import db_control as dbcontrol
import random
import datetime as dt

# TOKEN AND GENERAL DEFINITIONS =====================
TOKEN = os.environ['BOT_TOKEN']

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = Bot(command_prefix="$", intents=intents)


# DICE DEFINIITONS ===========================
def roll_d100():
  return random.randint(1, 100)


async def result_100(ctx):

  #getting username
  id = ctx.author.id

  # Update user status
  new_value = '01/01/2000'
  dbcontrol.update_user_db(id, 'blocked_until', new_value)
  new_value = 'ready'
  dbcontrol.update_user_db(id, 'status', new_value)
  new_value = 'Rei do Dado'
  dbcontrol.update_user_db(id, 'titulo', new_value)

  # Remove role from all users
  await remove_role_all_users(ctx, 'Rei do dado')
  # Add role only to user that rolled 100
  await add_role(ctx, ctx.author, 'Rei do dado')
  # Send message
  await ctx.send(f'AJOELHEM-SE PERANTE {ctx.author.name}, O REI DO DADO')


async def result_1(ctx):

  #getting username
  id = ctx.author.id

  # Update user status
  new_value = (dt.date.today() + dt.timedelta(days=1)).strftime('%d/%m/%Y')
  dbcontrol.update_user_db(id, 'blocked_until', new_value)
  new_value = 'Erro crítico'
  dbcontrol.update_user_db(id, 'status', new_value)
  new_value = 'Pereba'
  dbcontrol.update_user_db(id, 'titulo', new_value)

  # Send message
  await ctx.send(f'```kkkkkkkkkk {ctx.author.name} tu é um comédia, n joga amanha```'
                 )


def date_handler(string):
  if string == 'tomorrow':
    return (dt.date.today() + dt.timedelta(days=1)).strftime('%d/%m/%Y')
  elif string == '':
    return '01/01/2000'


async def perform_action(ctx, values):

  #getting username
  id = ctx.author.id

  new_value = date_handler(values['blocked_until'])
  dbcontrol.update_user_db(id, 'blocked_until', new_value)
  dbcontrol.update_user_db(id, 'status', values['status'])
  dbcontrol.update_user_db(id, 'titulo', values['titulo'])

  if values['titulo'] != '':
    # Remove role from all users
    await remove_role_all_users(ctx, values['titulo'])
    # Add role only to user that rolled 100
    await add_role(ctx, ctx.author, values['titulo'])

  # Send message
  str_1 = values['str_1']
  str_2 = values['str_2']
  await ctx.send(f'```{str_1}{ctx.author.name}{str_2}```')


rules_dict = {
  1: {
    'role': 'Rei do Dado',
    'action_values': {
      'blocked_until': 'tomorrow',
      'status': 'erro_critico',
      'titulo': 'Pereba',
      'str_1': 'kkkkkkkkkk ',
      'str_2': ' tu é um comédia, n joga amanha'
    }
  },
  24: {
    'action_values': {
      'blocked_until': '',
      'status': 'ready',
      'titulo': 'Biba',
      'str_1': '',
      'str_2': ' de a binda nesse exato momento, tu é biba'
    }
  },
  51: {
    'action_values': {
      'blocked_until': '',
      'status': 'ready',
      'titulo': '',
      'str_1': '',
      'str_2': ' mande uma foto bebendo uma :baby_bottle:'
    }
  },
  60: {
    'action_values': {
      'blocked_until': '',
      'status': 'ready',
      'titulo': '',
      'str_1': '',
      'str_2': ' se senta na minha :eggplant:'
    }
  },
  66: {
    'action_values': {
      'blocked_until': '',
      'status': 'ready',
      'titulo': '',
      'str_1': '',
      'str_2': ' escolha alguem para nao jogar amanhã :japanese_ogre:'
    }
  },
  70: {
    'action_values': {
      'blocked_until': '',
      'status': 'play_again',
      'titulo': '',
      'str_1': '',
      'str_2': ' se tenta de novo hj! :peach:'
    }
  },
  80: {
    'action_values': {
      'blocked_until': '',
      'status': 'play_again',
      'titulo': '',
      'str_1': '',
      'str_2': ' peça p alguem te autorizar a jogar de novo'
    }
  },
  90: {
    'action_values': {
      'blocked_until': '',
      'status': 'ready',
      'titulo': '',
      'str_1': '',
      'str_2': ' escolhe alguem p jogar de novo'
    }
  },
  100: {
    'action_values': {
      'blocked_until': '',
      'status': 'ready',
      'titulo': 'Rei do dado',
      'str_1': 'AJOELHEM-SE PERANTE ',
      'str_2': ', O REI DO DADO'
    }
  },
}


async def check_dice_result(ctx, result):

  global rules_dict

  if result not in rules_dict.keys():
    pass
  else:
    await perform_action(ctx, rules_dict[result]['action_values'])


# DISCORD ROLE MANIPULATION ===========================
async def add_role(ctx, member, role_name):
  role = get(ctx.guild.roles, name=role_name)
  await member.add_roles(role)


async def remove_role_all_users(ctx, role_name):
  role = get(ctx.guild.roles, name=role_name)
  for member in ctx.guild.members:
    await member.remove_roles(role)


def check_user_status(ctx):

  author = ctx.author

  id = str(author.id)

  last_played_date = db['user_status'][id]['last_played']
  last_played_date = dt.datetime.strptime(last_played_date, '%d/%m/%Y').date()

  blocked_until = db['user_status'][id]['blocked_until']
  blocked_until = dt.datetime.strptime(blocked_until, '%d/%m/%Y').date()

  # checks if player already rolled the dice today
  if db['user_status'][str(author.id)]['status'] == 'play_again':
    dbcontrol.update_user_db(author.id, 'status', 'ready')
    return True, 'nothing'
  elif last_played_date == dt.date.today():
    msg = f'``` {author.name} tu ja jogou hj irmão, tenha paciencia!```'
    return False, msg
  elif (db['user_status'][str(author.id)]['status'] !=
        'ready') and (blocked_until >= dt.date.today()):
    msg = f'```{author.name} não pode jogar, vacilao! - bloqueado até {blocked_until}```'
    return False, msg
  else:
    dbcontrol.update_user_db(author.id, 'status', 'ready')
    last_played = dt.date.today().strftime('%d/%m/%Y')
    dbcontrol.update_user_db(author.id, 'last_played', last_played)
    return True, 'nothing'


# BOT ACTIONS ==========================
@bot.command()
async def rolada(ctx):

  # Getting the author from the message
  author = ctx.author

  dbcontrol.check_user_in_db(author.id, author.name)

  # Check if author can play
  can_play, msg = check_user_status(ctx)
  if can_play:
    pass
  else:
    await ctx.send(msg)
    return

  # Roll the dice and get action
  dice_result = roll_d100()
  dbcontrol.save_roll(author.id, author.name, dice_result)
  await ctx.send(f'```{author.name} deu uma rolada e tirou: {dice_result}```')

  # Check dice result and take action if needed
  await check_dice_result(ctx, dice_result)


@bot.command()
async def check_status(ctx):

  global user_status_dict

  id = str(ctx.author.id)
  status = db['user_status'][id]['status']
  last_played = db['user_status'][id]['last_played']
  blocked_until = db['user_status'][id]['blocked_until']
  titulo = db['user_status'][id]['titulo']

  await ctx.send(f'id: {id}')
  await ctx.send(f'status: {status}')
  await ctx.send(f'last_played: {last_played}')
  await ctx.send(f'blocked_until: {blocked_until}')
  await ctx.send(f'titulo: {titulo}')


# @bot.event
# async def on_raw_reaction_add(payload):
#   message = await bot.get_channel(payload.channel_id
#                                   ).fetch_message(payload.message_id)
#   reaction = discord.utils.get(message.reactions, emoji="📩")
#   user = payload.member

keep_alive()


try:
    bot.run(TOKEN)
except:
    os.system("kill 1")

