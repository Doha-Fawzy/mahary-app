import google.generativeai as genai
import os
from dotenv import load_dotenv

# تحميل المفتاح
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("النماذج المتاحة لمفتاحك هي:")
# طباعة كل النماذج التي تدعم توليد النصوص
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)