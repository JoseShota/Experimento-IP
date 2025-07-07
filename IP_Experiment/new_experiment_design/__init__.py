from __future__ import annotations  # For postponed evaluation of annotations
from otree.api import *
import random, json, logging
from typing import List, Tuple

# Define the full survey questions as a module-level constant.
PRACTICE_QUESTION = "¿Qué color es mejor, el rojo o el azul?"
PRACTICE_OPTIONS = ("El rojo", "El azul")
PRACTICE_FIRST_OPTION = "El rojo"
PRACTICE_SECOND_OPTION = "El azul"

BELIEF_QUESTION = (
    'Otros participantes en esta sesión van a tener una "conversación" en el '
    'mismo tema, con la misma información (o falta de información) sobre '
    'cuántos pagaron el costo para dar o quitarle 20 pesos a los demás en el '
    'grupo, y en un grupo cuyos miembros fueron asignados de la misma manera '
    'que en tu grupo. Queremos que nos digas, de todos los participantes que '
    'estuvieron en una "conversación" bajo esas circunstancias, qué porcentaje '
    'crees que expresó una opinión a los demás en el grupo diferente a la '
    'opinión privada que nos reportaron?. Si tu respuesta está a una diferencia '
    'de 10 puntos porcentuales de la respuesta correcta, te pagaremos diez '
    'pesos extra. Esto es, te pagaremos diez pesos extra si adivinas X, y la '
    'respuesta correcta está en el rango entre X-10 y X+10.'
)

PRE_CONV_QUESTIONS = [
    "¿Qué lugar es mejor: La Condesa o Coyoacán?",
    "¿Crees que el gobierno debería tener el poder de prohibirte fumar "
    "incluso en espacios al aire libre como playas o parques públicos?"
]

# ------------------------------------------------------------------
# ► Constantes para la página de sanciones
# ------------------------------------------------------------------
PUNISH_CHOICES = [
    ('GIVE',  'Le daría los 20 pesos'),
    ('TAKE',  'Le quitaría los 20 pesos'),
]

INTRO_A = """
Supón que una persona expresó una opinión que es:
- <strong>diferente</strong> a la opinión privada de la persona misma que expresó la opinión
- <strong>diferente</strong> a tu opinión privada
"""

INTRO_B = INTRO_A.replace("diferente</strong> a tu opinión privada",
                           "igual</strong> a tu opinión privada")

INTRO_C = INTRO_A.replace("diferente</strong> a la opinión privada de la persona misma que expresó la opinión",
                           "igual</strong> a la opinión privada de la persona misma que expresó la opinión")

INTRO_D = INTRO_C.replace("diferente</strong> a tu opinión privada",
                           "igual</strong> a tu opinión privada")

YOUR_DECISION = "Tienes que decidir si darle o quitarle 20 pesos. ¿Qué harías?"

THEIR_DECISION_A = """
Ahora considera a diez personas en esta sesión diferentes a ti. Cada uno tiene que decidir si darle o quitarle 20 pesos a alguien que expresó una opinión:
- <strong>diferente</strong> a la opinión privada de la persona misma que expresó la opinión
- <strong>diferente</strong> a la opinión privada de quien va decidir si dar o quitar 20 pesos

¿Cuántos de los diez le darían 20 pesos? Nota que los demás le quitarían 20 pesos.  
"""

THEIR_DECISION_B = """
Ahora considera a diez personas en esta sesión diferentes a ti. Cada uno tiene que decidir si darle o quitarle 20 pesos a alguien que expresó una opinión:
- <strong>diferente</strong> a la opinión privada de la persona misma que expresó la opinión
- <strong>igual</strong> a la opinión privada de quien va decidir si dar o quitar 20 pesos

¿Cuántos de los diez le darían 20 pesos? Nota que los demás le quitarían 20 pesos.  
"""

THEIR_DECISION_C = """
Ahora considera a diez personas en esta sesión diferentes a ti. Cada uno tiene que decidir si darle o quitarle 20 pesos a alguien que expresó una opinión:
- <strong>igual</strong> a la opinión privada de la persona misma que expresó la opinión
- <strong>diferente</strong> a la opinión privada de quien va decidir si dar o quitar 20 pesos

¿Cuántos de los diez le darían 20 pesos? Nota que los demás le quitarían 20 pesos.  
"""

THEIR_DECISION_D = """
Ahora considera a diez personas en esta sesión diferentes a ti. Cada uno tiene que decidir si darle o quitarle 20 pesos a alguien que expresó una opinión:
- <strong>igual</strong> a la opinión privada de la persona misma que expresó la opinión
- <strong>igual</strong> a la opinión privada de quien va decidir si dar o quitar 20 pesos

¿Cuántos de los diez le darían 20 pesos? Nota que los demás le quitarían 20 pesos.  
"""

PUNISH_TEXTS = [
    # 1-4: decisiones propias ↓
    "Supón que una persona expresó una opinión que es:\n"
    "- <strong>diferente</strong> a la opinión privada de quien expresó la opinión\n"
    "- <strong>diferente</strong> a tu opinión privada\n"
    "- el tema es uno para el que pagaste el costo para dar o quitar 20 pesos a los demás miembros de tu grupo\n"
    "¿Le darías o quitarías los 20 pesos?",

    "Supón que una persona expresó una opinión que es:\n"
    "- <strong>diferente</strong> a la opinión privada de quien expresó la opinión\n"
    "- <strong>igual</strong> a tu opinión privada\n"
    "- el tema es uno para el que pagaste el costo para dar o quitar 20 pesos a a los demás miembros de tu grupo\n"
    "¿Le darías o quitarías los 20 pesos?",

    "Supón que una persona expresó una opinión que es:\n"
    "- <strong>igual</strong> a la opinión privada de quien expresó la opinión\n"
    "- <strong>diferente</strong> a tu opinión privada\n"
    "- el tema es uno para el que pagaste el costo para dar o quitar 20 pesos a a los demás miembros de tu grupo\n"
    "¿Le darías o quitarías los 20 pesos?",

    "Supón que una persona expresó una opinión que es:\n"
    "- <strong>igual</strong> a la opinión privada de quien expresó la opinión\n"
    "- <strong>igual</strong> a tu opinión privada\n"
    "- el tema es uno para el que pagaste el costo para dar o quitar 20 pesos a a los demás miembros de tu grupo\n"
    "¿Le darías o quitarías los 20 pesos?",

    # 5-8: predicciones sobre 10 terceros ↓
    "Supón que hay diez personas en esta sesión (diferentes a ti) que para un tema pagaron el costo para dar o quitar 20 pesos a los integrantes de su grupo dependiendo de la opinión que le expresen. Supón que un integrante de su grupo expresó una opinión que es: \n"
    "- <strong>diferente</strong> a la opinión privada de quien expresó la opinión\n"
    "- <strong>diferente</strong> a la opinión privada de quien va decidir si dar o quitar 20 pesos\n"
    "¿Cuántas de las diez personas le daría los 20 pesos? Nota que como los diez pagaron el costo por dar o quitar 20 pesos, los que no den 20 pesos quitarían 20 pesos.",

    "Supón que hay diez personas en esta sesión (diferentes a ti) que para un tema pagaron el costo para dar o quitar 20 pesos a los integrantes de su grupo dependiendo de la opinión que le expresen. Supón que un integrante de su grupo expresó una opinión que es: \n"
    "- <strong>diferente</strong> a la opinión privada de quien expresó la opinión\n"
    "- <strong>igual</strong> a la opinión privada de quien va decidir si dar o quitar 20 pesos\n"
    "¿Cuántas de las diez personas le daría los 20 pesos? Nota que como los diez pagaron el costo por dar o quitar 20 pesos, los que no den 20 pesos quitarían 20 pesos.",


    "Supón que hay diez personas en esta sesión (diferentes a ti) que para un tema pagaron el costo para dar o quitar 20 pesos a los integrantes de su grupo dependiendo de la opinión que le expresen. Supón que un integrante de su grupo expresó una opinión que es: \n"
    "- <strong>igual</strong> a la opinión privada de quien expresó la opinión\n"
    "- <strong>diferente</strong> a la opinión privada de quien va decidir si dar o quitar 20 pesos\n"
    "¿Cuántas de las diez personas le daría los 20 pesos? Nota que como los diez pagaron el costo por dar o quitar 20 pesos, los que no den 20 pesos quitarían 20 pesos.",


    "Supón que hay diez personas en esta sesión (diferentes a ti) que para un tema pagaron el costo para dar o quitar 20 pesos a los integrantes de su grupo dependiendo de la opinión que le expresen. Supón que un integrante de su grupo expresó una opinión que es: \n"
    "- <strong>igual</strong> a la opinión privada de quien expresó la opinión\n"
    "- <strong>igual</strong> a la opinión privada de quien va decidir si dar o quitar 20 pesos\n"
    "¿Cuántas de las diez personas le daría los 20 pesos? Nota que como los diez pagaron el costo por dar o quitar 20 pesos, los que no den 20 pesos quitarían 20 pesos.",

]


SURVEY_QUESTIONS = [
    "¿Estás de acuerdo con la frase 'el dinero compra la felicidad'?",
    "¿Crees que el ser humano es inherentemente bueno o malo?",
    "Llega contigo tu mejor amiga/o que acaba de hacerse un nuevo corte de pelo. Emocionada/o te pregunta si te gusta, pero a ti te parece que fue una terrible decisión. ¿Crees que mentir en esta situación es justificable, sabiendo que la verdad le haría sentir muy mal?",
    "¿Qué equipo de futbol es mejor: el América o las Chivas?",
    "¿Estás de acuerdo con la frase 'no hay paz sin la violencia'?",
    "¿Crees que los videojuegos violentos fomentan actitudes violentas en la vida real?",
    "¿Crees que uno de los criterios principales para contratar a alguien en México es el color de piel?",
    "¿Quién tiene mejor música, Luis Miguel o Juan Gabriel?",
    "¿Estás de acuerdo en que hay que separar el arte de Michael Jackson del artista?",
    "Estás en una guerra y debes decidir si salvar la vida de tu compañero o la de un niño inocente que está en peligro. ¿A quién salvarías?",
    "¿Estás de acuerdo con la pena de muerte?",
    "Una persona rica y grosera tira un billete de cien pesos sin darse cuenta. ¿Deberías devolvérselo?",
    "¿Qué es lo más higiénico, bañarse en la mañana o en la noche?",
    "¿Qué saga de películas es mejor: Harry Potter o El Señor de los Anillos?",
    "¿Qué tan rápido México debería transicionar a las energías renovables, tomando en cuenta que entre más rápido transicionar peor va a ser el crecimiento económico dado que el petróleo es un tercio de la economía del país?"
]

FIRST_OPTIONS = [
    "De acuerdo",
    "Bueno",
    "Sí debería",
    "El América",
    "De acuerdo",
    "Sí",
    "Sí",
    "Luis Miguel",
    "De acuerdo",
    "A mi compañero",
    "De acuerdo",
    "Sí, debería devolvérselo",
    "Bañarse en la mañana",
    "Harry Potter",
    "En 10 años"
]

SECOND_OPTIONS = [
    "En desacuerdo",
    "Malo",
    "No debería",
    "Las Chivas",
    "En desacuerdo",
    "No",
    "No",
    "Juan Gabriel",
    "En desacuerdo",
    "Al niño",
    "En desacuerdo",
    "No, no debería devolvérselo",
    "Bañarse en la noche",
    "El Señor de los Anillos",
    "En 25 años"
]




# -----------------------------------------------------------------------------
# Logging configuration for debugging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# --------------------------------------------------------------------
# Utilidad: sortear el tratamiento según las probabilidades pedidas
# --------------------------------------------------------------------
def draw_treatment() -> Tuple[float, str]:
    u = random.random()
    if u < 0.5:
        return 0.5, '0.5_H'
    elif u < 0.75:
        return 0.7, '0.7_H'
    else:
        return 0.3, '0.7_L'

MIN_PER_POOL = 3           # umbral configurable

def enough_players(H_pool, L_pool, min_per_pool=MIN_PER_POOL):
    """¿Hay al menos `min_per_pool` en cada pool?"""
    return len(H_pool) >= min_per_pool and len(L_pool) >= min_per_pool


# -----------------------------------------------------------------------------
# Constants and Helper Functions
# -----------------------------------------------------------------------------
class C(BaseConstants):
    NAME_IN_URL = 'new_experiment_design'
    PLAYERS_PER_GROUP = 3
    NUM_BINARY_QUESTIONS = 15 
    NUM_ROUNDS = 27

    CORRECT_ANSWERS = dict(
        comp_q1='c',
        comp_q2='d',
        comp_q3='a',        # tu BooleanField usa True/False
        comp_q4='c',
        comp_q5='d',
        comp_q6='c',
        comp_q7='a',
    )

    QUESTION_TEXT = dict(
        comp_q1=('1. ¿Cuál de las siguientes opciones describe correctamente las acciones disponibles para un participante una vez que se formó su grupo en el experimento?'),
        comp_q2=('2. ¿Qué sucede si un participante decide pagar el costo (5 pesos) para darle o quitarle 20 pesos a los demás miembros de su grupo, y el participante decide quitarle 20 pesos a uno de ellos?'),
        comp_q3=('3. Calcula la cantidad de dinero con la que termina el siguiente participante: <br>'
            '  • Paga el costo para decidir dar o quitar 20 pesos a cada miembro del grupo.<br>'
            '  • Expresa su opinión privada ante el grupo y gana 10 pesos.<br>'
            '  • Los otros miembros de su grupo deciden quitarle 20 pesos.<br>'
            '  • Adivina correctamente el porcentaje de personas que expresaron una opinión diferente a su opinión privada en esas "conversaciónes", y recibe 10 pesos extra.<br>'
            '  • Advinó incorrectamente si la opinión que le expresaron los demás miembros es igual a su opinión privada.<br>'
                 ),
        comp_q4=('4. Caclula la cantidad de dinero con la que termina el siguiente participante: <br>'
            '  • Paga el costo para decidir dar o quitar 20 pesos a cada miembro del grupo.<br>'
            '  • Expresa la opinión alterna a su opinión privada.<br>'
            '  • Los otros miembros no pagan el costo para decidir dar o quitar 20 pesos.<br>'
            '  • Adivina correctamente el porcentaje de personas que expresaron una opinión diferente a su opinión privada en esas "conversaciónes", y recibe 10 pesos extra.<br>'
            '  • Advina correctamente si la opinión que le expresaron los demás miembros es igual a su opinión privada, y recibe 10 pesos adicionales.<br>'),
        comp_q5=('¿Cómo se crean los grupos de tres personas en el experimento?'),
        comp_q6=('6. ¿Qué es lo que cada participantes debe adivinar sobre los miembros de su grupo en este experimento?'),
        comp_q7=('7. (Verdadero o Falso) Los participantes no sabrán quiénes son los demás miembros de cada grupo en los que estén.'),
    )

    QUESTION_OPTIONS = dict(
        comp_q1=[
            ('a', 'a) Escoger qué opinión expresarle a los demás en el grupo. Decidir si dar o quitar dinero a cada uno de los miembros. Adivinar si la opinión que los demás miembros te expresaron es la misma que expresaron en privado. Adivina el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.'),
            ('b', 'b) Escoger qué opinión expresarle a los demás en el grupo. Adivinar si la opinión que los demás mimebros te expresaron es la misma que expresaron en privado. Adivina el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.'),
            ('c', 'c) Escoger qué opinión expresarle a los demás en el grupo. Entre quienes pagaron cinco pesos por hacerlo decidir si dar o quitar dinero a cada uno de los demás miembros del grupo. Adivinar si la opinión que los demás miembros te expresaron es la misma que expresaron en privado. Adivina el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.'),
            ('d', 'd) Escoger qué opinión expresarle a los demás en el grupo. Entre quienes pagaron cinco pesos por hacerlo decidir si dar o quitar dinero a cada uno de los demás miembros del grupo. Adivina el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.'),
        ],
        comp_q2=[
            ('a', 'a) El participante gana 20 pesos'),
            ('b', 'b) El participante recupera los 5 pesos pagados y el otro miembro gana 20 pesos adicionales'),
            ('c', 'c) Sólo el que paga pierde dinero; el otro miembro no gana ni pierde nada'),
            ('d', 'd) El participante pierde 5 pesos y el otro miembro pierde 20 pesos'),
        ],
        comp_q3=[
            ('a', 'a) Termina con 25 pesos'),
            ('b', 'b) Termina con -25 pesos. Es decir, acaba sin dinero.'),
            ('c', 'c) Termina con 30 pesos'),
            ('d', 'd) Termina con 45 pesos'),
        ],
        comp_q4=[
            ('a', 'a) Termina con 40 pesos'),
            ('b', 'b) Termina con 15 pesos'),
            ('c', 'c) Termina con 65 pesos'),
            ('d', 'd) Termina con 50 pesos'),
        ],
        comp_q5=[
            ('a', 'a) Según sus características personales (por ejemplo, edad o género)'),
            ('b', 'b) Los participantes eligen libremente a los mimebros de su grupo'),
            ('c', 'c) De forma totalmente aleatoria'),
            ('d', 'd) Basándose en las opiniones privadas de los participantes sobre cada uno de los temas de la Parte 3 del experimento'),
        ],
        comp_q6=[
            ('a', 'a) Si la opinión que los demás miembros le expresaron es la misma que expresaron en privado'),
            ('b', 'b) La decisión que tomará cada uno de los mimebros sobre dar o quitar 20 pesos a los demás y si la opinión que los demás miembros le expresaron es la misma que expresaron en privado'),
            ('c', 'c) Si la opinión que los demás miembros te expresaron es la misma que expresaron en privado y el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.'),
            ('d', 'd) Si la opinión que los demás miembros le expresaron es diferente a su opinión privada'),
        ],
        comp_q7=[
            ('a', 'a) Verdadero: los participantes no sabrán quiénes son los demás miembros de cada grupo en los que estén.'),
            ('b', 'b) Falso: los participantes sí sabrán quiénes son los demás miembros de cada grupo en los que estén.'),
        ],
    )


    CORRECT_EXPLANATIONS = dict(
        comp_q1='Las acciones disponibles para un participante una vez que se formó su grupo son: (1) escoger qué opinión expresarle a los demás en el grupo, (2) para quienes pagaron el costo por hacerlo decidir si dar o quitar dinero a cada uno de los miembros, (3) adivinar si la opinión que los demás miembros te expresaron es la misma que expresaron en privado, y (4) adivinar el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.',
        comp_q2='Los participantes que pagan el costo por decidir dar o quitar 20 pesos a los demás miembros de su grupo se les sustrae 5 pesos de su dinero disponible. Si los participantes deciden quitarle 20 pesos a uno de los miembros, esa decisión se aplicará al miembro; pierde 20 pesos.',
        comp_q3='El participante recibe 50 pesos por participar, pierde 5, gana 10, pierde 40 y gana 10. Entonces, termina con 50 - 5 + 10 - 40 + 10 = 25 pesos.',
        comp_q4='El participante recibe 50 pesos por participar, pierde 5, gana 10 y gana 10. Entonces, termina con 50 - 5 + 10 + 10 = 65 pesos.',
        comp_q5='Los grpos de tres personas se forman a partir de las opiniones privadas de los participantes sobre cada uno de los temas de la Parte 3 del experimento.',
        comp_q6='Los participantes deben adivinar si la opinión que los demás miembros te expresaron es la misma que expresaron en privado y el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.',
        comp_q7='Verdadero: los participantes no sabrán quiénes son los demás miembros de cada grupo en los que estén.',
    )  

def load_partner_ids(player: Player) -> list[int]:
    """
    Devuelve la lista de id_in_subsession de los compañeros,
    usando field_maybe_none para evitar TypeError si es None.
    """
    raw = player.field_maybe_none('partner_ids') or '[]'
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def get_partners(player: Player) -> List[Player]:
    ids = load_partner_ids(player)
    return [p for p in player.subsession.get_players()
            if p.id_in_subsession in ids]



# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class Subsession(BaseSubsession):
    def creating_session(self):
        # Si no existe, créalo y GUAŔDALO inmediatamente
        if 'HL_map' not in self.session.vars:
            hl_map = [random.choice([True, False])
                      for _ in range(C.NUM_BINARY_QUESTIONS)]
            self.session.vars['HL_map'] = hl_map
            # use warning en lugar de debug para que siempre se vea en consola
            logger.warning(f"HL_map creado en creating_session: {hl_map}")
        if 'HL_preconv_map' not in self.session.vars:
            # Un booleano por cada pregunta de pre-conv
            self.session.vars['HL_preconv_map'] = [
                random.choice([True, False]) for _ in range(len(PRE_CONV_QUESTIONS))
            ]
            logger.warning(f"HL_preconv_map creado: {self.session.vars['HL_preconv_map']}")


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Consent field: participants must affirm their informed consent.
    consent = models.BooleanField(
        label="He leído y doy mi consentimiento para participar en el estudio.",
        widget=widgets.CheckboxInput
    )
    
    # New fields for the Practice Round (pre-practice survey)
    practice_binary_choice = models.StringField(
        choices=[('H', "El rojo"), ('L', "El azul")],
        blank=False,
        doc="Tema de Conversación: ¿Qué color es mejor, el rojo o el azul?"
    )
    practice_pay_to_judge = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False,
        doc="Respuesta de práctica sobre disposición a incurrir en el costo"
    )

    # Personal information fields:
    age = models.IntegerField(label="Edad", min=18)
    gender = models.StringField(
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        label="Sexo"
    )
    racial_identification = models.StringField(
        choices=[
            ('Mestizo', 'Mestiza/o'),
            ('Indigena', 'Indígena'),
            ('Caucasico', 'Caucásico'),
            ('Afro', 'Afrodescendiente'),
            ('Asiatico', 'Asiática/o'),
            ('Arabe', 'Árabe'),
            ('Otros', 'Otros:')
        ],
        label="¿Cómo te identificas racialmente?"
    )
    previous_experiment = models.IntegerField(
        label="¿En cuántos experimentos has participado previamente?",
        min=0
    )
    

    # Binary survey responses for 10 questions with custom labels:
    binary_choice_1 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False
    )
    binary_choice_2 = models.StringField(
        choices=[('H', "Bueno"), ('L', "Malo")],
        blank=False
    )

    binary_choice_3 = models.StringField(
        choices=[('H', "Sí debería"), ('L', "No debería")],
        blank=False
    )
    binary_choice_4 = models.StringField(
        choices=[('H', "El América"), ('L', "Las Chivas")],
        blank=False
    )
    binary_choice_5 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False
    )
    binary_choice_6 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False
    )
    binary_choice_7 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False
    )
    binary_choice_8 = models.StringField(
        choices=[('H', "Luis Miguel"), ('L', "Juan Gabriel")],
        blank=False
    )
    binary_choice_9 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False
    )
    binary_choice_10 = models.StringField(
        choices=[('H', "A mi compañero"), ('L', "Al niño")],
        blank=False
    )
    binary_choice_11 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False
    )
    binary_choice_12 = models.StringField(
        choices=[('H', "Sí, debería devolvérselo"), ('L', "No, no debería devolvérselo")],
        blank=False
    )
    binary_choice_13 = models.StringField(
        choices=[('H', "Bañarse en la mañana"), ('L', "Bañarse en la noche")],
        blank=False
    )
    binary_choice_14 = models.StringField(
        choices=[('H', "Harry Potter"), ('L', "El Señor de los Anillos")],
        blank=False
    )
    binary_choice_15 = models.StringField(
        choices=[('H', "En 10 años"), ('L', "En 25 años")],
        blank=False
    )
    pre_binary_choice_1 = models.StringField(
        choices=[('H','La Condesa'),('L','Coyoacán')],
        label=PRE_CONV_QUESTIONS[0],
        blank=False,
    )
    pre_binary_choice_2 = models.StringField(
        choices=[('H','Sí'),('L','No')],
        label=PRE_CONV_QUESTIONS[1],
        blank=False,
    )

    # Updated willingness-to-judge fields with custom display choices:
    pay_to_judge_1 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_2 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_3 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_4 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_5 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_6 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_7 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_8 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_9 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_10 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_11 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_12 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_13 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_14 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_to_judge_15 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False
    )
    pay_preconv_1 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False,
    )
    pay_preconv_2 = models.BooleanField(
        choices=[[True, "Sí"], [False, "No"]],
        blank=False,
    )
    # ── PRÁCTICA ───────────────────────────────────────────────────────
    practice_punish_1 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    practice_punish_2 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    practice_punish_3 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    practice_punish_4 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    practice_punish_5 = models.IntegerField(min=0, max=10, blank=False)
    practice_punish_6 = models.IntegerField(min=0, max=10, blank=False)
    practice_punish_7 = models.IntegerField(min=0, max=10, blank=False)
    practice_punish_8 = models.IntegerField(min=0, max=10, blank=False)

    # ── PRE-CONVERSACIÓN ──────────────────────────────────────────────
    preconv_punish_1 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    preconv_punish_2 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    preconv_punish_3 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    preconv_punish_4 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    preconv_punish_5 = models.IntegerField(min=0, max=10, blank=False)
    preconv_punish_6 = models.IntegerField(min=0, max=10, blank=False)
    preconv_punish_7 = models.IntegerField(min=0, max=10, blank=False)
    preconv_punish_8 = models.IntegerField(min=0, max=10, blank=False)

    # ── CONVERSACIÓN (rondas 13-27) ───────────────────────────────────
    conv_punish_1 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    conv_punish_2 = models.StringField(choices=PUNISH_CHOICES, blank=False) 
    conv_punish_3 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    conv_punish_4 = models.StringField(choices=PUNISH_CHOICES, blank=False)
    conv_punish_5 = models.IntegerField(min=0, max=10, blank=False)
    conv_punish_6 = models.IntegerField(min=0, max=10, blank=False)
    conv_punish_7 = models.IntegerField(min=0, max=10, blank=False)
    conv_punish_8 = models.IntegerField(min=0, max=10, blank=False)

            # ─── Cuestionario de comprensión ────────────────────────────────────
    comp_q1 = models.StringField(
        label=(
            '1. ¿Cuál de las siguientes opciones describe correctamente las acciones disponibles para un participante una vez que se formó su grupo en el experimento?'
        ),
        choices=[
            ('a', 'a) Escoger qué opinión expresarle a los demás en el grupo. Decidir si dar o quitar dinero a cada uno de los miembros. Adivinar si la opinión que los demás miembros te expresaron es la misma que expresaron en privado. Adivina el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.'),
            ('b', 'b) Escoger qué opinión expresarle a los demás en el grupo. Adivinar si la opinión que los demás mimebros te expresaron es la misma que expresaron en privado. Adivina el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.'),
            ('c', 'c) Escoger qué opinión expresarle a los demás en el grupo. Entre quienes pagaron cinco pesos por hacerlo decidir si dar o quitar dinero a cada uno de los demás miembros del grupo. Adivinar si la opinión que los demás miembros te expresaron es la misma que expresaron en privado. Adivina el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.'),
            ('d', 'd) Escoger qué opinión expresarle a los demás en el grupo. Entre quienes pagaron cinco pesos por hacerlo decidir si dar o quitar dinero a cada uno de los demás miembros del grupo. Adivina el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.')
        ],
        blank=False,
    )

    comp_q2 = models.StringField(
        label=(
            '2. ¿Qué sucede si un participante decide pagar el costo (5 pesos) para darle o quitarle 20 pesos a los demás miembros de su grupo, y el participante decide quitarle 20 pesos a uno de ellos?'
        ),
        choices=[
            ('a', 'a) El participante gana 20 pesos'),
            ('b', 'b) El participante recupera los 5 pesos pagados y el otro miembro gana 20 pesos adicionales'),
            ('c', 'c) Sólo el que paga pierde dinero; el otro miembro no gana ni pierde nada'),
            ('d', 'd) El participante pierde 5 pesos y el otro miembro pierde 20 pesos')
        ],
        blank=False,
    )

    comp_q3 = models.StringField(
        label=(
            '3. Calcula la cantidad de dinero con la que termina el siguiente participante: <br>'
            '  • Paga el costo para decidir dar o quitar 20 pesos a cada miembro del grupo.<br>'
            '  • Expresa su opinión privada ante el grupo y gana 10 pesos.<br>'
            '  • Los otros miembros de su grupo deciden quitarle 20 pesos.<br>'
            '  • Adivina correctamente el porcentaje de personas que expresaron una opinión diferente a su opinión privada en esas "conversaciónes", y recibe 10 pesos extra.<br>'
            '  • Advinó incorrectamente si la opinión que le expresaron los demás miembros es igual a su opinión privada.<br>'
        ),
        choices=[
            ('a', 'a) Termina con 25 pesos'),
            ('b', 'b) Termina con -25 pesos. Es decir, acaba sin dinero.'),
            ('c', 'c) Termina con 30 pesos'),
            ('d', 'd) Termina con 45 pesos')
        ], 
    )

    comp_q4 = models.StringField(
        label=(
            '4. Caclula la cantidad de dinero con la que termina el siguiente participante: <br>'
            '  • Paga el costo para decidir dar o quitar 20 pesos a cada miembro del grupo.<br>'
            '  • Expresa la opinión alterna a su opinión privada.<br>'
            '  • Los otros miembros no pagan el costo para decidir dar o quitar 20 pesos.<br>'
            '  • Adivina correctamente el porcentaje de personas que expresaron una opinión diferente a su opinión privada en esas "conversaciónes", y recibe 10 pesos extra.<br>'
            '  • Advina correctamente si la opinión que le expresaron los demás miembros es igual a su opinión privada, y recibe 10 pesos adicionales.<br>'
        ),
        choices=[
            ('a', 'a) Termina con 40 pesos'),
            ('b', 'b) Termina con 15 pesos'),
            ('c', 'c) Termina con 65 pesos'),
            ('d', 'd) Termina con 50 pesos'),
        ],
        blank=False,
    )

    comp_q5 = models.StringField(
        label=(
            '¿Cómo se crean los grupos de tres personas en el experimento?'
        ),
        choices=[
            ('a', 'a) Según sus características personales (por ejemplo, edad o género)'),
            ('b', 'b) Los participantes eligen libremente a los mimebros de su grupo'),
            ('c', 'c) De forma totalmente aleatoria'),
            ('d', 'd) Basándose en las opiniones privadas de los participantes sobre cada uno de los temas de la Parte 3 del experimento'),
        ],
        blank=False,
    )

    comp_q6 = models.StringField(
        label=(
            '6. ¿Qué es lo que cada participantes debe adivinar sobre los miembros de su grupo en este experimento?'
        ),
        choices=[
            ('a', 'a) Si la opinión que los demás miembros le expresaron es la misma que expresaron en privado'),
            ('b', 'b) La decisión que tomará cada uno de los mimebros sobre dar o quitar 20 pesos a los demás y si la opinión que los demás miembros le expresaron es la misma que expresaron en privado'),
            ('c', 'c) Si la opinión que los demás miembros te expresaron es la misma que expresaron en privado y el porcentaje de gente que le expresaron a su grupo una opinión que no es su opinón privada.'),
            ('d', 'd) Si la opinión que los demás miembros le expresaron es diferente a su opinión privada')
        ],
        blank=False,
    )

    comp_q7 = models.StringField(
        label=(
            '7. (Verdadero o Falso) Los participantes no sabrán quiénes son los demás miembros de cada grupo en los que estén.'
        ),
        choices=[
            ('a', 'a) Verdadero: los participantes no sabrán quiénes son los demás miembros de cada grupo en los que estén.'),
            ('b', 'b) Falso: los participantes sí sabrán quiénes son los demás miembros de cada grupo en los que estén.'),
        ],
        blank=False,
    )


    treatment = models.LongStringField(blank=False)
    second_choice = models.StringField(choices=['H', 'L'], blank=False)
    juicio_1 = models.StringField(
        choices=[
            ('GIVE',  'Darle 20 pesos al miembro 1'),
            ('TAKE',  'Quitarle 20 pesos al miembro 1')
        ],
        label='¿Qué decides, darle o quitarle 20 pesos al <strong>miembro 1</strong>?',
        blank=False,
    )
    juicio_2 = models.StringField(
        choices=[
            ('GIVE',  'Darle 20 pesos al miembro 2'),
            ('TAKE',  'Quitarle 20 pesos al miembro 2')
        ],
        label='¿Qué decides, darle o quitarle 20 pesos al <strong>miembro 2</strong>?',
        blank=False,
    )
    mentira_1 = models.StringField(choices=['Sí','No'], label='¿Consideras que la opinión que el miembro 1 expresó ante el grupo es la misma que nos expresó en privado?')
    mentira_2 = models.StringField(choices=['Sí','No'], label='¿Consideras que la opinión que el miembro 2 expresó ante el grupo es la misma que nos expresó en privado?')
    partner_ids = models.LongStringField(
        blank=True,
        doc="JSON list of the other two id_in_subsession in my group"
    )
    
    # New field: Tag to capture the binary question used for grouping in each round (Stage 2)
    current_question_tag = models.StringField(blank=True)

    # ---------------------------------------------------------------
    #  ❖ NUEVOS CAMPOS para la página de creencias (uno por sección)
    # ---------------------------------------------------------------
    belief_practice_pct  = models.IntegerField(
        label=BELIEF_QUESTION, min=0, max=100, blank=False
    )
    belief_preconv_pct   = models.IntegerField(
        label=BELIEF_QUESTION, min=0, max=100, blank=False
    )
    belief_conv_pct      = models.IntegerField(
        label=BELIEF_QUESTION, min=0, max=100, blank=False
    )

# -------------------------------------------------------------
# 1.  Emparejamiento en la RONDA DE PRÁCTICA
# -------------------------------------------------------------
def practice_pair_players(subsession: Subsession) -> None:
    players = subsession.get_players()
    H_pool  = [p for p in players if p.participant.vars.get('practice_binary_choice') == 'H']
    L_pool  = [p for p in players if p.participant.vars.get('practice_binary_choice') == 'L']
    groups: list[list[Player]] = []
    GROUP_SIZE = 3

    logger.debug(
        f"[practice] INICIO grouping (round {subsession.round_number}): "
        f"H={len(H_pool)}, L={len(L_pool)} (mín. {MIN_PER_POOL} cada uno)"
    )

    while enough_players(H_pool, L_pool):

        # 1) Sorteo del tratamiento
        prob_H, tlabel = draw_treatment()
        inform         = random.choice([True, False])
        logger.debug(f"  → Nuevo treatment={tlabel}, prob_H={prob_H:.2f}")

        # 2) Seleccionamos directamente los 3 miembros
        trio: list[Player] = []
        for _ in range(GROUP_SIZE):
            pick_H = (random.random() < prob_H and H_pool) or not L_pool
            pool   = H_pool if pick_H else L_pool
            trio.append(pool.pop())

        # 3) Guardamos treatment y partner_ids
        treatment = {
            'prob_H': prob_H,
            'label' : tlabel,
            'inform': inform,
            'practice': True
        }
        for p in trio:
            p.treatment   = json.dumps(treatment)
            p.partner_ids = json.dumps(
                [q.id_in_subsession for q in trio if q != p]
            )
        logger.info(f"    TRÍO formado: {[p.id_in_subsession for p in trio]} con {treatment}")
        groups.append(trio)

    # ---------- remanentes = grupos Control ----------
    rem = H_pool + L_pool
    random.shuffle(rem)
    while len(rem) >= GROUP_SIZE:
        trio = [rem.pop() for _ in range(GROUP_SIZE)]
        treatment = {'label': 'Control', 'inform': random.choice([True, False]), 'practice': True}
        for p in trio:
            p.treatment   = json.dumps(treatment)
            p.partner_ids = json.dumps([q.id_in_subsession for q in trio if q != p])
        groups.append(trio)
    logger.debug(f"  Total de grupos (practice): {len(groups)}")
    subsession.set_group_matrix(groups)


# --- 1) Nueva función de emparejamiento para las rondas 4–11 ---
# --- 1) Nueva función de emparejamiento para las rondas 4–11 ---
def pair_preconv_players(subsession: Subsession) -> None:
    """
    Emparejamiento idéntico a pair_players, usando pre_binary_choices.
    Aplica solo para rondas 4–11 (8 rondas en total):
        - Rondas 4–7 (q_index=0): primera pre_binary_choice
        - Rondas 8–11 (q_index=1): segunda pre_binary_choice
    """
    rn = subsession.round_number
    # Solo para las rondas 4–11
    if rn < 4 or rn > 11:
        return

    # Calcular sección y q_index: secciones de 4 rondas cada una
    # 4-7 → section=0; 8-11 → section=1
    section = (rn - 4) // 4
    assert section in [0, 1], f"Expected section 0 or 1 for rn {rn}, got {section}"
    q_index = section

    # subronda dentro del bloque de 4: 0,1,2,3
    subround = (rn - 4) % 4

    players = subsession.get_players()
    H_pool = [p for p in players if p.participant.vars['pre_binary_choices'][q_index] == 'H']
    L_pool = [p for p in players if p.participant.vars['pre_binary_choices'][q_index] == 'L']
    groups: list[list[Player]] = []
    GROUP_SIZE = 3

    logger.debug(
        f"[preconv round {rn}] H={len(H_pool)}, L={len(L_pool)} "
        f"(mín. {MIN_PER_POOL} cada uno), subround={subround}"
    )
    # Emparejamiento con reintentos idéntico a pair_players
    while enough_players(H_pool, L_pool):
        prob_H, tlabel = draw_treatment()
        # Inform determinístico: las dos primeras subrondas sin inform, las dos últimas siempre con inform
        use_inform = (subround >= 2)
        logger.debug(
            f"  → Nuevo treatment={tlabel}, prob_H={prob_H:.2f}, "
            f"use_inform={use_inform}"
        )
        # Seleccionamos directamente los 3 integrantes
        trio = []
        for _ in range(GROUP_SIZE):
            pick_H = (random.random() < prob_H and H_pool) or not L_pool
            pool   = H_pool if pick_H else L_pool
            trio.append(pool.pop())

        # Armamos dict treatment
        treatment = {'prob_H': prob_H, 'label': tlabel}
        if use_inform:
            treatment['inform'] = True

        # Guardamos en cada jugador
        for p in trio:
            p.treatment   = json.dumps(treatment)
            p.partner_ids = json.dumps(
                [q.id_in_subsession for q in trio if q != p]
            )
        logger.info(
            f"    TRÍO preconv (q_index={q_index}): "
            f"{[p.id_in_subsession for p in trio]} con {treatment}"
        )
        groups.append(trio)

    # Remanentes: singleton, igual a pair_players
    rem = H_pool + L_pool
    random.shuffle(rem)
    for p in rem:
        p.treatment = ''
        p.partner_ids = '[]'
        groups.append([p])

    logger.debug(f"  Grupos formados (preconv): {len(groups)} (incluye {len(rem)} singletons)")
    subsession.set_group_matrix(groups)




# -------------------------------------------------------------
# 2.  Emparejamiento en RONDAS 4-13
# -------------------------------------------------------------
def pair_players(subsession: Subsession) -> None:
    rn = subsession.round_number

    # 2.1 Antes de la encuesta de pre‐conversación
    if rn <= 3:
        return

    # 2.2 Rondas 4–11: sección pre‐conversación
    if rn <= 11:
        pair_preconv_players(subsession)
        return

    # 2.3 Rondas ≥12: tu lógica original, solo hay que desplazar el índice
    order = subsession.session.vars['question_order']
    # ajustamos el offset: ahora la primera Q de 'order' corresponde a ronda 12
    qi = order[rn - 12]

    players = subsession.get_players()
    H_pool  = [p for p in players if p.participant.vars['binary_choices'][qi] == 'H']
    L_pool  = [p for p in players if p.participant.vars['binary_choices'][qi] == 'L']
    groups: list[list[Player]] = []
    GROUP_SIZE = 3

    logger.debug(
        f"[conv round {rn}] H={len(H_pool)}, L={len(L_pool)} "
        f"(mín. {MIN_PER_POOL} cada uno)"
    )

    while enough_players(H_pool, L_pool):

        prob_H, tlabel = draw_treatment()
        inform        = random.choice([True, False])
        logger.debug(f"  → Nuevo treatment={tlabel}, prob_H={prob_H:.2f}, inform={inform}")

        trio = []
        for _ in range(GROUP_SIZE):
            pick_H = (random.random() < prob_H and H_pool) or not L_pool
            pool   = H_pool if pick_H else L_pool
            trio.append(pool.pop())

        treatment = {'prob_H': prob_H, 'label': tlabel, 'inform': inform}
        for p in trio:
            p.treatment   = json.dumps(treatment)
            p.partner_ids = json.dumps(
                [q.id_in_subsession for q in trio if q != p]
            )
        logger.info(
            f"    TRÍO conv: {[p.id_in_subsession for p in trio]} con {treatment}"
        )
        groups.append(trio)

    # ---------- remanentes = grupos Control ----------
    rem = H_pool + L_pool
    random.shuffle(rem)
    for p in rem:
        # opcionalmente, asegúrate de limpiar campos:
        p.treatment = ''
        p.partner_ids = '[]'
        groups.append([p])

    logger.debug(f"  Grupos formados: {len(groups)} (incluye {len(rem)} singleton para waitpage)")
    subsession.set_group_matrix(groups)




# -----------------------------------------------------------------------------
# Page Definitions
# -----------------------------------------------------------------------------
# Stage 1: Survey pages (only in round 1)
class _BasePunishPage(Page):
    template_name = 'new_experiment_design/PunishPage.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        f   = ctx['form']

        ctx['items'] = [
            # ---------- Escenario A ----------
            (None, INTRO_A),
            (f['preconv_punish_1'], YOUR_DECISION),
            (f['preconv_punish_5'], THEIR_DECISION_A),

            # ---------- Escenario B ----------
            (None, INTRO_B),
            (f['preconv_punish_2'], YOUR_DECISION),
            (f['preconv_punish_6'], THEIR_DECISION_B),

            # ---------- Escenario C ----------
            (None, INTRO_C),
            (f['preconv_punish_3'], YOUR_DECISION),
            (f['preconv_punish_7'], THEIR_DECISION_C),

            # ---------- Escenario D ----------
            (None, INTRO_D),
            (f['preconv_punish_4'], YOUR_DECISION),
            (f['preconv_punish_8'], THEIR_DECISION_D),
        ]
        return ctx








class ConsentFormPage(Page):
    form_model = 'player'
    form_fields = ['consent']
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

class IntroductionPage(Page):
    # This page is only shown in round 1
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

class ExperimentInstructions(Page):
    template_name = 'new_experiment_design/ExperimentInstructions.html'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

class PracticeBinaryQuestion(Page):
    form_model = 'player'
    form_fields = ['practice_binary_choice']
    
    # Display this page only in Round 1 (practice stage added after consent)
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Set the practice question and options.
        context.update({
            'practice_question': PRACTICE_QUESTION,
            'practice_options': PRACTICE_OPTIONS,
            'practice_notice': "ESTO ES UNA PRÁCTICA. La respuesta no contará para el estudio.",
        })
        return context

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Optionally, store the practice response in participant.vars if preferred.
        player.participant.vars['practice_binary_choice'] = player.practice_binary_choice
        logger.debug(f"Stored practice_binary_choice: {player.practice_binary_choice}")

class PracticeWillingnessToPayCost(Page):
    form_model = 'player'
    form_fields = ['practice_pay_to_judge']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use the PRACTICE_QUESTION as the reference text for judging.
        context['practice_question'] = PRACTICE_QUESTION
        context['practice_notice'] = "ESTO ES UNA PRÁCTICA. La respuesta no se usará en el emparejamiento real."
        # Here you can hardcode the question text or even add extra instructions
        return context

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['practice_pay_to_judge'] = player.practice_pay_to_judge
        logger.debug(f"Stored practice_pay_to_judge: {player.practice_pay_to_judge}")

class PracticePunishPage(_BasePunishPage):
    form_model  = 'player'
    form_fields = [f'practice_punish_{i}' for i in range(1, 9)]
    @staticmethod
    def is_displayed(player):        # ronda 1
        return player.round_number == 1
    

class PracticeSurveyWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        # (Optional) Log that all practice responses were received.
        logger.debug("All players have completed the practice survey.")

class PracticeGroupingWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        practice_pair_players(subsession)


    
class PracticeTreatmentAndDecision(Page):
    form_model = 'player'
    form_fields = ['second_choice']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        # 1) Pregunta y opciones de práctica
        current_question = PRACTICE_QUESTION
        options = PRACTICE_OPTIONS
        player.current_question_tag = current_question

        # 2) Cálculo de porcentaje dispuesto a juzgar
        players = player.subsession.get_players()
        judge_yes = sum(
            1 for p in players
            if p.participant.vars.get('practice_pay_to_judge')
        )
        judge_percent = (judge_yes / len(players)) * 100 if players else 0

        # 3) Selección del texto de tratamiento
        try:
            treatment = json.loads(player.treatment)
        except (TypeError, json.JSONDecodeError):
            treatment = {'label': 'Control', 'inform': False, 'practice': True}

        label = treatment.get('label', 'Control')
        if label == '0.5_H':
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>cinco</strong> a favor de '{options[0]}' y "
                f"<strong>cinco</strong> a favor de '{options[1]}'. Escogemos uno al azar."
            )
        elif label == '0.7_H':
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>siete</strong> a favor de '{options[0]}' y "
                f"<strong>tres</strong> a favor de '{options[1]}'. Escogemos uno al azar."
            )
        elif label == '0.7_L':
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>siete</strong> a favor de '{options[1]}' y "
                f"<strong>tres</strong> a favor de '{options[0]}'. Escogemos uno al azar."
            )
        else:
            selection_text = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>siete</strong> a favor de '{options[1]}' y "
                f"<strong>tres</strong> a favor de '{options[0]}'. Escogemos uno al azar."
            )

        treatment_text = (
            f"Para esta “conversación” de práctica, te hemos agrupado con otros dos "
            f"participantes usando la pregunta: '{current_question}'. {selection_text}"
        )

        inform_text = ""
        if treatment.get('inform'):
            inform_text = (
                f"Te informamos que el {judge_percent:.0f}% de los participantes "
                "estaban dispuestos a pagar 5 pesos para darle o quitarle 20 pesos a los demás miembros de su grupo "
                "después de observar la opinión que le expresó."
            )

        # 4) Aviso de práctica
        practice_notice = "ESTA ES UNA PRÁCTICA. Tu decisión pública es solo para entrenamiento."

        return {
            'treatment_text': treatment_text,
            'inform_text': inform_text,
            'current_question': current_question,
            'options': options,
            'practice_notice': practice_notice,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        opts = context['options']
        q    = context['current_question']

        if form:
            form.second_choice.choices = [
                ('H', opts[0]),
                ('L', opts[1]),
            ]
            form.second_choice.label = q

        return context


class PracticeSecondDecisionWaitPageForGroup(WaitPage):
    wait_for_all_groups = False
    template_name = 'otree/WaitPage.html'
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

class PracticePublicDisplayPage(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    @staticmethod
    def get_form_fields(player: Player):
        # En práctica sólo usamos el flag practice_pay_to_judge
        if player.participant.vars.get('practice_pay_to_judge'):
            return ['juicio_1', 'juicio_2']
        else:
            return []


    @staticmethod
    def vars_for_template(player: Player) -> dict:
        partners = get_partners(player)
        current_question = PRACTICE_QUESTION
        options = PRACTICE_OPTIONS

        # Collect each partner's choice text
        partner_choices = []
        for comp in partners:
            if comp.second_choice == 'H':
                partner_choices.append(options[0])
            elif comp.second_choice == 'L':
                partner_choices.append(options[1])
            else:
                partner_choices.append("No ha respondido")

        return {
            'partner_choices': partner_choices,
            'current_question': current_question,
            'show_judge_form': player.participant.vars.get('practice_pay_to_judge') is True,
        }
    
class PracticeLieQuestionPage(Page):
    form_model = 'player'
    form_fields = ['mentira_1', 'mentira_2']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        partners = get_partners(player)
        current_question = PRACTICE_QUESTION
        options = PRACTICE_OPTIONS

        partner_choices = []
        for comp in partners:
            if comp.second_choice == 'H':
                partner_choices.append(options[0])
            elif comp.second_choice == 'L':
                partner_choices.append(options[1])
            else:
                partner_choices.append("No ha respondido")

        return {
            'partner_choices': partner_choices,
            'current_question': current_question
        }

class BeliefPracticePage(Page):
    form_model  = 'player'
    form_fields = ['belief_practice_pct']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 2
    
    @staticmethod
    def vars_for_template(player):
        val = player.field_maybe_none('belief_practice_pct') or 50
        return dict(
            initial_val=val,
            label_text=BELIEF_QUESTION        # ← usa la constante
        )


class Comprehension(Page):
    form_model = 'player'
    form_fields = list(C.CORRECT_ANSWERS.keys())

    @staticmethod
    def before_next_page(player, timeout_happened):
        res, score = {}, 0
        for f in C.CORRECT_ANSWERS:
            given   = getattr(player, f)
            correct = C.CORRECT_ANSWERS[f]
            ok      = given == correct
            res[f] = dict(
            text    = C.QUESTION_TEXT[f],  # enunciado completo (HTML)
            given   = str(given),          # lo que marcó el participante
            correct = str(correct),        # clave correcta
            ok      = ok,                  # booleano
)

            score += ok
        # SOLO datos primitivos → siempre json-/pickle-safe
        player.participant.vars.update(comp_results=res, comp_score=score)

    @staticmethod
    def is_displayed(player):
        return player.round_number == 3





class ComprehensionFeedback(Page):
    @staticmethod
    def vars_for_template(player):
        results = player.participant.vars['comp_results']
        score   = player.participant.vars['comp_score']

        for fname, info in results.items():
            info['options']     = C.QUESTION_OPTIONS[fname]
            info['explanation'] = C.CORRECT_EXPLANATIONS[fname]

        return dict(
            results=results,
            score=score,
            total=len(C.CORRECT_ANSWERS),
        )


    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

class PersonalInfoPage(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'racial_identification', 'previous_experiment']
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

class PreConvBinaryQuestions(Page):
    form_model = 'player'
    form_fields = (
        ['pre_binary_choice_1', 'pre_binary_choice_2']
        + [f'binary_choice_{i}' for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
    )

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 3

    def get_context_data(self, **kwargs):
        ctx   = super().get_context_data(**kwargs)
        form  = kwargs['form']
        sess  = self.subsession.session

        # Asegura que existan los mapas de rotación
        hl_pre = sess.vars.setdefault(
                    'HL_preconv_map',
                    [random.choice([True, False]) for _ in PRE_CONV_QUESTIONS])
        hl_map = sess.vars.setdefault(
                    'HL_map',
                    [random.choice([True, False]) for _ in range(C.NUM_BINARY_QUESTIONS)])

        rendered = []

        # --- 2 preguntas pre-conversación ---
        pre_specs = [
            ("La Condesa", "Coyoacán"),
            ("Sí", "No"),
        ]
        for idx, fname in enumerate(['pre_binary_choice_1', 'pre_binary_choice_2']):
            field = form[fname]
            Htxt, Ltxt = pre_specs[idx]
            if not hl_pre[idx]:
                Htxt, Ltxt = Ltxt, Htxt
            field.choices = [('H', Htxt), ('L', Ltxt)]
            field.label   = PRE_CONV_QUESTIONS[idx]
            rendered.append(field)

        # --- 15 preguntas “generales” ---
        for j in range(C.NUM_BINARY_QUESTIONS):
            field = form[f'binary_choice_{j+1}']
            Htxt, Ltxt = FIRST_OPTIONS[j], SECOND_OPTIONS[j]
            if not hl_map[j]:
                Htxt, Ltxt = Ltxt, Htxt
            field.choices = [('H', Htxt), ('L', Ltxt)]
            field.label   = SURVEY_QUESTIONS[j]
            rendered.append(field)

        ctx['rendered_fields'] = rendered
        return ctx


    @staticmethod
    def before_next_page(player, timeout_happened):
        # Guarda ambos bloques en participant.vars
        player.participant.vars['pre_binary_choices'] = [
            player.pre_binary_choice_1,
            player.pre_binary_choice_2,
        ]
        player.participant.vars['binary_choices'] = [
            getattr(player, f'binary_choice_{i}')
            for i in range(1, C.NUM_BINARY_QUESTIONS + 1)
        ]



# 2) Página de WTP para ronda 3
class PreConvWillingnessToPayCost(Page):
    form_model = 'player'
    form_fields = (
        ['pay_preconv_1', 'pay_preconv_2']
        + [f'pay_to_judge_{i}' for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
    )

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Solo en la ronda 3 (después de guardar las respuestas binarias pre‐conversación)
        return player.round_number == 3

    def get_context_data(self, **kwargs):
        ctx   = super().get_context_data(**kwargs)
        form  = kwargs['form']

        q_and_f = [
            (PRE_CONV_QUESTIONS[0], form['pay_preconv_1']),
            (PRE_CONV_QUESTIONS[1], form['pay_preconv_2']),
        ]
        for i in range(C.NUM_BINARY_QUESTIONS):
            q_and_f.append( (SURVEY_QUESTIONS[i],
                            form[f'pay_to_judge_{i+1}']) )

        ctx['questions_and_fields'] = q_and_f
        return ctx


    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vars['pre_pay_to_judge_choices'] = [
            player.pay_preconv_1,
            player.pay_preconv_2,
        ]
        player.participant.vars['pay_to_judge_choices'] = [
            getattr(player, f'pay_to_judge_{i}')
            for i in range(1, C.NUM_BINARY_QUESTIONS + 1)
        ]

        logger.debug(f"Stored pre_pay_to_judge_choices: {player.participant.vars['pre_pay_to_judge_choices']}")

class PreConvPunishPage(_BasePunishPage):
    form_model  = 'player'
    form_fields = [f'preconv_punish_{i}' for i in range(1, 9)]
    @staticmethod
    def is_displayed(player):        # ronda 3
        return player.round_number == 3

# 3) Página de espera para sincronizar antes de pasar a las rondas de grupo
class PreConvSurveyWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Solo en la ronda 3, justo después del WTP pre‐conversación
        return player.round_number == 3

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        # Opcional: aquí podrías registrar métricas o debug
        logger.debug("Todos completaron el WTP pre‐conversación.")

# --- RONDAS 4–11: Pre-conversación ---

class PreConvGroupingWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Solo en rondas 4 a 11
        return 4 <= player.round_number <= 11

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        pair_preconv_players(subsession)


class PreConvTreatmentAndDecision(Page):
    form_model = 'player'
    form_fields = ['second_choice']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Sólo en rondas 4–11 y si efectivamente hay dos partners
        partner_ids = load_partner_ids(player)
        return (
            4 <= player.round_number <= 11
            and len(partner_ids) == 2
        )

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        # 1) Determinar sección 0 (rondas 4–7) o 1 (8–11)
        section = (player.round_number - 4) // 4

        # 2) Rotación H/L pre-conversación
        hl_pre = player.session.vars.get('HL_preconv_map', [True, True])
        if section == 0:
            text_H, text_L = "La Condesa", "Coyoacán"
        else:
            text_H, text_L = "Sí", "No"
        if hl_pre[section]:
            first_opt, second_opt = text_H, text_L
        else:
            first_opt, second_opt = text_L, text_H

        # 3) Pregunta actual
        current_q = PRE_CONV_QUESTIONS[section]
        player.current_question_tag = current_q

        # 4) Porcentaje dispuestos a juzgar
        players = player.subsession.get_players()
        judge_yes = sum(
            1 for p in players
            if p.participant.vars['pre_pay_to_judge_choices'][section]
        )
        pct = (judge_yes / len(players) * 100) if players else 0

        # 5) Texto de selección según tratamiento
        try:
            treatment = json.loads(player.treatment)
        except (TypeError, json.JSONDecodeError):
            treatment = {'label': 'Control', 'inform': False}
        label = treatment.get('label', 'Control')

        if label == '0.5_H':
            sel_txt = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez "
                f"candidatos. Hay <strong>cinco</strong> a favor de '{first_opt}' y "
                f"<strong>cinco</strong> a favor de '{second_opt}'."
            )
        elif label == '0.7_H':
            sel_txt = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez "
                f"candidatos. Hay <strong>siete</strong> a favor de '{first_opt}' y "
                f"<strong>tres</strong> a favor de '{second_opt}'."
            )
        elif label == '0.7_L':
            sel_txt = (
                f"Para determinar cada individuo del trío, tomamos un grupo de diez "
                f"candidatos. Hay <strong>siete</strong> a favor de '{second_opt}' y "
                f"<strong>tres</strong> a favor de '{first_opt}'."
            )
        else:
            sel_txt = "Escogimos el grupo sin tomar en cuenta las posturas de las diez personas."

        treatment_text = (
            f"Para esta “conversación”, te hemos agrupado con otros dos participantes "
            f"usando la pregunta: '{current_q}'. {sel_txt} Escogemos uno al azar."
        )

        inform_text = ""
        if treatment.get('inform'):
            inform_text = (
                f"Te informamos que el {pct:.0f}% de los participantes están dispuestos "
                "a pagar 5 pesos para dar o quitar 20 pesos a los demás miembros de su grupo después de "
                "observar la opinión que les expresaron."
            )

        # 6) Opciones para la decisión simultánea
        if hl_pre[section]:
            options = (text_H, text_L)
        else:
            options = (text_L, text_H)

        return {
            'treatment_text':   treatment_text,
            'inform_text':      inform_text,
            'current_question': current_q,
            'options':          options,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        opts = context['options']
        q    = context['current_question']

        if form:
            form.second_choice.choices = [
                ('H', opts[0]),
                ('L', opts[1]),
            ]
            form.second_choice.label = q

        return context



class PreConvSecondDecisionWaitPage(WaitPage):
    wait_for_all_groups = False
    template_name = 'otree/WaitPage.html'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Usamos field_maybe_none para evitar TypeError si partner_ids es None
        partner_ids = load_partner_ids(player)
        return (
            4 <= player.round_number <= 11
            and len(partner_ids) == 2
        )


class PreConvPublicDisplayPage(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Usamos field_maybe_none para evitar TypeError si partner_ids es None
        partner_ids = load_partner_ids(player)
        return (
            4 <= player.round_number <= 11
            and len(partner_ids) == 2
        )

    @staticmethod
    def get_form_fields(player):
        section = (player.round_number - 4) // 4
        pay = player.participant.vars['pre_pay_to_judge_choices'][section]
        return ['juicio_1', 'juicio_2'] if pay else []

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        section = (player.round_number - 4) // 4
        current_question = PRE_CONV_QUESTIONS[section]

        # Textos rotados igual que en la decisión simultánea
        text_H, text_L = ("La Condesa", "Coyoacán") if section == 0 else ("Sí", "No")
        if player.session.vars['HL_preconv_map'][section]:
            opt_H, opt_L = text_H, text_L
        else:
            opt_H, opt_L = text_L, text_H

        partners = get_partners(player)
        partner_choices = []
        for p in partners:
            choice = getattr(p, 'second_choice', None)
            if choice == 'H':
                partner_choices.append(opt_H)
            elif choice == 'L':
                partner_choices.append(opt_L)
            else:
                partner_choices.append("No ha respondido")

        return {
            'partner_choices': partner_choices,
            'current_question': current_question,
            'show_judge_form': player.participant.vars['pre_pay_to_judge_choices'][section],
        }


class PreConvLieQuestionPage(Page):
    form_model = 'player'
    form_fields = ['mentira_1', 'mentira_2']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Usamos field_maybe_none para evitar TypeError si partner_ids es None
        partner_ids = load_partner_ids(player)
        return (
           4 <= player.round_number <= 11
            and len(partner_ids) == 2
        )

    @staticmethod
    def vars_for_template(player: Player):
        # 1) Determinar sección y pregunta
        section = (player.round_number - 4) // 4
        current_question = PRE_CONV_QUESTIONS[section]

        # 2) Definir los textos H/L para esta sección
        if section == 0:
            text_H, text_L = "La Condesa", "Coyoacán"
        else:
            text_H, text_L = "Sí", "No"

        # 3) Aplicar rotación según HL_preconv_map
        hl_map = player.session.vars.get('HL_preconv_map', [True, True])
        if hl_map[section]:
            opt_H, opt_L = text_H, text_L
        else:
            opt_H, opt_L = text_L, text_H

        # 4) Construir la lista de respuestas públicas de los compañeros
        partners = get_partners(player)
        partner_choices = []
        for p in partners:
            choice = getattr(p, 'second_choice', None)
            if choice == 'H':
                partner_choices.append(opt_H)
            elif choice == 'L':
                partner_choices.append(opt_L)
            else:
                partner_choices.append("No ha respondido")

        return {
            'partner_choices': partner_choices,
            'current_question': current_question,
        }


class PreConvEndGroupWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return 4 <= player.round_number <= 11

class BeliefPreConvPage(Page):
    form_model  = 'player'
    form_fields = ['belief_preconv_pct']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        in_preconv_round = 4 <= player.round_number <= 11
        grouped          = len(load_partner_ids(player)) == 2
        return in_preconv_round and grouped
    
    @staticmethod
    def vars_for_template(player):
        val = player.field_maybe_none('belief_preconv_pct') or 50
        return dict(
            initial_val=val,
            label_text=BELIEF_QUESTION        # ← usa la constante
        )
    

class BinaryQuestions(Page):
    form_model = 'player'
    
    @staticmethod
    def get_form_fields(player: Player):
        return [f"binary_choice_{i}" for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 12

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['binary_choices'] = [
            getattr(player, f"binary_choice_{i}") for i in range(1, C.NUM_BINARY_QUESTIONS + 1)
        ]
        logger.debug(f"Stored binary_choices: {player.participant.vars['binary_choices']}")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1) Extraer el form de kwargs
        form = kwargs.get('form')

        # 2) Recuperar o generar el HL_map
        session = self.player.session
        hl_map = session.vars.get('HL_map')
        if hl_map is None:
            hl_map = [random.choice([True, False])
                      for _ in range(C.NUM_BINARY_QUESTIONS)]
            session.vars['HL_map'] = hl_map
            logger.warning(f"HL_map no encontrado: creado sobre la marcha: {hl_map}")

        # 3) Construir la lista de campos ya “rotados”
        rendered_fields = []
        for i in range(C.NUM_BINARY_QUESTIONS):
            field = form[f"binary_choice_{i+1}"]
            if hl_map[i]:
                field.choices = [
                    ('H', FIRST_OPTIONS[i]),
                    ('L', SECOND_OPTIONS[i])
                ]
            else:
                field.choices = [
                    ('H', SECOND_OPTIONS[i]),
                    ('L', FIRST_OPTIONS[i])
                ]
            field.label = SURVEY_QUESTIONS[i]
            rendered_fields.append(field)

        # 4) Pasar al template
        context['rendered_fields'] = rendered_fields
        context['question_list']    = list(range(1, C.NUM_BINARY_QUESTIONS + 1))
        return context


class WillingnessToPayCost(Page):
    form_model = 'player'
    
    @staticmethod
    def get_form_fields(player: Player):
        return [f"pay_to_judge_{i}" for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 12
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        field_names = [f"pay_to_judge_{i}" for i in range(1, C.NUM_BINARY_QUESTIONS + 1)]
        rendered_fields = [form[field_name] for field_name in field_names]
        question_texts = SURVEY_QUESTIONS  
        context['questions_and_fields'] = list(zip(question_texts, rendered_fields))
        return context

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pay_choices = []
        for i in range(1, C.NUM_BINARY_QUESTIONS + 1):
            field_name = f"pay_to_judge_{i}"
            pay_choices.append(getattr(player, field_name))
        player.participant.vars['pay_to_judge_choices'] = pay_choices
        logger.debug(f"Stored pay_to_judge_choices: {pay_choices}")

class ConvPunishPage(_BasePunishPage):
    form_model  = 'player'
    form_fields = [f'conv_punish_{i}' for i in range(1, 9)]
    @staticmethod
    def is_displayed(player):        # ronda 12
        return player.round_number == 12

class SurveyWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 12

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        if 'question_order' not in subsession.session.vars:
            order = list(range(C.NUM_BINARY_QUESTIONS))
            random.shuffle(order)
            subsession.session.vars['question_order'] = order
            logger.debug(f"SurveyWaitPage set question_order: {order}")

# Stage 2: Group interaction pages (only for rounds > 3)
class GroupingWaitPage(WaitPage):
    wait_for_all_groups = True
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number >= 13

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        pair_players(subsession)

class TreatmentAndDecision(Page):
    form_model = 'player'
    form_fields = ['second_choice']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Usamos field_maybe_none para evitar TypeError si partner_ids es None
        partner_ids = load_partner_ids(player)
        return (
            player.round_number >= 12
            and len(partner_ids) == 2
        )

    @staticmethod
    def vars_for_template(player: Player):
        # --- Lógica de TreatmentInformation.vars_for_template ---
        qi     = player.session.vars['question_order'][player.round_number - 12]
        hl_map = player.session.vars['HL_map']
        first_option  = FIRST_OPTIONS[qi]
        second_option = SECOND_OPTIONS[qi]
        if not hl_map[qi]:
            first_option, second_option = second_option, first_option

        current_question = SURVEY_QUESTIONS[qi]
        player.current_question_tag = current_question

        players    = player.subsession.get_players()
        judge_yes  = sum(1 for p in players if p.participant.vars['pay_to_judge_choices'][qi])
        judge_pct  = (judge_yes / len(players)) * 100 if players else 0

        treatment = json.loads(player.treatment or '{"label":"Control","inform":false}')
        label     = treatment.get('label', 'Control')
        if label == '0.5_H':
            selection_text = (
                "Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>cinco</strong> a favor de '{first_option}' y "
                f"<strong>cinco</strong> a favor de '{second_option}'. Escogemos uno al azar."
            )
        elif label == '0.7_H':
            selection_text = (
                "Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>siete</strong> a favor de '{first_option}' y "
                f"<strong>tres</strong> a favor de '{second_option}'. Escogemos uno al azar."
            )
        elif label == '0.7_L':
            selection_text = (
                "Para determinar cada individuo del trío, tomamos un grupo de diez candidatos. "
                f"Hay <strong>siete</strong> a favor de '{second_option}' y "
                f"<strong>tres</strong> a favor de '{first_option}'. Escogemos uno al azar."
            )
        else:
            selection_text = "Escogimos el grupo sin tomar en cuenta las posturas de las diez personas."

        treatment_text = (
            f"Para esta “conversación”, te hemos agrupado con otros dos participantes usando la pregunta de práctica: "
            f"'{current_question}'. {selection_text}"
        )

        inform_text = ""
        if treatment.get('inform'):
            inform_text = (
                f"Te informamos que el {judge_pct:.0f}% de los participantes están dispuestos a pagar 5 pesos "
                "para darle o quitarle 20 pesos a los demás miembros de su grupos después de observar la opinión que le expresaron."
            )

        # --- Lógica de PublicDecision.get_context_data para opciones del formulario ---
        if hl_map[qi]:
            options = (FIRST_OPTIONS[qi], SECOND_OPTIONS[qi])
        else:
            options = (SECOND_OPTIONS[qi], FIRST_OPTIONS[qi])

        return {
            'treatment_text': treatment_text,
            'inform_text':    inform_text,
            'current_question': current_question,
            'options': options,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        # Usamos lo que ya está en context
        opts = context['options']
        q   = context['current_question']

        form.second_choice.choices = [
            ('H', opts[0]),
            ('L', opts[1]),
        ]
        form.second_choice.label = q
        return context

class SecondDecisionWaitPageForGroup(WaitPage):
    wait_for_all_groups = False
    template_name = 'otree/WaitPage.html'
    
    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Usamos field_maybe_none para evitar TypeError si partner_ids es None
        partner_ids = load_partner_ids(player)
        return (
            player.round_number >= 12
            and len(partner_ids) == 2
        )

class PublicDisplayPage(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Usamos field_maybe_none para evitar TypeError si partner_ids es None
        partner_ids = load_partner_ids(player)
        return (
            player.round_number >= 12
            and len(partner_ids) == 2
        )

    @staticmethod
    def get_form_fields(player):
        qi = player.session.vars['question_order'][player.round_number - 12]
        pay_choices = player.participant.vars.get('pay_to_judge_choices',
                                                  [False]*C.NUM_BINARY_QUESTIONS)
        return ['juicio_1', 'juicio_2'] if pay_choices[qi] else []


    @staticmethod
    def vars_for_template(player: Player):
        qi      = player.session.vars['question_order'][player.round_number - 12]
        hl_map  = player.session.vars['HL_map']
        partners = get_partners(player)

        if hl_map[qi]:
            options = (FIRST_OPTIONS[qi], SECOND_OPTIONS[qi])
        else:
            options = (SECOND_OPTIONS[qi], FIRST_OPTIONS[qi])

        partner_choices = [
            options[0] if p.second_choice == 'H'
            else options[1] if p.second_choice == 'L'
            else "No ha respondido"
            for p in partners
        ]

        show_judge_form = player.participant.vars['pay_to_judge_choices'][qi]
        return dict(partner_choices=partner_choices,
                    current_question=SURVEY_QUESTIONS[qi],
                    show_judge_form=show_judge_form)

class LieQuestionPage(Page):
    form_model = 'player'
    form_fields = ['mentira_1', 'mentira_2']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        # Usamos field_maybe_none para evitar TypeError si partner_ids es None
        partner_ids = load_partner_ids(player)
        return (
            player.round_number >= 12
            and len(partner_ids) == 2
        )

    @staticmethod
    def vars_for_template(player: Player):
        qi      = player.session.vars['question_order'][player.round_number - 12]
        hl_map  = player.session.vars['HL_map']
        partners = get_partners(player)

        if hl_map[qi]:
            options = (FIRST_OPTIONS[qi], SECOND_OPTIONS[qi])
        else:
            options = (SECOND_OPTIONS[qi], FIRST_OPTIONS[qi])

        partner_choices = [
            options[0] if p.second_choice == 'H'
            else options[1] if p.second_choice == 'L'
            else "No ha respondido"
            for p in partners
        ]

        return dict(partner_choices=partner_choices,
                    current_question=SURVEY_QUESTIONS[qi])

class EndGroupWaitPage(WaitPage):
    wait_for_all_groups = True  # espera a todos los que vean esta página
    @staticmethod
    def is_displayed(player: Player) -> bool:
        # todos los jugadores (grupales y singleton) la ven en rondas > 3
        return player.round_number >= 12 

class BeliefConversationPage(Page):
    form_model  = 'player'
    form_fields = ['belief_conv_pct']

    @staticmethod
    def is_displayed(player: Player) -> bool:
        in_conv_round = 13 <= player.round_number <= 27
        grouped       = len(load_partner_ids(player)) == 2
        return in_conv_round and grouped
    
    @staticmethod
    def vars_for_template(player):
        val = player.field_maybe_none('belief_conv_pct') or 50
        return dict(
            initial_val=val,
            label_text=BELIEF_QUESTION        # ← usa la constante
        )

class ThankYouPage(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        return {}

# -----------------------------------------------------------------------------
# Page Sequence
# -----------------------------------------------------------------------------
page_sequence = [
    # --- Round 1: Pre-Practice Survey Stage ---
    #ConsentFormPage,              # Only in round 1
    ExperimentInstructions,       # Only in round 1
    #PersonalInfoPage,            # Only in round 1
    #PracticeBinaryQuestion,       # Only in round 1 (practice survey)
    #PracticeWillingnessToPayCost, # Only in round 1 (practice survey)
    #PracticeSurveyWaitPage,       # Only in round 1 (practice survey wait)

    # --- Round 2: Practice Group Interaction Stage ---
    #PracticeGroupingWaitPage,             # Only in round 2
    #PracticeTreatmentAndDecision,
    #PracticeSecondDecisionWaitPageForGroup,  # Only in round 2
    #PracticePublicDisplayPage,            # Only in round 2
    #PracticeLieQuestionPage,              # Only in round 2
    #BeliefPracticePage,
    #Comprehension,
    #ComprehensionFeedback,

    PreConvBinaryQuestions,         # Ronda 3
    PreConvWillingnessToPayCost,    # 
    #PreConvPunishPage, 
    #PreConvSurveyWaitPage,          # 

    #PreConvGroupingWaitPage,        #Rondas 4-11
    #PreConvTreatmentAndDecision,          # Rondas 4-11
    #PreConvSecondDecisionWaitPage,
    #PreConvPublicDisplayPage,
    #PreConvLieQuestionPage,
    #BeliefPreConvPage,
    #PreConvEndGroupWaitPage,
    SurveyWaitPage,              

    GroupingWaitPage,            # Ronda 13-27
    TreatmentAndDecision,            
    SecondDecisionWaitPageForGroup,  
    PublicDisplayPage,           
    LieQuestionPage, 
    BeliefConversationPage,            
    EndGroupWaitPage,
    ThankYouPage                 
]
