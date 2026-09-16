import os
from groq import Groq
from dotenv import load_dotenv

# تحميل المفاتيح من ملف .env
load_dotenv()

print("="*50)
print("🔍 جاري فحص نماذج Groq المتاحة...")
print("="*50)

try:
    # الاتصال بخوادم Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # جلب قائمة النماذج
    models = client.models.list()
    
    # طباعة المعرفات (IDs)
    for m in models.data:
        print(f" ✅ {m.id}")
        
except Exception as e:
    print(f" ❌ حدث خطأ: {e}")
    
print("="*50)