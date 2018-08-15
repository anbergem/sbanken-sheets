from enum import Enum


class Category(Enum):
    SUBSCRIPTION = 'Abonnoment'


transaction_keywords = [
    {
        'category': Category.SUBSCRIPTION,
        'description': 'Spotify'
    },
    {
        'category': Category.SUBSCRIPTION,
        'description': 'HBO'
    },
    {
        'category': Category.SUBSCRIPTION,
        'description': 'Viaplay'
    },
]