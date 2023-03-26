import enum

STARS_CHOICES = [
    (1, 'One'),
    (2, 'Two'),
    (3, 'Three'),
    (4, 'Fore'),
    (5, 'Five'),
]
LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('ua', 'Ukrainian'),
    ('fr', 'French')
]
TYPE_BOOK_CHOICES = [
    ('translated', 'Переклад'),
    ('origin', 'Авторська'),
]
STATUS_BOOK_CHOICES = [
    ('reading', 'Читаю'),
    ('favorite', 'Обране'),
    ('planned', 'У планах'),
    ('dropped', 'Кинув'),
    ('read', 'Прочитав')
]
COMMISSION_CHOICE = [
    (15, '15%',),
    (12, '12%',),
    (12, '10%',),
]
ACTION_ACCESS_CHOICES = [
    ('all', 'Усі'),
    ('admin', 'Модератори'),
    ('none', 'Ніхто'),
]
TYPE_TRANSACTION_CHOICES = [
    ('deposit', 'Поповненя'),
    ('withdrawal', 'Зняття'),
    ('earn', 'Продаж'),
    ('spend', 'Покупка'),
]

TYPE_MSG = [
    ('question', 'Питання'),
    ('answer', 'Відповідь'),

]

class TransactionType(enum.Enum):
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    EARN = 'earn'
    SPEND = 'spend'
    BUY_ADV = 'buy_adv'
    CHOICES = [
        ('deposit', 'Поповненя'),
        ('withdrawal', 'Зняття'),
        ('earn', 'Продаж'),
        ('spend', 'Покупка'),
        ('buy_adv', 'Покупка реклами'),
    ]


TYPE_NOTIFICATIONS_CHOICES = [
    ('deposit', 'Поповненя'),
    ('withdrawal', 'Зняття'),
    ('change_status_book', 'Зміна статусу книги')
]

tr_types = {
    'DEPOSIT': 'deposit',
    'WITHDRAWAL': 'withdrawal',
    'EARN': 'earn',
    'SPEND': 'spend'
}

# STATUS_BOOK_CHOICES = [
#     ('reading', 'Xитаю'),
#     ('finished', 'Прочитав'),
#     ('planed', 'У планах'),
#     ('abandoned_books', 'Кинув.'),
# ]