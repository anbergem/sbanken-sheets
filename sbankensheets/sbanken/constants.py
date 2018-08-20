from enum import Enum


class Category(Enum):
    SPOTIFY = 'Spotify'
    TV_SUBSCRIPTION = 'TV-abonnoment'
    STIPEND_ANDREAS = 'Stipend Andreas'
    PAYMENT = 'Lønn'
    PUBLIC_TRANSPORT = 'Kollektiv'
    PARKING = 'Parkering'
    TOLL = 'Bompenger'


transaction_keywords = [
    {
        'category': Category.SPOTIFY,
        'description': 'Spotify',
    },
    {
        'category': Category.TV_SUBSCRIPTION,
        'description': 'Netflix',
    },
    {
        'category': Category.TV_SUBSCRIPTION,
        'description': 'HBO',
    },
    {
        'category': Category.TV_SUBSCRIPTION,
        'description': 'Viaplay',
    },
    {
        'category': Category.STIPEND_ANDREAS,
        'description': 'Statens lånekasse',
    },
    {
        'category': Category.PAYMENT,
        'description': 'lønn',
        'transaction_type': 'LØNN',
    },
    {
        'category': Category.PUBLIC_TRANSPORT,
        'description': 'ruter',
    },
    {
        'category': Category.PARKING,
        'description': 'easypark',
    },
    {
        'category': Category.TOLL,
        'description': 'fjellinjen',
    },
]
