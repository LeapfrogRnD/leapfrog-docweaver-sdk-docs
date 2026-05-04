from app.logger import logger


class BaseService:
    def __init__(self) -> None:
        self.logger = logger
