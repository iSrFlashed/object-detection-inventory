import streamlit as st
from app.Login.login_logic import authenticate_user

from app.Main.main_ui import show_sidebar, show_content  

st.set_page_config(page_title="Image Classifier", page_icon="📷", layout="wide")


st.markdown(
    """
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
        }
        
        .css-1d391kg {
            background-color: #121212 !important;
        }

        .login-box {
            background-color: #1e1e1e;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
            text-align: center;
        }

        input {
            background-color: #2a2a2a !important;
            color: #ffffff !important;
        }

        .stButton>button {
            width: 100%;
            background-color: #4B89DC !important;
            color: white !important;
            border-radius: 5px;
        }

        .image-container {
            display: flex;
            justify-content: center;
            align-items: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def show_login():
    st.sidebar.markdown("## 🏠 Navigation")
    st.sidebar.markdown("🔑 **Login**", unsafe_allow_html=True)


    col1, col2 ,col3= st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='color: #4B89DC;'>🔐 Log In</h2>", unsafe_allow_html=True)

        username = st.text_input("👤 User", key="username_input_unique")
        password = st.text_input("🔑 Password", type="password", key="password_input_unique")

        if st.button("🚀 Login"):
            token = authenticate_user(username, password)
            if token:
                st.session_state.logged_in = True
                st.session_state.token = token
                st.success("✅ Successful access")
                st.rerun()
            else:
                st.error("❌ Invalid User and/or Password")

        st.markdown("</div>", unsafe_allow_html=True)


    with col3:
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2920/2920329.png", width=200)
        st.markdown("</div>", unsafe_allow_html=True)


if "logged_in" not in st.session_state or not st.session_state.logged_in:
    show_login()
else:
    menu = show_sidebar()  
    show_content(menu) 
