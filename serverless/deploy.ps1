# PowerShell Deployment Script for Mind Map Explorer

Write-Host "=== Mind Map Explorer Serverless Deployment ===" -ForegroundColor Green

# Set timestamp for unique S3 bucket name
$env:TIMESTAMP = Get-Random

Write-Host "Using timestamp: $env:TIMESTAMP" -ForegroundColor Yellow

# Get the deployment stage
$STAGE = if ($args[0]) { $args[0] } else { "dev" }
Write-Host "Deploying to stage: $STAGE" -ForegroundColor Yellow

# Deploy the application
Write-Host "Deploying Serverless application..." -ForegroundColor Green
npx serverless deploy --stage $STAGE --verbose

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Use 'npm run info' to see the deployed endpoints and resources" -ForegroundColor Green
