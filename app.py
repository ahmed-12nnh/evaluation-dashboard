import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date

# -------------------------------------------------------------------
#  Database Setup & Models
# -------------------------------------------------------------------
Base = declarative_base()

class Applicant(Base):
    __tablename__ = 'applicants'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    dob = Column(String(50)) # Using string for simplicity, or Date
    education = Column(String(255))
    current_task = Column(String(255))
    address = Column(String(255))
    
    evaluation = relationship("Evaluation", back_populates="applicant", uselist=False)

class Evaluation(Base):
    __tablename__ = 'evaluations'
    id = Column(Integer, primary_key=True)
    applicant_id = Column(Integer, ForeignKey('applicants.id'))
    
    # 1 to 10 criteria
    deep_current = Column(Integer)
    deep_political = Column(Integer)
    general_skills = Column(Integer)
    deep_media = Column(Integer)
    ideological_security = Column(Integer)
    
    notes = Column(Text)
    
    applicant = relationship("Applicant", back_populates="evaluation")

# Initialize DB (Use Supabase if URL is in secrets, else local SQLite)
if "DATABASE_URL" in st.secrets:
    db_url = st.secrets["DATABASE_URL"]
else:
    db_url = 'sqlite:///dashboard.db'

engine = create_engine(db_url, echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def seed_data():
    session = SessionLocal()
    if session.query(Applicant).count() == 0:
        a1 = Applicant(
            full_name="أحمد محمد علي",
            dob="1990-05-12",
            education="بكالوريوس هندسة حاسوب",
            current_task="مهندس برمجيات",
            address="بغداد، الكرادة"
        )
        a2 = Applicant(
            full_name="فاطمة حسن رضاء",
            dob="1995-10-22",
            education="ماجستير علوم سياسية",
            current_task="باحثة وأكاديمية",
            address="النجف الأشرف، حي الجامعة"
        )
        session.add(a1)
        session.add(a2)
        session.commit()
    session.close()

seed_data()

# -------------------------------------------------------------------
#  Streamlit UI
# -------------------------------------------------------------------

st.set_page_config(page_title="لوحة تحكم لجنة التقييم", layout="wide", page_icon="📝")

# CSS Styling to make it look professional
st.markdown("""
<style>
    .cv-card {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .cv-header {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .cv-item {
        margin-bottom: 10px;
        font-size: 1.1rem;
    }
    .cv-label {
        font-weight: bold;
        color: #34495e;
    }
    /* Change font for arabic support */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Main Title
st.title("لوحة تحكم لجنة التقييم 📊")

session = SessionLocal()
applicants = session.query(Applicant).all()

# Session state to handle navigation
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'cv'
if 'selected_applicant_id' not in st.session_state:
    if applicants:
        st.session_state.selected_applicant_id = applicants[0].id
    else:
        st.session_state.selected_applicant_id = None

# Sidebar
st.sidebar.header("قائمة المتقدمين 👥")

# Create a selectbox or list in sidebar
applicant_dict = {a.id: a.full_name for a in applicants}
if applicants:
    # Find index of currently selected applicant
    try:
        current_index = list(applicant_dict.keys()).index(st.session_state.selected_applicant_id)
    except ValueError:
        current_index = 0

    selected_id = st.sidebar.selectbox(
        "اختر متقدم للمراجعة:",
        options=list(applicant_dict.keys()),
        format_func=lambda x: applicant_dict[x],
        index=current_index
    )
    
    # If selection changes in sidebar, reset to CV view
    if selected_id != st.session_state.selected_applicant_id:
        st.session_state.selected_applicant_id = selected_id
        st.session_state.view_mode = 'cv'

# Main Area
if st.session_state.selected_applicant_id:
    applicant = session.query(Applicant).filter(Applicant.id == st.session_state.selected_applicant_id).first()
    
    if st.session_state.view_mode == 'cv':
        st.header("السيرة الذاتية للمتقدم")
        
        # Display CV
        st.markdown(f"""
        <div class="cv-card">
            <h3 class="cv-header">👤 {applicant.full_name}</h3>
            <div class="cv-item"><span class="cv-label">📅 تاريخ الميلاد:</span> {applicant.dob}</div>
            <div class="cv-item"><span class="cv-label">🎓 التحصيل الدراسي:</span> {applicant.education}</div>
            <div class="cv-item"><span class="cv-label">💼 المهمة الحالية:</span> {applicant.current_task}</div>
            <div class="cv-item"><span class="cv-label">📍 عنوان السكن:</span> {applicant.address}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 الانتقال لتقييم المتقدم", use_container_width=True, type="primary"):
                st.session_state.view_mode = 'evaluate'
                st.rerun()
                
    elif st.session_state.view_mode == 'evaluate':
        st.header("استمارة التقييم 📝")
        
        st.info(f"**جاري تقييم المتقدم:** {applicant.full_name}", icon="ℹ️")
        
        # Check if already evaluated
        existing_eval = session.query(Evaluation).filter(Evaluation.applicant_id == applicant.id).first()
        
        with st.form("evaluation_form"):
            st.subheader("محاور التقييم (من 1 إلى 10)")
            
            # Default values
            d1 = existing_eval.deep_current if existing_eval and existing_eval.deep_current else 5
            d2 = existing_eval.deep_political if existing_eval and existing_eval.deep_political else 5
            d3 = existing_eval.general_skills if existing_eval and existing_eval.general_skills else 5
            d4 = existing_eval.deep_media if existing_eval and existing_eval.deep_media else 5
            d5 = existing_eval.ideological_security if existing_eval and existing_eval.ideological_security else 5
            notes_val = existing_eval.notes if existing_eval and existing_eval.notes else ""
            
            val1 = st.slider("محور العمق التياري", 1, 10, d1)
            val2 = st.slider("محور العمق السياسي", 1, 10, d2)
            val3 = st.slider("محور المهارات العامة", 1, 10, d3)
            val4 = st.slider("محور العمق الإعلامي", 1, 10, d4)
            val5 = st.slider("المحور العقائدي والأمني", 1, 10, d5)
            
            st.subheader("الملاحظات النهائية")
            final_notes = st.text_area("أضف أي ملاحظات إضافية عن المتقدم هنا...", value=notes_val)
            
            submitted = st.form_submit_button("✅ حفظ التقييم", type="primary", use_container_width=True)
            
            if submitted:
                if existing_eval:
                    existing_eval.deep_current = val1
                    existing_eval.deep_political = val2
                    existing_eval.general_skills = val3
                    existing_eval.deep_media = val4
                    existing_eval.ideological_security = val5
                    existing_eval.notes = final_notes
                else:
                    new_eval = Evaluation(
                        applicant_id=applicant.id,
                        deep_current=val1,
                        deep_political=val2,
                        general_skills=val3,
                        deep_media=val4,
                        ideological_security=val5,
                        notes=final_notes
                    )
                    session.add(new_eval)
                
                session.commit()
                st.success("تم حفظ التقييم بنجاح!")
                # Add a small button to return to CV view
        
        if st.button("⬅️ العودة إلى السيرة الذاتية"):
            st.session_state.view_mode = 'cv'
            st.rerun()

else:
    st.info("لا يوجد متقدمين في قاعدة البيانات حالياً.")

session.close()
