import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import os
import pandas as pd

# Load external CSS file
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("whatsapp-chat-analysis-main/style.css")

# Title of the application
st.sidebar.title("WhatsApp Chat Analyzer")

# Upload file section
uploaded_file = st.sidebar.file_uploader("Choose a file (.txt or .zip)")
if uploaded_file is not None:
    data = None
    file_path = ""

    # Handle .zip files
    if uploaded_file.name.endswith('.zip'):
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall("extracted_chats")
            file_names = zip_ref.namelist()
            if len(file_names) > 0:
                file_path = os.path.join("extracted_chats", file_names[0])
            else:
                st.error("No valid chat file found in the ZIP archive.")
                st.stop()

        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                data = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding="ISO-8859-1") as file:
                data = file.read()

    elif uploaded_file.name.endswith('.txt'):
        bytes_data = uploaded_file.getvalue()
        try:
            data = bytes_data.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            data = bytes_data.decode("ISO-8859-1")

    else:
        st.error("Please upload a valid .txt or .zip file.")
        st.stop()

    if data is None:
        st.error("Failed to read the file. Please upload a valid file.")
        st.stop()

    df = preprocessor.preprocess(data)
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.markdown('<div class="animated-title">Top Statistics</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        st.markdown('<div class="animated-title">Monthly Timeline</div>', unsafe_allow_html=True)
        timeline = helper.monthly_timeline(selected_user, df)
        if not timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.warning("No data available for Monthly Timeline.")

        st.markdown('<div class="animated-title">Daily Timeline</div>', unsafe_allow_html=True)
        daily_timeline = helper.daily_timeline(selected_user, df)
        if not daily_timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.warning("No data available for Daily Timeline.")

        st.markdown('<div class="animated-title">Activity Map</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            if not busy_day.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.warning("No data available for Most Busy Day.")

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            if not busy_month.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.warning("No data available for Most Busy Month.")

        st.markdown('<div class="animated-title">Weekly Activity Map</div>', unsafe_allow_html=True)
        user_heatmap = helper.activity_heatmap(selected_user, df)
        if not user_heatmap.empty and not user_heatmap.isnull().values.all():
            user_heatmap = user_heatmap.fillna(0).applymap(lambda x: int(round(x)))
            fig, ax = plt.subplots()
            sns.heatmap(user_heatmap, cmap="YlGnBu", annot=True, fmt=".0f", linewidths=.5)
            st.pyplot(fig)
        else:
            st.warning("No data available for Weekly Activity Map.")

        if selected_user == 'Overall':
            st.markdown('<div class="animated-title">Most Busy Users</div>', unsafe_allow_html=True)
            x, new_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)
            with col1:
                if not x.empty:
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                else:
                    st.warning("No data available for Most Busy Users.")
            with col2:
                if not new_df.empty:
                    st.dataframe(new_df)
                else:
                    st.warning("No user data available.")

        st.markdown('<div class="animated-title">Wordcloud</div>', unsafe_allow_html=True)
        df_wc = helper.create_wordcloud(selected_user, df)
        if df_wc:
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            plt.axis("off")
            st.pyplot(fig)
        else:
            st.warning("No words available to generate WordCloud.")

        st.markdown('<div class="animated-title">Most Common Words</div>', unsafe_allow_html=True)
        most_common_df = helper.most_common_words(selected_user, df)
        if not most_common_df.empty:
            fig, ax = plt.subplots()
            ax.barh(most_common_df['word'], most_common_df['count'], color='blue')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.warning("No common words to display!")

        st.markdown('<div class="animated-title">Emoji Analysis</div>', unsafe_allow_html=True)
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)
        with col1:
            if not emoji_df.empty:
                st.dataframe(emoji_df)
            else:
                st.warning("No emojis found to analyze.")
        with col2:
            if not emoji_df.empty and emoji_df.shape[0] > 0:
                fig, ax = plt.subplots()
                top_n = min(5, len(emoji_df))
                ax.pie(emoji_df.iloc[:top_n, 1], labels=emoji_df.iloc[:top_n, 0], autopct="%0.2f")
                st.pyplot(fig)
            else:
                st.warning("No emoji data available for analysis.")

