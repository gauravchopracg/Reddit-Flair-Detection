import praw
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pickle
from RedditAPI import accinfo

# for suppressing any warnings from getting displayed
import warnings
warnings.filterwarnings("ignore")

info = accinfo()

def get_posts(urls):

    reddit = praw.Reddit(client_id=info[0], client_secret=info[1], user_agent=info[2], username=info[3], password=info[4])

    topics = {
          "title":[],
          "url": [],
          "body":[],
          "comments": []
         }
    
    flair = ""
    
    for i in urls:
        post = reddit.submission(url=i)
        topics["title"].append(post.title)
        topics["url"].append(i)
        topics["body"].append(post.selftext)
        if len(urls) == 1:
            flair = post.link_flair_text
        
        comments =  ''
        topics["comments"].append(comments)
    
    # Creating a dataframe for all the values
    topics_data = pd.DataFrame(topics)
    topics_data["corpus"] = topics_data["title"] + " " + topics_data["body"] + " " + topics_data["comments"]
    
    return(topics_data, flair)

def rem_emoji(text):
    '''
    Takes a string as an input and returns the 
    same string after removing all the emojis
    '''
    
    emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    
    return(emoji_pattern.sub(r'', text)) # no emoji


def predict(df):
    
    X = tfidf_vectorizer.transform(df["corpus"])
    
    predictions = clf.predict(X)
    labels = label_encoder.inverse_transform(predictions)
    
    return(labels)

def process(urls):
    '''
    Input: list of urls if reddit posts
    Function: Fetches the post data from the API and cleans it in steps, and then runs prediction
    Output: list of predictions
    '''
    
    
    df, flair = get_posts(urls)
    
    df["corpus"] = df["corpus"].apply(lambda x: x.lower())
    df["corpus"] = df["corpus"].apply(rem_emoji)
    
    english_stopwords = set(stopwords.words("english"))
    df['corpus'] = df['corpus'].apply(lambda x: ' '.join([x for x in x.lower().split() if x not in english_stopwords]))
    
    # Punctuation Removal
    df['corpus'] = df['corpus'].str.replace('[^\w\s]',' ')
    
    stop_words = pd.Series(' '.join(df['corpus']).split()).value_counts()[:20]
    df['corpus']=df['corpus'].apply(lambda x: ' '.join([x for x in x.split() if x not in stop_words]))
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer() 
    df["lemmatized"] = df["corpus"].apply(lambda x: " ".join([lemmatizer.lemmatize(i) for i in x.split(" ")]))
    
    labels = predict(df)
    
    result = pd.DataFrame({"labels": labels}, index = list(df.url.values)).to_dict()["labels"]
    
    return(result, flair)
    

# Loading models
clf = pickle.load(open("classifier.pkl", "rb"))
label_encoder = pickle.load(open("label_encoder.pkl", "rb"))
tfidf_vectorizer = pickle.load(open("tfidf_vectorizer.pkl", "rb"))