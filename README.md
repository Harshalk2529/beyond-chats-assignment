# beyond-chats-assignment
Beyond Chats Internship Assignment 

# 🧠 Reddit User Persona Generator

This project analyzes a Reddit user's public activity and generates a psychological and behavioral **persona profile** in plain text format.

---

## 🔍 What It Does

Given a Reddit profile URL, the script:
- Extracts posts and comments using the Reddit API (`praw`)
- Analyzes:
  - Estimated age & gender
  - Personality traits (Big Five & MBTI-style axes)
  - Emotional tone (polarity & subjectivity)
  - Interests (top subreddits & themes)
  - Goals, values, and motivations
- Outputs a structured `.txt` file with the complete persona report

 ## 🚀 How to Run

# 1. Download reddit_persona.py
# 2. Replace with your reddit app credentials
    reddit = praw.Reddit(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_SECRET",
        user_agent="/u/YOUR_USERNAME"
    )

# 3. Add this libraries and dependencies 
- pip install praw textblob nltk
- python -m nltk.downloader punkt

# 4. Finally run - reddit_persona.py
  Takes input as a - https://www.reddit.com/user/username/ (format)
  Not works with - https://www.reddit.com/r/username/
                 - https://www.reddit.com/user/username/comments/
                 - https://www.reddit.com/user/username/posts/

  
  ## Contents

  - reddit_persona.py	(Main script for generating persona)
  - Corresponding reddit_persona.ipynb file
  - persona of user Hungry-Move-6603
  - persona of user kojied
  - Readme.md
