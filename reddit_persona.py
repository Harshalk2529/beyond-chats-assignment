#Import necessary Libraries
import praw # Reddit API Wrapper
from textblob import TextBlob  # For sentiment analysis
import nltk # Natural Language Toolkit

# API Setup

reddit = praw.Reddit(
    client_id="your_reddit_app_client_id",  # Replace with your Reddit App client ID
    client_secret="your_reddit_secret_id",  # Replace with your Reddit App secret
    user_agent="/u/your_username",
)

nltk.download("punkt")   # Download required tokenizer data
import os
from datetime import datetime

# Function to extract Reddit username from profile url
def extract_username(url):
    return url.rstrip("/").split("/")[-1]


# To fetch user comments, subreddits and posts
def get_user_data(username, limit=100):
    try:
        user = reddit.redditor(username)
        _ = user.id  # Force test
        posts, comments, subreddits = [], [], []
    except Exception as e:
        print(f"❌ Unable to access user data for u/{username}: {e}")
        return [], [], []
    
    # Collect recent posts, comments and their subreddits

    for comment in user.comments.new(limit=limit):
        comments.append(comment.body)
        subreddits.append(comment.subreddit.display_name)

    for submission in user.submissions.new(limit=limit):
        posts.append(submission.title + " " + (submission.selftext or ""))
        subreddits.append(submission.subreddit.display_name)

    return posts, comments, subreddits

import re
from collections import Counter

# Analyze user demographics (age, gender, location, interests)

def analyze_demographics(username, posts, comments, subreddits):
    texts = posts + comments
    all_text = " ".join(texts)

    # Try to estimate age from username using year patterns
    birth_year = None   
    match = re.search(r"(19|20)\d{2}", username)
    if match:
        birth_year = int(match.group())
        age = 2025 - birth_year if 1920 < birth_year < 2025 else "Unknown"
    else:
        age = "Unknown"

     # Estimate gender based on subreddit participation
    gender = "Unknown"
    gender_subs = {
        "female": [
            "TwoXChromosomes",
            "AskWomen",
            "femalefashionadvice",
            "TrollXChromosomes",
        ],
        "male": ["AskMen", "MensLib", "malefashionadvice"],
    }
    gender_counts = {"female": 0, "male": 0}
    for sub in subreddits:
        if sub in gender_subs["female"]:
            gender_counts["female"] += 1
        elif sub in gender_subs["male"]:
            gender_counts["male"] += 1

    if gender_counts["female"] > gender_counts["male"]:
        gender = "Likely Female"
    elif gender_counts["male"] > gender_counts["female"]:
        gender = "Likely Male"
    else:
        gender = "Unknown"

    # Try to extract possible location mentions
    location_matches = re.findall(
        r"\b(?:from|live in|moved to|based in)\s+([A-Z][a-z]+)", all_text
    )
    location = location_matches[0] if location_matches else "Unknown"

    top_interests = [s[0] for s in Counter(subreddits).most_common(5)]

    summary = f"Username: u/{username}\nEstimated Age: {age}\nLikely Gender: {gender}\nPossible Location: {location}\nTop Interests/Subreddits: {', '.join(top_interests)}"
    return summary


# Formatted persona
# Map personality traits based on common axis (e.g., Introvert vs Extrovert)
from collections import defaultdict


def personality_axis(posts, comments):
    long_text = " ".join(posts + comments).lower()
    traits = {
        "Introvert": [
            "alone",
            "quiet",
            "introspective",
            "reserved",
            "reflect",
            "prefer staying in",
        ],
        "Extrovert": [
            "party",
            "hangout",
            "talk",
            "outgoing",
            "social",
            "group",
            "friends",
        ],
        "Intuition": [
            "theory",
            "idea",
            "concept",
            "imagine",
            "future",
            "possibility",
            "vision",
        ],
        "Sensing": [
            "details",
            "facts",
            "experience",
            "observation",
            "realistic",
            "data",
        ],
        "Feeling": ["feel", "empathy", "emotion", "values", "kind", "care", "harmony"],
        "Thinking": ["logic", "analyze", "reason", "critique", "objective", "system"],
    }
    scores = defaultdict(int)
    for trait, keywords in traits.items():
        for word in keywords:
            scores[trait] += long_text.count(word)
    axes = [
        ("Introvert", "Extrovert"),
        ("Intuition", "Sensing"),
        ("Feeling", "Thinking"),
    ]
    results = []

    # Compare traits pair-wise and calculate percentages
    for t1, t2 in axes:
        c1, c2 = scores[t1], scores[t2]
        total = c1 + c2 if (c1 + c2) > 0 else 1
        p1 = round((c1 / total) * 100)
        p2 = 100 - p1
        dominant = t1 if p1 > p2 else t2
        results.append(f"{t1[:1]}–{t2[:1]}: {dominant} ({p1}% {t1}, {p2}% {t2})")
    return "\n".join(results)

# Analyze Big Five traits + Interests + Values + Emotional Tone
def analyze_personality(posts, comments, subreddits):
    long_text = " ".join(posts + comments).lower()
    trait_keywords = {
        "Openness": ["imagine", "creativity", "philosophy", "theory", "dream"],
        "Conscientiousness": ["routine", "plan", "organized", "goal", "discipline"],
        "Extraversion": ["party", "people", "hangout", "social", "talk"],
        "Agreeableness": ["care", "support", "feel", "empathy", "kind"],
        "Neuroticism": ["anxious", "depressed", "worried", "stressed", "upset"],
    }
    result = []
    for trait, keywords in trait_keywords.items():
        example = next(
            (
                text
                for text in posts + comments
                if any(k in text.lower() for k in keywords)
            ),
            None,
        )
        level = "high" if example else "low"
        line = f"{trait}: {level}"
        if example:
            line += f"\n    🔹 Sample: \"{example.split('.')[0]}...\""
        result.append(line)
    # Add top subreddits with examples
    result.append("\nInterests and Passions:")
    for sub, count in Counter(subreddits).most_common(5):
        line = f"- {sub} ({count} posts/comments)"
        for text in posts + comments:
            if sub.lower() in text.lower():
                line += f"\n    🔹 Sample: \"{text.split('.')[0]}...\""
                break
        result.append(line)

    result.append("\n🔎 Possible Values, Beliefs & Judgements:")
    value_keywords = {
        "Freedom": ["freedom", "choice", "independent"],
        "Equality": ["equality", "fairness", "rights", "justice"],
        "Tradition": ["tradition", "culture", "heritage"],
        "Progress": ["change", "innovation", "future"],
        "Security": ["safe", "security", "protection", "risk"],
    }
    for value, keywords in value_keywords.items():
        example = next(
            (
                text
                for text in posts + comments
                if any(k in text.lower() for k in keywords)
            ),
            None,
        )
        if example:
            result.append(f"- {value}\n    🔹 Sample: \"{example.split('.')[0]}...\"")
    # sentiment analysis
    blob = TextBlob(long_text)
    result.append("\n🧠 Emotional Tone:")
    result.append(f"Polarity: {round(blob.sentiment.polarity, 2)}")
    result.append(f"Subjectivity: {round(blob.sentiment.subjectivity, 2)}")

    sentiments = [
        (TextBlob(t).sentiment.polarity, t) for t in posts + comments if len(t) > 20
    ]
    if sentiments:
        most_pos = max(sentiments, key=lambda x: x[0])
        most_neg = min(sentiments, key=lambda x: x[0])
        result.append("\n🔹 Most Positive Sample:")
        result.append(
            f'    "{most_pos[1][:100]}..."\n    Score: {round(most_pos[0], 2)}'
        )
        result.append("\n🔹 Most Negative Sample:")
        result.append(
            f'    "{most_neg[1][:100]}..."\n    Score: {round(most_neg[0], 2)}'
        )

    return "\n".join(result)

# Extract user goals, needs, desires using common intent patterns
#  patterns for goals and needs
# patterns to catch goal/need expressions
def extract_goals_needs(posts, comments):
    texts = posts + comments
    patterns = [
        r"\bto have [^\n.?!]+[.?!]",
        r"\bto select [^\n.?!]+[.?!]",
        r"\bto enjoy [^\n.?!]+[.?!]",
        r"\bto be able to [^\n.?!]+[.?!]",
        r"\bi need [^\n.?!]+[.?!]",
        r"\bi'm trying to [^\n.?!]+[.?!]",
        r"\bi want to [^\n.?!]+[.?!]",
        r"\bmy goal is [^\n.?!]+[.?!]",
        r"\bcan someone [^\n.?!]+[.?!]",
        r"\bhow do i [^\n.?!]+[.?!]",
        r"\bany tips [^\n.?!]+[.?!]",
        r"\bi wish [^\n.?!]+[.?!]",
        r"\bi would like to [^\n.?!]+[.?!]",
        r"\bi struggle with [^\n.?!]+[.?!]",
        r"\bi hope to [^\n.?!]+[.?!]",
        r"\bi wish to [^\n.?!]+[.?!]",
        r"\bto (?:achieve|accomplish|complete|succeed in) [^\n.?!]+[.?!]",
        r"\bi'm looking for [^\n.?!]+[.?!]",
        r"\bit's important that [^\n.?!]+[.?!]",
        r"\bit should have [^\n.?!]+[.?!]",
        r"\bi value [^\n.?!]+[.?!]",
        r"\bi prefer [^\n.?!]+[.?!]",
    ]
    matched_statements = []
    for text in texts:
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matched_statements.extend(found)
    matched_statements = [
        s.strip().capitalize() for s in matched_statements if len(s.strip()) > 10
    ]
    matched_statements = list(dict.fromkeys(matched_statements))
    if matched_statements:
        return "\n".join([f"{i+1}. {s}" for i, s in enumerate(matched_statements)])
    else:
        return "No explicit goals or needs were detected."


# Combine all components into a structured report and save as text

def generate_and_save_report(username, posts, comments, subreddits):
    summary = analyze_demographics(username, posts, comments, subreddits)
    axis = personality_axis(posts, comments)
    traits = analyze_personality(posts, comments, subreddits)
    goals = extract_goals_needs(posts, comments)

    full_report = f"""
--- REDDIT USER PERSONA ---

[User Summary]
{summary}

[Personality Axis]
{axis}

[Traits, Interests & Sentiment]
{traits}

[Goals, Needs & Wishes]
{goals}
""" #File will be named as username_persona.txt
    with open(f"{username}_persona.txt", "w", encoding="utf-8") as f:
        f.write(full_report)
    print(f"[✅] Persona saved to {username}_persona.txt")


# Main Execution
user_url = input("Enter Reddit Profile URL: ")
username = extract_username(user_url)
print(f"[→] Extracted username: {username}")

print("[...] Fetching Reddit activity...")
posts, comments, subreddits = get_user_data(username)

print("[...] Generating and saving persona...")
generate_and_save_report(username, posts, comments, subreddits)





