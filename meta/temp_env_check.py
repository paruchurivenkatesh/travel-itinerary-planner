import os
print('OPENAI_API_KEY set:', bool(os.getenv('OPENAI_API_KEY')))
print('API_BASE_URL set:', bool(os.getenv('API_BASE_URL')))
print('MODEL_NAME set:', bool(os.getenv('MODEL_NAME')))
print('HF_TOKEN set:', bool(os.getenv('HF_TOKEN')))
