"""Entry point for the application."""

import uvicorn

uvicorn.run("app.main:create_app", host="0.0.0.0", port=8000, lifespan="on", factory=True)
