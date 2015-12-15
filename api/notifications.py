import sendgrid
from skill_match.settings import SENDGRID_KEY, TWILIO_SID, TWILIO_TOKEN
from twilio.rest import TwilioRestClient


def send_email(email, subject, html):
    sender = 'SkillMatch <fredoflynn@gmail.com>'
    sg = sendgrid.SendGridClient(SENDGRID_KEY)

    message = sendgrid.Mail()
    message.add_to(email)
    message.set_subject(subject)
    message.set_html(html)
    message.set_from(sender)
    status, msg = sg.send(message)


def send_text(phone_number):
    account = TWILIO_SID
    token = TWILIO_TOKEN
    client = TwilioRestClient(account, token)
    message = client.messages.create(to="+5082693675", from_="+17025059053",
                                 body="Hello there!")


def join_match_notify(match):
    creator_email = match.creator.email
    challenger = match.players.exclude(id=match.creator.id)[0]
    park = match.park.name
    sport = match.sport
    date = match.date.strftime("%A %B, %d")
    time = match.time.strftime("%I:%M %p")

    body_to_creator = "{} has joined your {} match at {} on {} at {}. Please " \
                      "go to the website to confirm or decline this match."\
                      .format(challenger.username, sport, park, date, time)
    subject = "Hey from SkillMatch"

    send_email(creator_email, subject, body_to_creator)


def confirm_match_notify(match):
    challenger_email = match.players.exclude(id=match.creator.id)[0].email
    date = match.date.strftime("%A %B, %d")
    time = match.time.strftime("%I:%M %p")

    body = "Your match for {} at {} on {} at {} has been accepted. Have a" \
           "good time!".format(match.sport, match.park.name, date, time)
    subject = "Your match has been accepted!"

    send_email(challenger_email, subject, body)


def decline_match_notify(match, challenger):
    challenger_email = challenger.email
    date = match.date.strftime("%A %B, %d")
    time = match.time.strftime("%I:%M %p")

    body = "The match for {} at {} on {} at {} has been declined. We are very" \
           "sorry. Please try again on another game.".format(match.sport,
                                                             match.park.name,
                                                             date, time)
    subject = "Your match request has been declined."

    send_email(challenger_email, subject, body)