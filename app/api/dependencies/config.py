from fastapi import Request

from app.config.settings import Settings


def get_config(request: Request) -> Settings:
    return request.app.state.config
