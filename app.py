import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'figure.figsize': (10, 5),
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'font.family': 'Segoe UI Emoji',
    'figure.autolayout': True,
    'axes.edgecolor': '#dddddd'
})

st.sidebar.title("Whatsapp Chat Analyzer")

st.sidebar.markdown(
    "📄 **Upload a WhatsApp exported chat file**  \n"
    "🕒 Ensure the chat uses **AM/PM time format** (not 24-hour format)."
)

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.markdown("### 📊 **Top Statistics**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", words)
        with col3:
            st.metric("Media Shared", num_media_messages)
        with col4:
            st.metric("Links Shared", num_links)

        st.markdown("### 📆 **Monthly Timeline**")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='#00a676', marker='o', linewidth=2)
        ax.set_ylabel("Messages")
        ax.set_xlabel("Month")
        ax.set_title("Monthly Message Flow 📈")
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.markdown("### 🗓️ **Daily Timeline**")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#444')
        ax.set_ylabel("Messages")
        ax.set_xlabel("Date")
        ax.set_title("Daily Activity Tracker")
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.markdown("### 🔁 **Activity Map**")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🔷 Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_day.index, y=busy_day.values, ax=ax, palette="pastel")
            ax.set_ylabel("Messages")
            st.pyplot(fig)

        with col2:
            st.markdown("#### 🔶 Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_month.index, y=busy_month.values, ax=ax, palette="flare")
            ax.set_ylabel("Messages")
            st.pyplot(fig)

        st.markdown("### 🔥 **Weekly Activity Heatmap**")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, cmap="YlGnBu", linewidths=0.5, linecolor='white', ax=ax)
        ax.set_title("Heatmap of Weekly Activity")
        st.pyplot(fig)

        if selected_user == 'Overall':
            st.markdown("### 🏅 **Most Busy Users**")
            x, new_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                sns.barplot(x=x.index, y=x.values, ax=ax, palette="rocket")
                ax.set_ylabel("Messages")
                ax.set_title("Top Users")
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        st.markdown("### ☁️ **WordCloud**")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        most_common_df = helper.most_common_words(selected_user, df)
        st.markdown("### 🔤 **Most Common Words**")
        fig, ax = plt.subplots()
        sns.barplot(x=most_common_df[1], y=most_common_df[0], palette="mako", ax=ax)
        ax.set_xlabel("Frequency")
        ax.set_ylabel("Word")
        st.pyplot(fig)

        emoji_df = helper.emoji_helper(selected_user, df)
        st.markdown("### 😂 **Emoji Analysis**")
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            top_emojis = emoji_df[emoji_df['count'] > 1].head(10)
            labels = top_emojis['emoji']
            fig, ax = plt.subplots()
            colors = sns.color_palette('pastel')[0:len(top_emojis)]
            ax.pie(top_emojis['count'], labels=labels, autopct="%0.2f%%", colors=colors, startangle=140, textprops={'fontsize': 12})
            ax.set_title("Emoji Usage Breakdown")
            st.pyplot(fig)
