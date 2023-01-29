import logging

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, ORJSONResponse

from api.v1 import base
from core.config import app_settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title=app_settings.title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.middleware('http')
async def validate_ip(request: Request, call_next):
    """Check if the client's IP is in the black list"""

    client = str(request.client.host)

    if client in app_settings.blacklisted_ips:
        logger.error(
            'Client "%(client)s" is not allowed to access this resource.',
            {'client': client}
        )

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content='Access Denied'
        )

    return await call_next(request)


app.include_router(base.api_router, prefix='/api/v1')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.host,
        port=app_settings.port,
        reload=True
    )
