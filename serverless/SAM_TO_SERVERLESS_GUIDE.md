# Direct SAM to Serverless Framework Migration

This document outlines the steps to directly migrate your existing AWS SAM template to the Serverless Framework.

## Steps to Implement

1. **Replace your current serverless.yml**:
   ```powershell
   Move-Item -Path "C:\Users\Aryama Vinay Murthy\Desktop\mind_map_explorer\serverless\serverless.yml.direct" -Destination "C:\Users\Aryama Vinay Murthy\Desktop\mind_map_explorer\serverless\serverless.yml" -Force
   ```

2. **Fix the Lambda handler that's timing out**:
   ```powershell
   Move-Item -Path "C:\Users\Aryama Vinay Murthy\Desktop\mind_map_explorer\lambda_handlers\spaces_list_handler.py.serverless" -Destination "C:\Users\Aryama Vinay Murthy\Desktop\mind_map_explorer\lambda_handlers\spaces_list_handler.py" -Force
   ```

3. **Start the Serverless Offline server**:
   ```powershell
   cd "C:\Users\Aryama Vinay Murthy\Desktop\mind_map_explorer\serverless"
   npm run start
   ```

4. **Test the local API**:
   ```powershell
   Invoke-RestMethod -Method Get -Uri "http://localhost:3000/spaces"
   ```

5. **Deploy to AWS when ready**:
   ```powershell
   cd "C:\Users\Aryama Vinay Murthy\Desktop\mind_map_explorer\serverless"
   $env:TIMESTAMP = Get-Random
   npx serverless deploy --stage dev --verbose
   ```

## Key Differences Between SAM and Serverless Framework

1. **CloudFormation Syntax**: 
   - SAM uses `!Ref` and `!GetAtt` for references
   - Serverless Framework uses `Ref:` and `Fn::GetAtt:` instead

2. **API Gateway Integration**:
   - SAM uses the `AWS::Serverless::Api` resource
   - Serverless Framework configures API Gateway via `http` events in functions

3. **Environment Variables**:
   - Serverless Framework uses `${self:service}` and `${self:provider.stage}` for references

4. **Local Development**:
   - Serverless Framework uses the serverless-offline plugin
   - SAM uses SAM CLI for local development

## Notes

- The direct conversion maintains the same architecture and functionality as your original SAM template
- We've added environment variable detection for local development in the handler
- The serverless-offline plugin provides local API Gateway and Lambda emulation
