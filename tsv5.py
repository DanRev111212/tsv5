import streamlit as st
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import seaborn as sns
import random

# Define a function to perform sentiment analysis (dummy implementation)
def perform_sentiment_analysis(tweets):
    sentiment_scores = [random.uniform(-1, 1) for _ in range(len(tweets))]
    return sentiment_scores

# Define a function to fetch tweets
def fetch_tweets(username, term, location, num_tweets=100):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    try:
        if username:
            driver.get(f'https://nitter.catsarch.com/{username}')
        elif term:
            if location:
                driver.get(f'https://nitter.catsarch.com/search?q={term}&near={location}')
            else:
                driver.get(f'https://nitter.catsarch.com/search?q={term}')
        else:
            st.warning("Please enter a Twitter username or search term.")
            return [], []

        tweets, usernames = [], []

        while True:
            for tweet in driver.find_elements(By.CLASS_NAME, 'tweet-content'):
                tweets.append(tweet.text)
                usernames.append(username if username else term)

            try:
                driver.find_element(By.LINK_TEXT, 'Older').click()
            except:
                break
    except Exception as e:
        st.warning(f"An error occurred while fetching tweets: {str(e)}")
        tweets, usernames = [], []
    finally:
        driver.quit()

    return tweets, usernames

# Main Streamlit app
st.title('Twitter Sentiment Analysis')

username = st.text_input('Enter a Twitter username')
search_term = st.text_input('Enter a search term (optional)')
location = st.text_input('Enter a location (optional)')

if st.button('Analyze Tweets'):
    if username or search_term:
        tweets, usernames = fetch_tweets(username, search_term, location)

        if not tweets:
            st.warning("No tweets found for the given username or search term.")
        else:
            # Perform sentiment analysis
            sentiment_scores = perform_sentiment_analysis(tweets)

            # Create a DataFrame with tweets, usernames, and sentiment scores
            df = pd.DataFrame({'Username': usernames, 'Tweet': tweets, 'Sentiment Score': sentiment_scores})

            # Generate a Word Cloud
            text = ' '.join(tweets)
            wordcloud = WordCloud(width=800, height=400).generate(text)

            # Create sentiment distribution plot
            plt.figure(figsize=(10, 6))
            sns.histplot(data=df, x='Sentiment Score', bins=30, kde=True)
            plt.xlabel('Sentiment Score')
            plt.ylabel('Frequency')
            st.pyplot(plt)

            # Display Word Cloud
            st.image(wordcloud.to_array())

            # Display a table of tweets and their sentiment scores
            st.write(df)

            # Create a pie chart to visualize sentiment distribution
            sentiment_counts = df['Sentiment Score'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))
            sentiment_distribution = sentiment_counts.value_counts()
            fig, ax = plt.subplots()
            ax.pie(sentiment_distribution, labels=sentiment_distribution.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
            st.pyplot(fig)
    else:
        st.warning("Please enter a Twitter username or search term.")
