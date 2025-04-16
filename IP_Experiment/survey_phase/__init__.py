from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(
        label='How old are you?', min=18, max=99
    )
    gender = models.StringField(
        choices=['Female', 'Male', 'Non‑binary', 'Prefer not to say'],
        label='What is your gender?',
        widget=widgets.RadioSelect,
    )
    email_consent = models.BooleanField(
        blank=True,
        label='May we contact you by e‑mail for follow‑up studies?',
    )


class SurveyQuestions(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'email_consent']


page_sequence = []
