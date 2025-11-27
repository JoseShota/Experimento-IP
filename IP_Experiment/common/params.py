# common/params.py  (compartido por stage_1, stage_2 y payment)
TOPIC_LABELS = (
    "Topic 1","Topic 2","Topic 3","Topic 4","Topic 5",
    "Topic 6","Topic 7","Topic 8","Topic 9","Topic 10",
)
TREATMENT_CODES = (
    "New_Ten_Ninety","New_Twenty_Eighty","New_Thirty_Seventy",
    "New_Forty_Sixty","New_Fifty_Fifty","New_Sixty_Forty",
    "New_Seventy_Thirty","New_Eighty_Twenty","New_Ninety_Ten",
)
BINARY_OPTIONS = (
    ('Option H', 'Option L'),  # Question 1
    ('Option H', 'Option L'),  # Question 2
    ('Option H', 'Option L'),  # Question 3
    ('Option H', 'Option L'),  # Question 4
    ('Option H', 'Option L'),  # Question 5
    ('Option H', 'Option L'),  # Question 6
    ('Option H', 'Option L'),  # Question 7
    ('Option H', 'Option L'),  # Question 8
    ('Option H', 'Option L'),  # Question 9
    ('Option H', 'Option L'),  # Question 10
)
TREATMENT_TO_COUNTS = {
        'New_Ten_Ninety':   (1, 9),  # note the original spelling is kept
        'New_Twenty_Eighty': (2, 8),
        'New_Thirty_Seventy':(3, 7),
        'New_Forty_Sixty':   (4, 6),
        'New_Fifty_Fifty':   (5, 5),
        'New_Sixty_Forty':   (6, 4),
        'New_Seventy_Thirty':(7, 3),
        'New_Eighty_Twenty': (8, 2),
        'New_Ninety_Ten':    (9, 1),
    }
PRACTICE_ROUNDS = 1