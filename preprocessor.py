import re
import pandas as pd

def preprocess(data):
    """Preprocess WhatsApp chat data and return a structured DataFrame."""
    
    # Corrected regex pattern to handle MM/DD/YY, hh:mm AM/PM - format
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s[APap][Mm]\s-\s'

    # Split messages and extract dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create DataFrame with messages and date
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Correct datetime format for MM/DD/YY with AM/PM
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p - ')
    except ValueError:
        raise Exception("⚠️ Incorrect Date/Time format! Please verify the date format in the chat data.")

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Split user and message
    users = []
    messages = []
    
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
        if len(entry) > 1:  # User detected
            users.append(entry[1])  # User name
            messages.append(entry[2])  # Message content
        else:  # System notification or media
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Additional columns for better analysis
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Period column for time analysis
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append(f"00-{hour + 1}")
        else:
            period.append(f"{hour}-{hour + 1}")
    
    df['period'] = period

    return df
