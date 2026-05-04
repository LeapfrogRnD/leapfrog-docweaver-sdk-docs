#!/bin/bash
set -e

REGION="us-east-1"
ACCOUNT_ID="654654390449"
LAMBDA_FUNCTION="docweaver_mcp_server"
API_NAME="docweaver-mcp-api"

echo "Step 1: Creating HTTP API Gateway..."
API_ID=$(aws apigatewayv2 create-api \
  --name "$API_NAME" \
  --protocol-type HTTP \
  --region "$REGION" \
  --query 'ApiId' --output text)

echo "API ID: $API_ID"

echo "Step 2: Creating Lambda integration..."
INTEGRATION_ID=$(aws apigatewayv2 create-integration \
  --api-id "$API_ID" \
  --integration-type AWS_PROXY \
  --integration-uri "arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${LAMBDA_FUNCTION}" \
  --payload-format-version 2.0 \
  --region "$REGION" \
  --query 'IntegrationId' --output text)

echo "Integration ID: $INTEGRATION_ID"

echo "Step 3: Creating catch-all route..."
aws apigatewayv2 create-route \
  --api-id "$API_ID" \
  --route-key 'ANY /{proxy+}' \
  --target "integrations/${INTEGRATION_ID}" \
  --region "$REGION"

echo "Step 4: Deploying stage..."
aws apigatewayv2 create-stage \
  --api-id "$API_ID" \
  --stage-name prod \
  --auto-deploy \
  --region "$REGION"

echo "Step 5: Allowing API Gateway to invoke Lambda..."
aws lambda add-permission \
  --function-name "$LAMBDA_FUNCTION" \
  --statement-id apigw-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" \
  --region "$REGION" 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo "MCP endpoint: https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod"
echo ""
echo "Test with:"
echo "curl -X POST 'https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/mcp' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\",\"params\":{}}'"