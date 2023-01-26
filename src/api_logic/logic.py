import random

from fastapi import Request
from nanoid import generate


def shortener():
    """"Generate random unique string that can be used as a short url"""
    size = random.randint(5, 8)
    url = generate(size=size)
    return url


def get_client_address(request: Request) -> str:
    """Get client's addres."""

    client: str = request.client.host + ':' + \
        str(request.client.port)
    print(f'{client = }')
    return client
