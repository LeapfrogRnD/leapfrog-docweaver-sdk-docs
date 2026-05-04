FROM public.ecr.aws/lambda/python:3.11

WORKDIR /var/task

COPY pyproject.toml ./
COPY leap_docweaver_mcp ./leap_docweaver_mcp
COPY server.py ./
COPY lambda_handler.py ./

RUN pip install --no-cache-dir .

ENV PORT=8000
ENV DEFAULT_PORT=8000
ENV MCP_AUTH_ENABLED=true
ENV MCP_AUTH_MODE=jwt
ENV MCP_REQUIRED_SCOPES=openid,profile,email,mcp:read,mcp:write



CMD ["lambda_handler.handler"]
