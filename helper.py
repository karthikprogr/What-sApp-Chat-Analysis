from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

# Constant for media omission
MEDIA_OMITTED = '<Media omitted>\n'

# URL Extractor
extract = URLExtract()


def fetch_stats(selected_user, df):
    """Fetch basic statistics: messages, words, media, and links."""
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Drop NaN values and ensure messages are strings
    df['message'] = df['message'].dropna().astype(str)

    # Fetch the number of messages
    num_messages = df.shape[0]

    # Fetch the total number of words
    words = [word for message in df['message'] for word in message.split()]

    # Fetch number of media messages
    num_media_messages = df[df['message'] == MEDIA_OMITTED].shape[0]

    # Fetch number of links shared
    links = [url for message in df['message'] for url in extract.find_urls(message)]

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    """Identify the most active users and their contribution percentage."""
    
    # Count messages per user
    x = df['user'].value_counts().head()

    # Percentage calculation
    df_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'}
    )

    return x, df_percent


def create_wordcloud(selected_user, df):
    """Generate a word cloud after removing stop words."""
    
    # Read stop words from the file
    try:
        with open('stop_hinglish.txt', 'r') as f:
            stop_words = f.read().splitlines()
    except FileNotFoundError:
        stop_words = []

    # Filter data for selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove group notifications and media messages
    temp = df[(df['user'] != 'group_notification') & (df['message'] != MEDIA_OMITTED)]

    # Drop NaN values and convert to string
    temp['message'] = temp['message'].dropna().astype(str)

    # Remove stop words from messages
    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words])

    # Apply stop word removal
    temp['message'] = temp['message'].apply(remove_stop_words)

    # Generate word cloud if messages exist
    if not temp['message'].empty:
        wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
        df_wc = wc.generate(temp['message'].str.cat(sep=" "))
        return df_wc
    else:
        return None


def most_common_words(selected_user, df):
    """Find the most common words after removing stop words."""
    
    # Read stop words
    try:
        with open('stop_hinglish.txt', 'r') as f:
            stop_words = f.read().splitlines()
    except FileNotFoundError:
        stop_words = []

    # Filter messages for the selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove group notifications and media messages
    temp = df[(df['user'] != 'group_notification') & (df['message'] != MEDIA_OMITTED)]

    # Drop NaN values and convert to string
    temp['message'] = temp['message'].dropna().astype(str)

    # Extract words and remove stop words
    words = [word for message in temp['message'] for word in message.lower().split() if word not in stop_words]

    # Return most common words as a DataFrame
    if words:
        most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])
        return most_common_df
    else:
        return pd.DataFrame(columns=['word', 'count'])


def emoji_helper(selected_user, df):
    """Analyze the most frequently used emojis."""
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Extract emojis from messages
    emojis = [c for message in df['message'].dropna().astype(str) for c in message if c in emoji.EMOJI_DATA]

    if emojis:
        emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))), columns=['emoji', 'count'])
        return emoji_df
    else:
        return pd.DataFrame(columns=['emoji', 'count'])


def monthly_timeline(selected_user, df):
    """Generate monthly timeline data."""
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Group messages by year and month
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    # Create a readable time format
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)

    return timeline


def daily_timeline(selected_user, df):
    """Generate daily timeline data."""
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Group messages by date
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_activity_map(selected_user, df):
    """Analyze the most active days of the week."""
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Return day-wise message count
    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    """Analyze the most active months."""
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Return month-wise message count
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    """Generate heatmap data for user activity across time."""
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Pivot table to create heatmap data
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap







