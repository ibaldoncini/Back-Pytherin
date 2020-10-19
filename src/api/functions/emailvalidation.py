import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

class Validation:

  def __init__(self):
    self.__verification_code = self.__get_random_string(5)


  def __get_random_string(self,length):
    letters = string.ascii_uppercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


  def send_mail(self,to):
    from_u = 'pytherinfamaf@gmail.com'
    passw = 'Pytherin123'

    msg = MIMEMultipart()
    msg['Subject'] = "Secret Voldemort account verification"
    msg['From'] = from_u
    msg['To'] = to

    body = "Hi, your Secret Voldemort account verification code is " + \
        self.__verification_code

    msg.attach(MIMEText(body, 'plain'))

    text = msg.as_string()

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(from_u, passw)
    s.sendmail(from_u, to, text)
    s.close()
    #TODO, sacar esto de aca, es medio raro que send mail devuelva algo
    return self.__verification_code


  
