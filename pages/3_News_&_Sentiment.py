import streamlit as st
from services import NewsService, NewsController
from components import render_news_sentiment_module, render_section_loader, render_error_banner
from utils.session_cache import (
    get_cached_news, set_cached_news, get_cached_sentiment, set_cached_sentiment,
    get_news_loading_status, set_news_loading_status, get_news_error, set_news_error
)
from utils.error_handler import log_and_map_exception

st.set_page_config(page_title="News & Sentiment | FinSight", layout="wide")

if not st.session_state.get("current_company"):
    st.warning("⚠️ Please select a company from the main **Dashboard** first.")
else:
    profile = st.session_state.current_company
    st.title(f"Market News & Sentiment Analysis — {profile.ticker}")

    cached_news = get_cached_news()
    cached_sentiment = get_cached_sentiment()
    
    if get_news_loading_status():
        render_section_loader("Gathering News Coverage & Sentiment", height=300)
        try:
            articles, sentiment = NewsController(NewsService()).get_news_with_sentiment(profile.ticker)
            set_cached_news(articles)
            set_cached_sentiment(sentiment)
        except Exception as e:
            set_news_error(log_and_map_exception(e, "news"))
        finally:
            set_news_loading_status(False)
            st.rerun()
    elif get_news_error():
        render_error_banner(get_news_error())
    elif cached_news is not None and cached_sentiment is not None:
        render_news_sentiment_module(cached_news, cached_sentiment)
    else:
        set_news_loading_status(True)
        st.rerun()