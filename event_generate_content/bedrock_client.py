import boto3
import os
import json
import logging

class BedrockClient:
    def __init__(self, model_id=None):
        self.model_id = model_id or os.environ.get('BEDROCK_MODEL_ID', 'amazon.nova-micro-v1:0')
        self.client = boto3.client('bedrock-runtime')
        
    def generate_content(self, prompt, temperature=0.7, max_tokens=512):
        try:
            # Prepare request body based on model type
            if "claude" in self.model_id.lower():
                body = {
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "temperature": temperature,
                    "max_tokens_to_sample": max_tokens
                }
            elif "titan" in self.model_id.lower():
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "temperature": temperature,
                        "maxTokenCount": max_tokens
                    }
                }
            elif "nova" in self.model_id.lower():
                body = {
                    "inferenceConfig": {
                        "max_new_tokens": max_tokens
                    },
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"text": prompt}
                            ]
                        }
                    ]
                }
            else:
                # Generic fallback
                body = {
                    "prompt": prompt,
                    "temperature": temperature,
                    "maxTokens": max_tokens
                }
                
            # Convert to JSON string for API call
            body_json = json.dumps(body)

            # Call Bedrock
            response = self.client.invoke_model(
                 modelId=self.model_id,
                 contentType="application/json",
                 accept="application/json",
                body=body_json
             )

            # Parse response body
            response_body = json.loads(response['body'].read().decode('utf-8'))
            logging.info(f"Bedrock raw response: {response_body}")
            # Extract the generated text based on model type
            if "claude" in self.model_id.lower():
                result = response_body.get('completion')
            elif "titan" in self.model_id.lower():
                result = response_body.get('results', [{}])[0].get('outputText', '')
            elif "nova" in self.model_id.lower():
                results = response_body.get('output', {}).get('message', {}).get('content')
                if not results:
                    # fallback to old logic if structure is different
                    results = response_body.get('results')
                    if results and isinstance(results, list):
                        output = results[0].get('output', {})
                        text = output.get('text', '')
                    else:
                        text = ''
                else:
                    # nova returns a list of dicts with 'text' key
                    text = results[0].get('text', '') if isinstance(results, list) and results else ''
                # Remove code block markers if present
                if text.startswith('```html'):
                    text = text[len('```html'):].strip()
                elif text.startswith('```'):
                    text = text[len('```'):].strip()
                if text.endswith('```'):
                    text = text[:-3].strip()
                result = text
                logging.info(f"Extracted result for nova: {result}")
            else:
                # Generic fallback
                result = response_body.get('generated_text', str(response_body))
            
            # Format as HTML content
            html_content = f"""
            <div class="ai-generated-content">
                {result}
            </div>
            """
            
            return html_content
        except Exception as e:
            logging.error(f"Bedrock content generation failed: {e}")
            raise
