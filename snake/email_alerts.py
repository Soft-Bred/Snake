import smtplib
from email.mime.text import MIMEText
import requests
import netifaces

SMTPServer      = "smtp.mail.yahoo.com"
SMTPPort        = 587

# Personal Info
username        = "SnakeUpdates@yahoo.com"
password        = "qttggvsapzjtcodm"
sender          = "SnakeUpdates@yahoo.com"
reciever        = "SnakeUpdates@yahoo.com"
subject         = "New Snake Results"
leaderboardIP   = netifaces.ifaddresses('wlan0')[2][0]["addr"]

def getScores():
    scores = requests.get('http://127.0.0.1:5000/leaderboard')
    scores = scores.json()
    return scores

def sendEmail():
    print("Trying To Send Email")
    message = """This email is being sent to inform you of the latest top scores for your Snake game.

Top Scores:

"""
    for key, value in getScores()["result"].items():
        message += f"{key}. {value}\n"
    message += f"You can view the leaderboard at http://{leaderboardIP}:5500"
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = reciever
    mail = smtplib.SMTP(SMTPServer, SMTPPort)
    mail.starttls()
    mail.login(username, password)
    mail.sendmail(sender, reciever, msg.as_string())
    mail.quit()
    print("Email Sent")