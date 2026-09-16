import streamlit as st
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
import os
import json

# Load API Keys
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Page Config
st.set_page_config(
    page_title="مهاري",
    page_icon="🌟",
    layout="centered"
)

# RTL CSS
st.markdown("""
<style>
    body { direction: rtl; }
    .stApp { direction: rtl; }
    h1, h2, h3, p, div { 
        text-align: right; 
        font-family: 'Cairo', sans-serif;
    }
    .stButton button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        border-radius: 15px;
        margin: 5px;
    }
    .chat-msg {
        background: #1e3a5f;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: right;
        font-size: 18px;
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Session State
if "page" not in st.session_state:
    st.session_state.page = "home"
if "child_name" not in st.session_state:
    st.session_state.child_name = ""
if "child_answers" not in st.session_state:
    st.session_state.child_answers = []
if "parent_answers" not in st.session_state:
    st.session_state.parent_answers = []
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "report" not in st.session_state:
    st.session_state.report = ""

# ==================== QUESTIONS ====================
child_questions = [
    {
        "question": "لو فضلت في البيت يوم كامل، إيه أول حاجة هتعملها؟",
        "options": ["🎮 ألعب ألعاب فيديو", "📚 أقرأ أو أرسم", "🏃 أنزل ألعب برة", "🎬 أتفرج على يوتيوب"],
        "trait": "preferred_activity"
    },
    {
        "question": "لما المدرس بيشرح حاجة جديدة، بتفهم أكتر لما...",
        "options": ["👁️ أشوف صور أو رسومات", "👂 أسمع الشرح كويس", "✋ أعمل التجربة بنفسي", "📝 أكتب وأذاكر"],
        "trait": "learning_style"
    },
    {
        "question": "لما بتذاكر، بتحب يكون...",
        "options": ["🤫 هادي ومفيش ضوضاء", "🎵 فيه موسيقى خفيفة", "👥 مع أصحاب أو أهل", "🌳 في مكان مفتوح"],
        "trait": "learning_environment"
    },
    {
        "question": "لو مش فاهم حاجة في المدرسة، بتعمل إيه؟",
        "options": ["🙋 أسأل المدرس على طول", "📖 أرجع للكتاب لوحدي", "👫 أسأل صاحبي", "🎥 أدور على فيديو يشرح"],
        "trait": "help_seeking"
    },
    {
        "question": "إيه اللي بيخليك تحس إنك تعلمت حاجة صح؟",
        "options": ["⭐ لما أعمل التمرين صح", "💬 لما أشرحها لحد تاني", "🎯 لما أستخدمها في حياتي", "📊 لما أشوف درجتي كويسة"],
        "trait": "success_indicator"
    }
]

parent_questions = [
    {
        "question": f"طفلك لما بيتعلم حاجة جديدة، بيحب أكتر...",
        "options": ["يشوف فيديو أو صور", "يسمع شرح", "يجرب بنفسه", "يقرأ ويكتب"],
        "trait": "parent_learning_obs"
    },
    {
        "question": "لما بيواجه مشكلة في الواجب، أول حاجة بيعملها...",
        "options": ["يسألك على طول", "يحاول يحلها لوحده", "يسأل أخوه أو صاحبه", "يترك الواجب لوقت تاني"],
        "trait": "parent_problem_solving"
    },
    {
        "question": "طفلك بيتذكر المعلومات أكتر لما...",
        "options": ["يشوفها مكتوبة أو مصورة", "يسمعها أكتر من مرة", "يطبقها عملياً", "يكررها بصوت عالي"],
        "trait": "parent_memory_obs"
    }
]

# ==================== GEMINI CHAT ====================
def ask_gemini(child_name, question, answer):
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    prompt = f"""أنت مهاري، مساعد ذكي ودود للأطفال.
الطفل اسمه {child_name}، عمره بين 8-12 سنة.
السؤال كان: {question}
إجابة الطفل: {answer}

اكتب رد قصير جداً (جملة أو اتنين بالعربي) يشجع الطفل ويكمله للسؤال الجاي.
لا تذكر التحليل أو النتائج. كن مرح وودود."""
    response = model.generate_content(prompt)
    return response.text

# ==================== DEEPSEEK ANALYZER ====================
def analyze_and_report(child_name, child_answers, parent_answers):
    child_data = "\n".join([f"- {q['trait']}: {a}" 
                             for q, a in zip(child_questions, child_answers)])
    parent_data = "\n".join([f"- {q['trait']}: {a}" 
                              for q, a in zip(parent_questions, parent_answers)])
    
    prompt = f"""أنت خبير تعليمي متخصص في أساليب التعلم للأطفال.

بيانات الطفل: {child_name}

إجابات الطفل:
{child_data}

ملاحظات الوالدين:
{parent_data}

اكتب تقرير تعليمي شامل باللغة العربية يتضمن:
1. **ملخص شخصية {child_name} التعليمية**
2. **أسلوب التعلم الأساسي** (مع نسبة مئوية لكل أسلوب: بصري/سمعي/حركي/قرائي)
3. **البيئة المثالية للمذاكرة**
4. **نقاط القوة**
5. **توصيات عملية للوالدين والمعلمين** (5 نقاط على الأقل)
6. **تنبيه:** هذا التقرير لأغراض تعليمية فقط وليس تشخيصاً نفسياً

اكتب التقرير بشكل احترافي وواضح."""

    completion = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=900
    )
    return completion.choices[0].message.content

# ==================== PAGES ====================

# HOME PAGE
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center; font-size:48px'>🌟 مهاري</h1>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:20px; color:#888'>كل طفل بيتعلم بطريقة مختلفة — احنا بنكتشفها</p>", 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    child_name = st.text_input("✏️ اكتب اسم الطفل:", placeholder="مثال: أحمد")
    
    if child_name:
        st.session_state.child_name = child_name
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🚀 ابدأ رحلة مهاري!", use_container_width=True):
                st.session_state.page = "child_chat"
                st.rerun()

# CHILD CHAT PAGE
elif st.session_state.page == "child_chat":
    name = st.session_state.child_name
    q_idx = st.session_state.question_index
    
    st.markdown(f"<h2>🎮 أهلاً يا {name}!</h2>", unsafe_allow_html=True)
    
    # Progress
    progress = q_idx / len(child_questions)
    st.progress(progress)
    st.caption(f"السؤال {q_idx + 1} من {len(child_questions)}")
    
    if q_idx < len(child_questions):
        current_q = child_questions[q_idx]
        
        # Show previous response if exists
        if st.session_state.child_answers:
            last_response = st.session_state.get("last_gemini_response", "")
            if last_response:
                st.markdown(f"<div class='chat-msg'>🤖 {last_response}</div>", 
                           unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-msg'>🤖 أهلاً يا {name}! أنا مهاري، صاحبك الجديد 😊 خليني أتعرف عليك أكتر!</div>", 
                       unsafe_allow_html=True)
        
        st.markdown(f"<h3>{current_q['question']}</h3>", unsafe_allow_html=True)
        
        # Buttons in 2x2 grid
        col1, col2 = st.columns(2)
        options = current_q["options"]
        
        def handle_answer(answer, question):
            st.session_state.child_answers.append(answer)
            response = ask_gemini(name, question, answer)
            st.session_state.last_gemini_response = response
            st.session_state.question_index += 1
            if st.session_state.question_index >= len(child_questions):
                st.session_state.page = "parent_chat"
                st.session_state.question_index = 0
        
        with col1:
            if st.button(options[0], key=f"opt0_{q_idx}"):
                handle_answer(options[0], current_q["question"])
                st.rerun()
            if st.button(options[2], key=f"opt2_{q_idx}"):
                handle_answer(options[2], current_q["question"])
                st.rerun()
        with col2:
            if st.button(options[1], key=f"opt1_{q_idx}"):
                handle_answer(options[1], current_q["question"])
                st.rerun()
            if st.button(options[3], key=f"opt3_{q_idx}"):
                handle_answer(options[3], current_q["question"])
                st.rerun()

# PARENT CHAT PAGE
elif st.session_state.page == "parent_chat":
    name = st.session_state.child_name
    q_idx = st.session_state.question_index
    
    st.markdown(f"<h2>👨‍👩‍👧 صفحة الوالدين</h2>", unsafe_allow_html=True)
    st.markdown(f"<p>شكراً! دلوقتي محتاجين مساعدتك عشان نكمل تقرير <b>{name}</b></p>", 
               unsafe_allow_html=True)
    
    progress = q_idx / len(parent_questions)
    st.progress(progress)
    st.caption(f"السؤال {q_idx + 1} من {len(parent_questions)}")
    
    if q_idx < len(parent_questions):
        current_q = parent_questions[q_idx]
        st.markdown(f"<h3>{current_q['question']}</h3>", unsafe_allow_html=True)
        
        for i, option in enumerate(current_q["options"]):
            if st.button(option, key=f"parent_opt{i}_{q_idx}"):
                st.session_state.parent_answers.append(option)
                st.session_state.question_index += 1
                if st.session_state.question_index >= len(parent_questions):
                    st.session_state.page = "report"
                st.rerun()

# REPORT PAGE
elif st.session_state.page == "report":
    name = st.session_state.child_name
    
    st.markdown(f"<h2>📊 تقرير {name} التعليمي</h2>", unsafe_allow_html=True)
    
    if not st.session_state.report:
        with st.spinner("🔍 مهاري بيحلل البيانات..."):
            report = analyze_and_report(
                name,
                st.session_state.child_answers,
                st.session_state.parent_answers
            )
            st.session_state.report = report
    
    st.markdown(st.session_state.report)
    
    st.balloons()
    
    # Download button
    st.download_button(
        label="📥 تحميل التقرير",
        data=st.session_state.report,
        file_name=f"تقرير_{name}.txt",
        mime="text/plain"
    )
    
    if st.button("🔄 بدء جلسة جديدة"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()