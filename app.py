import streamlit as st
import plotly.express as px
from data_engine import fetch_creator_full_audit
from analytics import analyze_brand_fit

st.set_page_config(page_title="CREATOR INTEL PRO", layout="wide")

# UI THEME
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    .creator-header { display: flex; align-items: center; gap: 25px; background: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #8b5cf6; }
    .insight-card { background: rgba(139, 92, 246, 0.1); border-left: 5px solid #8b5cf6; padding: 15px; border-radius: 8px; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ CREATOR INTELLIGENCE AUDIT DASHBOARD")
url = st.text_input("Enter YouTube Profile/Channel URL")

if url:
    with st.spinner("Executing Full API Scan..."):
        data = fetch_creator_full_audit(url)
        if data:
            intel = analyze_brand_fit(data)

            # --- SECTION 1: CREATOR ID ---
            st.markdown(f"""
                <div class="creator-header">
                    <img src="{data['logo']}" style="width: 100px; height: 100px; border-radius: 50%;">
                    <div>
                        <h1 style='margin:0;'>{data['name']}</h1>
                        <p style='color: #8b5cf6; font-size: 1.2rem; margin:0;'>{data['subs']:,} Subscribers • {data['video_count']} Videos</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.write("##")

            # --- SECTION 2: API METRICS ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("AVG VIEWS (Last 30)", f"{data['avg_views']:,}")
            m2.metric("ENGAGEMENT RATE", f"{intel['er']}%")
            m3.metric("BOT RISK SCORE", f"{intel['bot_risk']}%")
            m4.metric("SENTIMENT SCORE", f"{intel['sentiment_score']}")

            st.divider()

            # --- SECTION 3: CHARTS & VERDICT ---
            col_left, col_right = st.columns([2, 1])

            with col_left:
                st.subheader("📊 Recent Performance Audit")
                fig_perf = px.bar(data['recent_performance'], x="Views", y="Title", orientation='h', color_discrete_sequence=['#8b5cf6'])
                fig_perf.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=400)
                st.plotly_chart(fig_perf, use_container_width=True)

            with col_right:
                st.subheader("🛡️ Campaign Verdict")
                if intel['status'] == "Success": st.success(intel['verdict'])
                else: st.warning(intel['verdict'])
                
                st.write("---")
                st.write("**Engagement Breakdown:**")
                st.write(f"👍 Avg Likes: {data['avg_likes']:,}")
                st.write(f"💬 Avg Comments: {data['avg_comments']:,}")

            st.divider()

            # --- SECTION 4: SENTIMENT TREND + INTERPRETATION ---
            st.subheader("🧠 Audience Sentiment Trend")
            fig_sent = px.area(y=intel['sentiment_list'], title="Interaction Polarity (Recent 500 Comments)")
            fig_sent.update_traces(line_color='#8b5cf6', fillcolor='rgba(139, 92, 246, 0.2)')
            fig_sent.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", yaxis_title="Polarity (-1 to +1)", xaxis_title="Comment Sequence")
            st.plotly_chart(fig_sent, use_container_width=True)

            # THE NEW INTERPRETATION INSIGHT
            st.markdown(f"""
                <div class="insight-card">
                    <h4>💡 Sentiment Interpretation</h4>
                    <p>{intel['sentiment_insight']}</p>
                    <small style="color: #8b949e;">Peaks represent high emotional resonance; valleys indicate friction or critical feedback.</small>
                </div>
            """, unsafe_allow_html=True)

            st.write("##")
            st.markdown("### 📝 Raw Interaction Log (Comments sections)")
            st.dataframe(data['comment_data'], use_container_width=True)

        else:
            st.error("Data retrieval failed. Please check the URL or API limits.")