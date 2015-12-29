from matchup.models import Feedback


def calculate_skills(skill_object, sport):
    player = skill_object.player
    feedbacks = Feedback.objects.filter(match__sport=sport).\
        filter(player=player)
    skill_total = 0
    sportsmanship_total = 0
    count = 0
    for feedback in feedbacks:
        skill_total += feedback.skill
        sportsmanship_total += feedback.sportsmanship
        count += 1
    skill_object.skill = skill_total / count
    skill_object.sportsmanship = sportsmanship_total / count
    skill_object.num_feedbacks = count
    skill_object.save()


def new_calculate_skills(skill_object, sport):
    player = skill_object.player
    feedbacks = Feedback.objects.filter(match__sport=sport).\
        filter(player=player)
    skill_total = 0
    sportsmanship_total = 0
    total_weight = 0
    count = 0
    for feedback in feedbacks:
        reviewer_cred = feedback.reviewer.skill_set.filter(sport=sport)
        if reviewer_cred:
            reviewer_cred = reviewer_cred[0]
            xp = reviewer_cred.num_feedbacks
            sportsmanship = reviewer_cred.sportsmanship

            weight = 0
            if 0 <= xp <= 10:
                weight = 5
            elif 11 < xp < 20:
                weight = 6
            elif 21 < xp < 30:
                weight = 7
            elif 31 < xp < 40:
                weight = 8
            elif 41 < xp < 50:
                weight = 9
            else:
                weight = 10

            # sportsmakship weighted 3 times heavier than xp (xp gets 1-10)
            # example weight calculation: sportsmanship of 85
            # 85 * 3 --> 255.5 / 10 --> 25.5 , rounded down to 25
            weight += int((sportsmanship * 3) / 10)

            skill_total += (feedback.skill * weight)
            sportsmanship_total += (feedback.sportsmanship * weight)
            total_weight += weight
            count += 1

    skill_object.skill = skill_total / total_weight
    skill_object.sportsmanship = sportsmanship_total / total_weight
    skill_object.num_feedbacks = count
    skill_object.save()


