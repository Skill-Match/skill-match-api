import sendgrid
from skill_match.settings import SENDGRID_KEY, TWILIO_SID, TWILIO_TOKEN
from twilio.rest import TwilioRestClient


# Notifications using Sendgrid for Email and Twilio for Text Messages.

def send_email(email, subject, html):
    sender = 'SkillMatch <fredoflynn@gmail.com>'
    sg = sendgrid.SendGridClient(SENDGRID_KEY)

    message = sendgrid.Mail()
    message.add_to(email)
    message.set_subject(subject)
    message.set_html(html)
    message.set_from(sender)
    status, msg = sg.send(message)


def send_text(phone_number, body):
    account = TWILIO_SID
    token = TWILIO_TOKEN
    client = TwilioRestClient(account, token)
    message = client.messages.create(to=phone_number, from_="+17025059053",
                                     body=body)


def create_match_notify(match):

    user_email = match.creator.email
    park_name = match.park.name
    sport = match.sport
    date = match.date.strftime("%A %B, %d")
    time = match.time.strftime("%I:%M %p")

    body_message = "You have succesfully created a match. You want to " \
                   "play {} at {} on {} at {}. We'll let you know if " \
                   "someone joins your match!".format(sport, park_name,
                                                      date, time)

    sg = sendgrid.SendGridClient(SENDGRID_KEY)

    message = sendgrid.Mail()
    message.add_to(user_email)
    message.set_subject(
        'Hi from SkillMatch!'
    )
    message.set_html("<p> " + body_message + "</p>")
    message.set_text(body_message)
    message.set_from('SkillMatch <fredoflynn@gmail.com>')
    status, msg = sg.send(message)


def join_match_notify(match, joiner):
    creator = match.creator
    challenger = joiner
    park = match.park.name
    sport = match.sport
    date = match.date.strftime("%A %B, %d")
    time = match.time.strftime("%I:%M %p")

    body = "Notification: {} has joined your {} match at {} on {} at {}. " \
           "Please go to the website to confirm or decline this match."\
           .format(challenger.username, sport, park, date, time)

    subject = "Someone joined your match!"

    send_email(creator.email, subject, body)

    if creator.profile.wants_texts and creator.profile.phone_number:
        send_text(creator.profile.phone_number, body)


def leave_match_notify(match, joiner):
    creator = match.creator
    challenger = joiner
    park = match.park.name
    sport = match.sport
    date = match.date.strftime("%A %B, %d")
    time = match.time.strftime("%I:%M %p")

    body = "Notification: {} has left your {} match at {} on {} at {}. " \
           "The match is now Open again."\
           .format(challenger.username, sport, park, date, time)

    subject = "Someone Left your match!"

    send_email(creator.email, subject, body)

    if creator.profile.wants_texts and creator.profile.wants_texts:
        send_text(creator.profile.phone_number, body)


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

    if challenger.profile.phone_number and challenger.profile.wants_texts:
        send_text(challenger.profile.phone_number, body)


def twenty_four_hour_notify(match):
    for player in match.players.all():
        if player.profile.wants_texts and player.profile.phone_number:
            time = time = match.time.strftime("%I:%M %p")
            body = "Reminder: Your {} match tomorrow is at {} at {}. Have a " \
                   "good one!".format(match.sport, time, match.park.name)
            send_text(player.profile.phone_number, body)
