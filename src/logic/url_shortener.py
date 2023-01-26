import random

from nanoid import generate


def shortener():
    """"Generate random unique string that can be used as a short url"""
    size = random.randint(5, 8)
    url = generate(size=size)
    return url
