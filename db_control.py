from replit import db
import datetime as dt


def check_user_in_db(id, user):
  
  #transforming both keys in string
  id = str(id)
  user = str(user)

  #if user do not exist yet, create a key
  if id not in db['user_status'].keys():
    db['user_status'][str(id)] = {
      'name': user,
      'titulo': '',
      'status': '',
      'blocked_until': '01/01/2000',
      'last_played': '01/01/2000'
    }
  else:
    pass

def update_user_db(id, property, new_value):

  id = str(id)
  property = str(property)
  new_value = str(new_value)
  
  db['user_status'][str(id)][property] = new_value

def save_roll(user_id, user_name, roll):
  user_id = str(user_id)
  user_name = str(user_name)
  date = dt.date.today().strftime('%d/%m/%Y')

  id = len(db['all_rolls'].keys()) + 1
  dict_register = {
    'user_id': user_id,
    'user_name': user_name,
    'date': date
  }
  
  db['all_rolls'][id] = dict_register
  