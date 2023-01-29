from fastapi import HTTPException, status


def url_not_found_error():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Url not found.'
    )


def url_gone_error():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail='URL was deleted from the database.'
    )


def internal_server_error():
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Internal Server Error'
    )
