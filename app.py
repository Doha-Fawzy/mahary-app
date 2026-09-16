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
child_questions = child_questions = [
    {
        "question": "لما المدرس بيشرح درس جديد، إيه اللي بيساعدك تفهم أكتر؟",
        "options": [
            "📊 لما بيرسم على السبورة أو بيوري صور",
            "👂 لما بيشرح بصوته وأسمعه كويس",
            "✋ لما أجرب بنفسي أو أعمل حاجة بإيدي",
            "📖 لما أقرأ في الكتاب وأكتب ملاحظات"
        ],
        "trait": "learning_modality"
    },
    {
        "question": "لما بتحل واجب وتلاقي سؤال صعب مش فاهمه، بتعمل إيه؟",
        "options": [
            "🙋 بسأل أمي أو أبويا على طول",
            "🤔 بحاول أفكر فيه لوحدي الأول",
            "📱 بدور على فيديو يشرحه",
            "😶 بسيبه وأكمل اللي بعده"
        ],
        "trait": "help_seeking_behavior"
    },
    {
        "question": "لما بتذاكر وحاجة تشتت تركيزك، بتعمل إيه؟",
        "options": [
            "😤 بزعل وأقوم من المذاكرة",
            "🎧 بحط سماعات وأكمل",
            "🔄 بخد راحة صغيرة وأرجع",
            "📍 بحاول أركز تاني من غير ما أوقف"
        ],
        "trait": "self_regulation"
    },
    {
        "question": "لما تتعلم حاجة جديدة وتحس إنك فهمتها، بتعمل إيه؟",
        "options": [
            "💬 بشرحها لصاحبي أو أخويا",
            "📝 بكتبها في ورقة بأسلوبي أنا",
            "🎯 بحل تمارين عليها على طول",
            "😊 بحس بفرحة وأكمل الموضوع الجاي"
        ],
        "trait": "comprehension_confirmation"
    },
    {
        "question": "لو قدرت تختار، تذاكر إزاي؟",
        "options": [
            "🤫 لوحدي في أوضة هادية",
            "👥 مع صاحب أو أخ أو أخت",
            "🎵 مع موسيقى خفيفة في الخلفية",
            "🌳 في مكان مفتوح زي الجنينة أو الشرفة"
        ],
        "trait": "learning_environment"
    },
    {
        "question": "لما بتحفظ معلومة مهمة، بتعمل إيه عشان متنساش؟",
        "options": [
            "🖼️ بعمل رسمة أو جدول في دماغي",
            "🔊 برددها بصوت عالي أكتر من مرة",
            "✍️ بكتبها أكتر من مرة",
            "🎬 بربطها بحاجة حصلت معايا في حياتي"
        ],
        "trait": "memory_strategy"
    },
    {
        "question": "لما المدرس يقول: 'مين عارف الإجابة؟' وانت عارفها، بتعمل إيه؟",
        "options": [
            "🙋 برفع إيدي على طول وأجاوب",
            "😶 بستنى حد تاني يجاوب الأول",
            "😅 بتمنى ميسألنيش، خايف أغلط",
            "📝 بكتب الإجابة في ورقتي بس"
        ],
        "trait": "classroom_participation"
    },
    {
        "question": "إيه اللي بيخليك تحب مادة أكتر من التانية؟",
        "options": [
            "🎨 لما فيها رسم أو ألوان أو صور",
            "🗣️ لما المدرس بيحكي قصص وأمثلة",
            "🔬 لما فيها تجارب أو أنشطة عملية",
            "📚 لما الكتاب واضح ومرتب وسهل"
        ],
        "trait": "subject_engagement"
    }
]

parent_questions_open = [
    {
        "question": "صفيلي طفلك وهو بيذاكر في البيت — إيه اللي بيحصل عادةً؟",
        "hint": "مثلاً: بيحتاج مساعدة؟ بيذاكر لوحده؟ بيزعل بسرعة؟",
        "trait": "homework_behavior"
    },
    {
        "question": "لما طفلك بيواجه حاجة صعبة ومش فاهمها، بيعمل إيه تحديداً؟",
        "hint": "مثلاً: بيسألك؟ بيزعل ويوقف؟ بيحاول لوحده؟ بيدور على فيديو؟",
        "trait": "problem_solving"
    },
    {
        "question": "إيه المواقف اللي بتلاحظ فيها إن طفلك بيتعلم بسرعة وبفرحة؟",
        "hint": "فكري في مواد معينة، أنشطة، أو مواقف في البيت",
        "trait": "peak_learning"
    },
    {
        "question": "إيه اللي بيعمله طفلك لما حد يشرحله حاجة جديدة؟",
        "hint": "مثلاً: بيسأل أسئلة؟ بيسمع بصمت؟ بيجرب على طول؟ بيحتاج يتكرر؟",
        "trait": "receiving_info"
    },
    {
        "question": "في رأيك إيه أكبر تحدي بيواجه طفلك في المذاكرة دلوقتي؟",
        "hint": "ممكن تكون صعوبة في التركيز، الخجل، الخوف من الغلط، أو حاجة تانية",
        "trait": "main_challenge"
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

# ==================== Qwen ANALYZER ====================
def analyze_and_report(child_name, child_answers, parent_answers):
    child_data = "\n".join([f"- {q['trait']}: {a}" 
                             for q, a in zip(child_questions, child_answers)])
    
    # Parent answers now have more detail
    parent_data = ""
    if st.session_state.get("parent_collected"):
        parent_data = "\n".join([
            f"- {item['trait']}:\n  السؤال: {item['question']}\n  الإجابة: {item['answer']}"
            for item in st.session_state.parent_collected
        ])
    else:
        parent_data = "\n".join([f"- ملاحظة {i+1}: {a}" 
                                  for i, a in enumerate(parent_answers)])
    
    prompt = f"""أنت خبير تعليمي متخصص في أساليب التعلم للأطفال.

بيانات الطفل: {child_name}

إجابات الطفل (من خلال الأنشطة):
{child_data}

ملاحظات الوالدين التفصيلية:
{parent_data}

اكتب تقرير تعليمي شامل باللغة العربية يتضمن:
1. **ملخص شخصية {child_name} التعليمية**
2. **أسلوب التعلم الأساسي** (مع نسبة مئوية: بصري/سمعي/حركي/قرائي)
3. **نقاط القوة التي ظهرت**
4. **التحديات المحتملة**
5. **البيئة المثالية للمذاكرة**
6. **توصيات عملية للوالدين** (5 نقاط)
7. **توصيات للمعلمين** (3 نقاط)
8. **تنبيه:** هذا التقرير لأغراض تعليمية فقط وليس تشخيصاً نفسياً أو طبياً

اكتب بأسلوب احترافي ودافئ."""

    completion = groq_client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=800
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
    
    st.markdown(f"<h2>👨‍👩‍👧 صفحة الوالدين</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:#1a3a1a; padding:15px; border-radius:10px; margin-bottom:20px'>
    <p style='color:#90EE90; font-size:16px'>
    أنتم اللي بتعرفوا <b>{name}</b> أكتر من أي حد 💚<br>
    إجاباتكم هتساعدنا نعمل تقرير دقيق وحقيقي ليه
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize parent chat history
    if "parent_chat_history" not in st.session_state:
        st.session_state.parent_chat_history = []
    if "parent_q_index" not in st.session_state:
        st.session_state.parent_q_index = 0
    if "parent_collected" not in st.session_state:
        st.session_state.parent_collected = []

    q_idx = st.session_state.parent_q_index
    
    # Progress
    st.progress(q_idx / len(parent_questions_open))
    st.caption(f"السؤال {q_idx + 1} من {len(parent_questions_open)}")
    
    # Show chat history
    for msg in st.session_state.parent_chat_history:
        if msg["role"] == "assistant":
            st.markdown(f"<div class='chat-msg'>🤖 {msg['content']}</div>", 
                       unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#2d4a2d; padding:12px; border-radius:10px; margin:8px 0; text-align:right'>👤 {msg['content']}</div>", 
                       unsafe_allow_html=True)
    
    # Show current question if not done
    if q_idx < len(parent_questions_open):
        current_q = parent_questions_open[q_idx]
        
        # Show question if first time
        if not st.session_state.parent_chat_history or \
           st.session_state.parent_chat_history[-1]["role"] == "user":
            st.markdown(f"<div class='chat-msg'>🤖 {current_q['question']}<br><small style='color:#aaa'>💡 {current_q['hint']}</small></div>", 
                       unsafe_allow_html=True)
        
        # Text input for parent
        parent_input = st.text_area(
            "إجابتك:",
            placeholder="اكتب هنا بحرية...",
            height=100,
            key=f"parent_input_{q_idx}"
        )
        
        col1, col2 = st.columns([3,1])
        with col2:
            if st.button("إرسال ➤", use_container_width=True):
                if parent_input.strip():
                    # Save answer
                    st.session_state.parent_collected.append({
                        "trait": current_q["trait"],
                        "question": current_q["question"],
                        "answer": parent_input
                    })
                    
                    # Add to chat history
                    st.session_state.parent_chat_history.append({
                        "role": "user", 
                        "content": parent_input
                    })
                    
                    # Get Gemini response
                    model = genai.GenerativeModel('gemini-3.5-flash-lite')
                    next_q_idx = q_idx + 1
                    
                    if next_q_idx < len(parent_questions_open):
                        next_q = parent_questions_open[next_q_idx]
                        prompt = f"""أنت مهاري، مساعد تعليمي ذكي.
الوالد يخبرك عن طفله {name}.
سؤالك كان: {current_q['question']}
إجابة الوالد: {parent_input}

اكتب رد قصير (جملة واحدة فقط) تشكر فيه الوالد وتنتقل للسؤال التالي.
ثم اسأل هذا السؤال: {next_q['question']}
التلميح: {next_q['hint']}

اكتب بالعربي فقط، بأسلوب دافئ وطبيعي."""
                    else:
                        prompt = f"""أنت مهاري، مساعد تعليمي ذكي.
الوالد أجاب على آخر سؤال عن طفله {name}.
إجابته: {parent_input}

اكتب رسالة شكر قصيرة (جملتين) وأخبره إن مهاري دلوقتي جاهز يحلل المعلومات ويعمل التقرير.
اكتب بالعربي فقط، بأسلوب دافئ."""
                    
                    response = model.generate_content(prompt)
                    
                    st.session_state.parent_chat_history.append({
                        "role": "assistant",
                        "content": response.text
                    })
                    
                    st.session_state.parent_q_index += 1
                    
                    if st.session_state.parent_q_index >= len(parent_questions_open):
                        # Convert collected answers to parent_answers format
                        st.session_state.parent_answers = [
                            item["answer"] for item in st.session_state.parent_collected
                        ]
                        st.session_state.page = "report"
                    
                    st.rerun()
                else:
                    st.warning("من فضلك اكتب إجابتك الأول!")

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