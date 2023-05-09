import pymongo
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import ssl
import os
from dotenv import load_dotenv


def sentiment_analysis():
    load_dotenv()
    ssl._create_default_https_context = ssl._create_unverified_context

    # Download VADER lexicon
    nltk.download('vader_lexicon')

    # Connect to MongoDB
    client = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = client['VolunteerHub']

    # Create a sentiment analyzer object
    sia = SentimentIntensityAnalyzer()

    # Retrieve all events from the event collection
    event_collection = db['events']
    comment_collection = db['comments']
    events = event_collection.find()

    # Analyze the sentiment of each comment and add the result to the corresponding event document
    for event in events:
        event_id = event['_id']
        comments = comment_collection.find({'event': event_id})
        comment_count = 0
        positive_count = 0
        negative_count = 0

        # Analyze the sentiment of each comment
        for comment in comments:
            scores = sia.polarity_scores(comment['message'])
            polarity_score = scores['compound']
            if polarity_score >= 0.5:
                positive_count += 1
            elif polarity_score <= -0.5:
                negative_count += 1
            comment_count += 1

        # Classify the event based on the sentiment of its comments
        if comment_count == 0:
            classification = 'neutral'
        elif (positive_count - negative_count) >= (comment_count / 2):
            classification = 'successful'
        else:
            classification = 'unsuccessful'

        # Update the event document with the classification
        event_collection.update_one({'_id': event_id}, {'$set': {'classification': classification}})

