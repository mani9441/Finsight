import streamlit as st
from components.sidebar import render_custom_sidebar
from core.constants import APP_TITLE
from pathlib import Path

LOGO_PATH = Path("assets/logo.png")


def hide_streamlit_header_footer():
    """Hides the top-right Deploy button, 3-dot menu, and bottom Streamlit footer."""
    hide_css = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployButton {display:none;}
        </style>
    """
    st.markdown(hide_css, unsafe_allow_html=True)



# Page config
st.set_page_config(
    page_title=f"{APP_TITLE}",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide Streamlit's default header elements (Deploy button & 3 dots)
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Declare Page Routes
dashboard = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    default=True,
)

price = st.Page(
    "pages/1_Price_Chart.py",
    title="Price Chart",
)

ratios = st.Page(
    "pages/2_Financial_Ratios.py",
    title="Financial Ratios",
)

risk = st.Page(
    "pages/4_Risk_Assessment.py",
    title="Risk Assessment",
)

news = st.Page(
    "pages/3_News_&_Sentiment.py",
    title="News & Sentiment",
)

summary = st.Page(
    "pages/5_AI_Summary.py",
    title="AI Summary",
)

# 1. Initialize navigation with hidden native UI
pg = st.navigation(
    [dashboard, price, ratios, risk, news, summary],
    position="hidden"
)

# 2. Render sidebar layout in exact custom order
render_custom_sidebar(
    dashboard_page=dashboard,
    price_page=price,
    ratios_page=ratios,
    risk_page=risk,
    news_page=news,
    summary_page=summary
)

# 3. Run current active page
pg.run()