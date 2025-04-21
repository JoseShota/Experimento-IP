from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # ► Etiquetas en el mismo orden que binary_choice_1 … binary_choice_37
    TOPIC_LABELS = [
        "¿Estás a favor o en contra de la legalización y regularización de la marihuana en México?",
        "¿La quesadilla lleva o no queso?",
        "¿Crees que debería haber más medidas de control de armas en México o que las personas tienen derecho a poseer armas para protegerse?",
        "¿Estás de acuerdo con la frase 'el dinero compra la felicidad'?",
        "¿Crees que el ser humano es inherentemente bueno o malo?",
        "¿Estarías de acuerdo en que los menores de edad puedan iniciar un proceso de transcición de género si así lo quieren?",
        "En China, cuando los abuelos contraen una enfermedad terminal, las familias acostumbran a no decirles. ¿Estás de acuerdo con esta práctica?",
        "¿Crees que las relaciones a distancia pueden ser tan exitosas como las relaciones en persona?",
        "¿Estarías de acuerdo que en tu empresa contraten a un ex convicto, aunque no trabajes con él?",
        "¿Estás de acuerdo que la clave para salir de la pobreza, en México, es el trabajo duro?",
        "Llega contigo tu mejor amiga/o que acaba de hacerse un nuevo corte de pelo. Emocionada/o te pregunta si te gusta, pero a ti te parece que fue una terrible decisión. ¿Crees que mentir en esta situación es justificable, sabiendo que la verdad le haría sentir muy mal?",
        "¿Crees que el gobierno debería tener el poder de prohibirte fumar incluso en espacios al aire libre como playas o parques públicos?",
        "¿Crees que los migrantes deberían tener los mismos derechos y oportunidades que los ciudadanos mexicanos?",
        "¿Qué equipo de futbol es mejor: el América o las Chivas?",
        "¿Estás de acuerdo con la frase 'no hay paz sin la violencia'?",
        "Verdadero o falso: El arte que se exhibe en los museos de arte contemporáneo ya no tiene el mismo virtuosismo que el arte en los museos clásicos",
        "¿Crees que los videojuegos violentos fomentan actitudes violentas en la vida real?",
        "¿Cuál es la forma correcta de llamarle: quesillo o queso Oaxaca?",
        "¿Crees que uno de los criterios principales para contratar a alguien en México es el color de piel?",
        "¿Quién tiene mejor música, Luis Miguel o Juan Gabriel?",
        "¿Estás de acuerdo en que hay que separar el arte de Michael Jackson del artista?",
        "Estás en una guerra y debes decidir si salvar la vida de tu compañero o la de un niño inocente que está en peligro. ¿A quién salvarías?",
        "¿Es ético tener una relación romántica o sexual con alguien en una posición de poder, como un profesor o un jefe?",
        "¿Estás de acuerdo en que el uso de las drogas deteriora la vida de las personas?",
        "¿Estás de acuerdo con la pena de muerte?",
        "¿Estás de acuerdo con la eutanasia y el suicidio asistido?",
        "¿Qué es más importante, afrontar la crisis climática o terminar la pobreza extrema en el mundo?",
        "Imagina que estás en el Titanic al momento de su hundimiento, ¿estás a favor de que se salven primero a los ancianos?",
        "Una persona rica y grosera tira un billete de cien pesos sin darse cuenta. ¿Deberías devolvérselo?",
        "¿Qué región del país es más bonita?",
        "¿Qué es lo más higiénico, bañarse en la mañana o en la noche?",
        "Ves que un tren se dirige hacia cuatro personas. Tienes la posibilidad de desviarlo a un camino que se dirige a una persona. ¿Lo desvías?",
        "¿Qué saga de películas es mejor: Harry Potter o El Señor de los Anillos?",
        "¿Qué lugar mejor: La Condesa o Coyoacán?",
        "¿Qué tan rápido México debería transicionar a las energías renovables, tomando en cuenta que entre más rápido transicionar peor va a ser el crecimiento económico dado que el petróleo es un tercio de la economía del país?",
        "Tienes la opción de salvar la vida de un niño que está en peligro pero para hacerlo, debes poner en riesgo tu propia vida, con un 10 por ciento de probabilidad de perderla. ¿Lo harías?",
        "¿Estás de acuerdo en que enseñar a los alumnos a utilizar adecuadamente los métodos anticonceptivos sea obligatorio en las escuelas mexicanas?"
    ]

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField(
        label='He leído y doy mi consentimiento para participar en el estudio.',
        widget=widgets.CheckboxInput,   # <- fuerza checkbox
        blank=False                     # requiere marcarla
    )

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

    binary_choice_1 = models.StringField(
        choices=[('H', "A favor"), ('L', "En contra")],
        blank=False,
        label="¿Estás a favor o en contra de la legalización y regularización de la marihuana en México?"
    )
    binary_choice_2 = models.StringField(
        choices=[('H', "Sí, la quesadilla lleva queso"), ('L', "No, la quesadilla no lleva queso")],
        blank=False,
        label="¿La quesadilla lleva o no queso?"
    )
    binary_choice_3 = models.StringField(
        choices=[('H', "Más medidas de control"), ('L', "Derecho a poseer armas")],
        blank=False,
        label="¿Crees que debería haber más medidas de control de armas en México o que las personas tienen derecho a poseer armas para protegerse?"
    )
    binary_choice_4 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo con la frase 'el dinero compra la felicidad'?"
    )
    binary_choice_5 = models.StringField(
        choices=[('H', "Bueno"), ('L', "Malo")],
        blank=False,
        label="¿Crees que el ser humano es inherentemente bueno o malo?"
    )
    binary_choice_6 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],  
        blank=False,
        label="¿Estarías de acuerdo en que los menores de edad puedan iniciar un proceso de transcición de género si así lo quieren?"
    )
    binary_choice_7 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="En China, cuando los abuelos contraen una enfermedad terminal, las familias acostumbran a no decirles. ¿Estás de acuerdo con esta práctica?"
    )
    binary_choice_8 = models.StringField(
        choices=[('H', "Sí lo pueden ser"), ('L', "No pueden llegar a serlo")],
        blank=False,
        label="¿Crees que las relaciones a distancia pueden ser tan exitosas como las relaciones en persona?"
    )
    binary_choice_9 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estarías de acuerdo que en tu empresa contraten a un ex convicto, aunque no trabajes con él?"
    )
    binary_choice_10 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo que la clave para salir de la pobreza, en México, es el trabajo duro?"
    )
    binary_choice_11 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="Llega contigo tu mejor amiga/o que acaba de hacerse un nuevo corte de pelo. Emocionada/o te pregunta si te gusta, pero a ti te parece que fue una terrible decisión. ¿Crees que mentir en esta situación es justificable, sabiendo que la verdad le haría sentir muy mal?"
    )
    binary_choice_12 = models.StringField(
        choices=[('H', "Sí debería"), ('L', "No debería")],
        blank=False,
        label="¿Crees que el gobierno debería tener el poder de prohibirte fumar incluso en espacios al aire libre como playas o parques públicos?"
    )
    binary_choice_13 = models.StringField(
        choices=[('H', "Sí deberían"), ('L', "No deberían")],
        blank=False,
        label="¿Crees que los migrantes deberían tener los mismos derechos y oportunidades que los ciudadanos mexicanos?"
    )
    binary_choice_14 = models.StringField(
        choices=[('H', "El América"), ('L', "Las Chivas")],
        blank=False,
        label="¿Qué equipo de futbol es mejor: el América o las Chivas?"
    )
    binary_choice_15 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo con la frase 'no hay paz sin la violencia'?"
    )
    binary_choice_16 = models.StringField(
        choices=[('H', "Verdadero"), ('L', "Falso")],
        blank=False,
        label="Verdadero o falso: El arte que se exhibe en los museos de arte contemporáneo ya no tiene el mismo virtuosismo que el arte en los museos clásicos",
    )
    binary_choice_17 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="¿Crees que los videojuegos violentos fomentan actitudes violentas en la vida real?"
    )
    binary_choice_18 = models.StringField(
        choices=[('H', "Quesillo"), ('L', "Queso Oaxaca")],
        blank=False,
        label="¿Cuál es la forma correcta de llamarle: quesillo o queso Oaxaca?"
    )
    binary_choice_19 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="¿Crees que uno de los criterios principales para contratar a alguien en México es el color de piel?"
    )
    binary_choice_20 = models.StringField(
        choices=[('H', "Luis Miguel"), ('L', "Juan Gabriel")],
        blank=False,
        label="¿Quién tiene mejor música, Luis Miguel o Juan Gabriel?"
    )
    binary_choice_21 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo en que hay que separar el arte de Michael Jackson del artista?"
    )
    binary_choice_22 = models.StringField(
        choices=[('H', "A mi compañero"), ('L', "Al niño")],
        blank=False,
        label="Estás en una guerra y debes decidir si salvar la vida de tu compañero o la de un niño inocente que está en peligro. ¿A quién salvarías?"
    )
    binary_choice_23 = models.StringField(
        choices=[('H', "Sí lo es"), ('L', "No lo es")],
        blank=False,
        label="¿Es ético tener una relación romántica o sexual con alguien en una posición de poder, como un profesor o un jefe?"
    )
    binary_choice_24 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo en que el uso de las drogas deteriora la vida de las personas?"
    )
    binary_choice_25 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo con la pena de muerte?"
    )
    binary_choice_26 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="¿Estás de acuerdo con la eutanasia y el suicidio asistido?"
    )
    binary_choice_27 = models.StringField(
        choices=[('H', "Afrontar la crisis climática"), ('L', "Terminar la pobreza extrema en el mundo")],
        blank=False,
        label="¿Qué es más importante, afrontar la crisis climática o terminar la pobreza extrema en el mundo?"
    )
    binary_choice_28 = models.StringField(
        choices=[('H', "A favor"), ('L', "En contra")],
        blank=False,
        label="Imagina que estás en el Titanic al momento de su hundimiento, ¿estás a favor de que se salven primero a los ancianos?"
    )
    binary_choice_29 = models.StringField(
        choices=[('H', "Sí, debería devolvérselo"), ('L', "No, no debería devolvérselo")],
        blank=False,
        label="Una persona rica y grosera tira un billete de cien pesos sin darse cuenta. ¿Deberías devolvérselo?"
    )
    binary_choice_30 = models.StringField(
        choices=[('H', "El Norte"), ('L', "El Sur")],
        blank=False,
        label="¿Qué región del país es más bonita?"
    )
    binary_choice_31 = models.StringField(
        choices=[('H', "Bañarse en la mañana"), ('L', "Bañarse en la noche")],
        blank=False,
        label="¿Qué es lo más higiénico, bañarse en la mañana o en la noche?"
    )
    binary_choice_32 = models.StringField(
        choices=[('H', "Sí lo desvío"), ('L', "Dejo que siga su trayecto")],
        blank=False,
        label="Ves que un tren se dirige hacia cuatro personas. Tienes la posibilidad de desviarlo a un camino que se dirige a una persona. ¿Lo desvías?"
    )
    binary_choice_33 = models.StringField(
        choices=[('H', "Harry Potter"), ('L', "El Señor de los Anillos")],
        blank=False,
        label="¿Qué saga de películas es mejor: Harry Potter o El Señor de los Anillos?"
    )
    binary_choice_34 = models.StringField(
        choices=[('H', "La Condesa"), ('L', "Coyoacán")],
        blank=False,
        label="¿Qué lugar es mejor: La Condesa o Coyoacán?"
    )
    binary_choice_35 = models.StringField(
        choices=[('H', "En 10 años"), ('L', "En 25 años")],
        blank=False,
        label="¿Qué tan rápido México debería transicionar a las energías renovables, tomando en cuenta que entre más rápido transicionar peor va a ser el crecimiento económico dado que el petróleo es un tercio de la economía del país?"
    )
    binary_choice_36 = models.StringField(
        choices=[('H', "Sí"), ('L', "No")],
        blank=False,
        label="Tienes la opción de salvar la vida de un niño que está en peligro pero para hacerlo, debes poner en riesgo tu propia vida, con un 10 por ciento de probabilidad de perderla. ¿Lo harías?"
    )
    binary_choice_37 = models.StringField(
        choices=[('H', "De acuerdo"), ('L', "En desacuerdo")],
        blank=False,
        label="¿Estás de acuerdo en que enseñar a los alumnos a utilizar adecuadamente los métodos anticonceptivos sea obligatorio en las escuelas mexicanas?"
    )
    more_binary_choice = models.StringField(
        blank=False,
        label="¿Qué otra/s pregunta/s sobre temas divisivos se te vienen a la mente?"
    )

for idx, topic in enumerate(C.TOPIC_LABELS, start=1): 
    setattr( 
        Player, f'reaction_pay_{idx}',
        models.StringField(
            choices=[('Y', 'Sí, pagaría'), ('N', 'No pagaría')],
            blank=False, label=( f'Vas a escuchar la opinión de una persona sobre el tema: <strong>{topic}</strong> ' '¿Pagarías <strong>5 pesos</strong> de lo que tienes para ' 'darle o quitarle <strong>20 pesos</strong> a esa persona?' ) ), )

# ─── 1) ¿Cuánto dinero pagaría?  (Currency / Integer) ───────────────
for idx, topic in enumerate(C.TOPIC_LABELS, start=1):
    setattr(
        Player,
        f'inc_pay_{idx}',
        models.IntegerField(          # usa CurrencyField si conviertes a puntos
            min=0,
            label=(
                f'Vas a escuchar la opinión de una persona sobre el tema: <strong>{topic}</strong>. '
                '¿Cuánto dinero estás dispuesto a pagar para darle o quitarle '
                '<strong>20 pesos</strong> a esa persona? '
                'Considera que después de dar tu respuesta tiraremos un dado: si sale por arriba de tu cifra no '
                'pagas nada; si sale por debajo, pagarás la cantidad que salga.'
            )
        ),
    )

# ─── 2) ¿Decir la verdad o mentir? (prob. juzgado = 50 %) ───────────
for idx, topic in enumerate(C.TOPIC_LABELS, start=1):
    setattr(
        Player,
        f'truth50_{idx}',
        models.StringField(
            choices=[('T', 'Diría la verdad'), ('M', 'Mentiría')],
            blank=False,
            label=(
                f'Vas a dar tu opinión a una persona sobre el tema: <strong>{topic}</strong>. '
                'La probabilidad de que la otra persona haya pagado 5 pesos para darte o quitarte 20 pesos después de dar tu opinión es de (Variamos).'
                'Si dices la verdad obtienes 10 pesos; si te juzgan '
                'negativamente pierdes 20 pesos. ¿Dirías la verdad o mentirías?'
            )
        ),
    )

# ─── 3) Probabilidad‑umbral para mentir ─────────────────────────────
for idx, topic in enumerate(C.TOPIC_LABELS, start=1):
    setattr(
        Player,
        f'threshold_prob_{idx}',
        models.IntegerField(
            min=0,
            max=100,
            label=(
                f'Imagínate que una persona con una opinión diferente a ti va a escuchar tu opinión sobre el tema: <strong>{topic}</strong>. '
                '¿Qué tan probable tiene que ser que esa persona pague 5 pesos para darte o quitarte 20 pesos para que mientas en el tema? Danos una probabilidad de la cual, por debajo das tu opinión verdadera y por arriba mientes sobre tu opinión.'
            )
        ),
    )




class ConsentForm(Page):
    form_model = 'player'
    form_fields = ['consent']

    # optional: don’t let them continue without the box ticked
    def error_message(player, values):
        if not values['consent']:
            return 'Debes aceptar para continuar.'
    

class Intro(Page):
    @staticmethod
    def is_displayed(player):
        return player.consent  # sólo si aceptó el consentimiento


class PersonalInfo(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'racial_identification', 'previous_experiment']
    
    @staticmethod
    def is_displayed(player):
        return player.consent  # sólo si aceptó el consentimiento


class BinaryQuestions(Page):
    form_model = 'player'
    form_fields = ['binary_choice_1', 'binary_choice_2', 'binary_choice_3', 'binary_choice_4', 'binary_choice_5','binary_choice_6','binary_choice_7','binary_choice_8','binary_choice_9','binary_choice_10','binary_choice_11','binary_choice_12','binary_choice_13','binary_choice_14','binary_choice_15','binary_choice_16','binary_choice_17','binary_choice_18','binary_choice_19','binary_choice_20','binary_choice_21','binary_choice_22','binary_choice_23','binary_choice_24','binary_choice_25','binary_choice_26','binary_choice_27','binary_choice_28','binary_choice_29','binary_choice_30','binary_choice_31','binary_choice_32','binary_choice_33','binary_choice_34', 'binary_choice_35', 'binary_choice_36', 'binary_choice_37', 'more_binary_choice']

    @staticmethod
    def is_displayed(player):
        return player.consent  # sólo si aceptó el consentimiento
    
class Reactions(Page):
 form_model = 'player'
 form_fields = [f'reaction_pay_{i}' for i in range(1, 38)]

 @staticmethod
 def is_displayed(player):
     return player.consent

class IncPay(Page):
    form_model = 'player'
    form_fields = [f'inc_pay_{i}' for i in range(1, 38)]

    @staticmethod
    def is_displayed(player):
        return player.consent


class Truth50(Page):
    form_model = 'player'
    form_fields = [f'truth50_{i}' for i in range(1, 38)]

    @staticmethod
    def is_displayed(player):
        return player.consent


class Threshold(Page):
    form_model = 'player'
    form_fields = [f'threshold_prob_{i}' for i in range(1, 38)]

    @staticmethod
    def is_displayed(player):
        return player.consent


page_sequence = [
    ConsentForm, Intro, PersonalInfo,
    BinaryQuestions,      # parte 2
    Reactions,            # parte 3.1
    IncPay,               # parte 3.2
    Truth50,              # parte 3.3
    Threshold             # parte 3.4
]

