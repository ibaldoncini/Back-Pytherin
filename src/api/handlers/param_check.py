from pony.orm import db_session,select
from api.models.users.user import User
from api.models.base import DB_User


def check_username_not_in_database (u : User):
  with db_session: 
    username_list = select ((u.username) for u in DB_User)
    return u.username not in username_list


def check_email_not_in_database (u : User):
  with db_session:
    mail_list = select ((u.email) for u in DB_User)
    return u.email not in mail_list

