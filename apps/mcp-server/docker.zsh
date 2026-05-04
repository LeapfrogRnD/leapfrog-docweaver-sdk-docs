#!/usr/bin/env zsh

# ─── Config ───────────────────────────────────────────────────────────────────
REGION="us-east-1"
AWS_ACCOUNT_ID="654654390449"
ECR_REPO="docweaver/mcp_server"
IMAGE_NAME="docweaver/mcp_server"
LAMBDA_FUNCTION="docweaver_mcp_server"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"

# ─── ECR Auth ─────────────────────────────────────────────────────────────────
ecr_login() {
  aws ecr get-login-password --region "$REGION" \
    | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
}

# ─── Build ────────────────────────────────────────────────────────────────────
build() {
  docker buildx build \
    --platform linux/amd64 \
    -t "${IMAGE_NAME}:latest" \
    --load \
    --provenance=false \
    --sbom=false \
    --no-cache \
    .
}


# ─── Tag & Push ───────────────────────────────────────────────────────────────
push() {
  docker tag "${IMAGE_NAME}:latest" "${ECR_URI}:latest"
  docker push "${ECR_URI}:latest"
}

# ─── Update Lambda ────────────────────────────────────────────────────────────
deploy() {
  aws lambda update-function-code \
    --function-name "$LAMBDA_FUNCTION" \
    --image-uri "${ECR_URI}:latest" \
    --region "$REGION"
}

# ─── Invoke Lambda ────────────────────────────────────────────────────────────
invoke() {
  aws lambda invoke \
    --function-name "$LAMBDA_FUNCTION" \
    --payload '{}' \
    --region "$REGION" \
    output.json
  cat output.json
}

# ─── Local Test ───────────────────────────────────────────────────────────────
run_local() {
  docker run --rm -p 9000:8000 --name docweaver_lambda_test \
    -e AWS_LAMBDA_RUNTIME_API="localhost:9000" \
    "${IMAGE_NAME}:latest"
}

invoke_local() {
  # MCP streamable-http endpoint
  curl -s -X POST "http://localhost:9000/mcp" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
}

invoke_local_lambda() {
  # Raw Lambda runtime invocation endpoint (only available with Lambda base image)
  curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
}

logs_local() {
  docker logs --tail 100 docweaver_lambda_test
}

test_local_mcp() {
  docker rm -f docweaver_lambda_test >/dev/null 2>&1 || true
  docker run -d -p 9000:8000 --name docweaver_lambda_test "${IMAGE_NAME}:latest" >/dev/null
  sleep 2
  echo "Invoking local Lambda runtime endpoint..."
  curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
  echo
  echo "--- logs ---"
  docker logs --tail 60 docweaver_lambda_test
}

# ─── ECR Image Management ─────────────────────────────────────────────────────
list_images() {
  aws ecr describe-images --repository-name "$ECR_REPO" --region "$REGION"
}

delete_image() {
  # Usage: delete_image <digest>
  aws ecr batch-delete-image \
    --repository-name "$ECR_REPO" \
    --region "$REGION" \
    --image-ids imageDigest="$1"
}

delete_all_images() {
  aws ecr list-images \
    --repository-name "$ECR_REPO" \
    --region "$REGION" \
    --query 'imageIds[*]' \
    --output json > /tmp/ecr_image_ids.json
  aws ecr batch-delete-image \
    --repository-name "$ECR_REPO" \
    --region "$REGION" \
    --image-ids file:///tmp/ecr_image_ids.json
}

# ─── Full Deploy Pipeline ─────────────────────────────────────────────────────
all() {
  ecr_login && build && push && deploy
  #  && invoke
}

# ─── Lambda Env Vars ──────────────────────────────────────────────────────────
set_env() {
  aws lambda update-function-configuration \
    --function-name "$LAMBDA_FUNCTION" \
    --region "$REGION" \
    --environment "Variables={$1}"
}

clear_env() {
  aws lambda update-function-configuration \
    --function-name "$LAMBDA_FUNCTION" \
    --region "$REGION" \
    --environment "Variables={}"
}

# ─── CloudWatch Logs ──────────────────────────────────────────────────────────
logs_lambda() {
  aws logs tail "/aws/lambda/${LAMBDA_FUNCTION}" --region "$REGION" --follow
}

# ─── Usage ────────────────────────────────────────────────────────────────────
usage() {
  echo "Available functions:"
  echo "  ecr_login       - Authenticate Docker with ECR"
  echo "  build           - Build Docker image (linux/amd64)"
  echo "  push            - Tag and push image to ECR"
  echo "  deploy          - Update Lambda with latest ECR image"
  echo "  invoke          - Invoke Lambda function and show output"
  echo "  run_local       - Run container locally on port 9000"
  echo "  invoke_local    - Invoke local container"
  echo "  logs_local      - Tail local container logs"
  echo "  test_local_mcp  - Start container, invoke it once, and print logs"
  echo "  list_images     - List ECR images"
  echo "  delete_image    - Delete ECR image by digest: delete_image <sha256:...>"
  echo "  delete_all_images - Delete all ECR images"
  echo "  set_env         - Set Lambda env vars: set_env 'KEY1=VAL1,KEY2=VAL2'"
  echo "  clear_env       - Clear all Lambda env vars"
  echo "  logs_lambda     - Tail CloudWatch Lambda logs"
  echo "  all             - Full pipeline: login > build > push > deploy > invoke"
}

# ─── Entrypoint ───────────────────────────────────────────────────────────────
# Source this file: source docker.zsh
# Then call any function directly, e.g.: all
