import os
import requests
from textblob import TextBlob
from dotenv import load_dotenv
load_dotenv()

# Load credentials from environment
FB_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FB_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN")
INSTA_USER_ID = os.getenv("IG_ACCOUNT_ID")
INSTA_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN")  # Same as FB token
LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_ORG_ID = os.getenv("LINKEDIN_ORGANIZATION_ID")

# Sentiment analysis
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return "positive" if polarity > 0 else "negative" if polarity < 0 else "neutral"

# ---------------------- FACEBOOK ANALYTICS ---------------------- #
def get_facebook_posts():
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/posts?fields=message,created_time,id&access_token={FB_TOKEN}"
    res = requests.get(url)
    res.raise_for_status()
    return res.json().get("data", [])

def get_facebook_post_metrics(post_id):
    fields = "insights.metric(post_impressions),likes.summary(true),comments.summary(true)"
    url = f"https://graph.facebook.com/v19.0/{post_id}?fields={fields}&access_token={FB_TOKEN}"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

def get_facebook_comments(post_id):
    url = f"https://graph.facebook.com/v19.0/{post_id}/comments?access_token={FB_TOKEN}"
    res = requests.get(url)
    res.raise_for_status()
    comments = res.json().get("data", [])
    return [(c['message'], analyze_sentiment(c['message'])) for c in comments if 'message' in c]

def display_facebook_analytics():
    posts = get_facebook_posts()
    if not posts:
        print("No Facebook posts found.")
        return
    for idx, post in enumerate(posts):
        print(f"{idx + 1}. ID: {post['id']} | Created: {post['created_time']} | Preview: {post.get('message', '')[:60]}")
    choice = int(input("Choose post number to analyze: ")) - 1
    post_id = posts[choice]["id"]
    metrics = get_facebook_post_metrics(post_id)
    impressions = metrics.get("insights", {}).get("data", [{}])[0].get("values", [{}])[0].get("value", 0)
    likes = metrics.get("likes", {}).get("summary", {}).get("total_count", 0)
    comments = metrics.get("comments", {}).get("summary", {}).get("total_count", 0)
    print(f"\nViews: {impressions}")
    print(f"Likes: {likes}")
    print(f"Comments: {comments}")

    sentiments = get_facebook_comments(post_id)
    print("\nSentiment Analysis:")
    if not sentiments:
        print("No comments available for sentiment analysis.")
    else:
        for comment, sentiment in sentiments:
            print(f"- {sentiment.upper()}: {comment}")

# ---------------------- INSTAGRAM ANALYTICS ---------------------- #
def get_instagram_posts():
    url = f"https://graph.facebook.com/v19.0/{INSTA_USER_ID}/media?fields=id,caption,timestamp&access_token={INSTA_TOKEN}"
    res = requests.get(url)
    res.raise_for_status()
    return res.json().get("data", [])

def get_instagram_post_metrics(post_id):
    url = f"https://graph.facebook.com/v19.0/{post_id}?fields=like_count,comments_count,caption&access_token={INSTA_TOKEN}"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

def get_instagram_comments(post_id):
    url = f"https://graph.facebook.com/v19.0/{post_id}/comments?access_token={INSTA_TOKEN}"
    res = requests.get(url)
    res.raise_for_status()
    comments = res.json().get("data", [])
    return [(c['text'], analyze_sentiment(c['text'])) for c in comments if 'text' in c]

def display_instagram_analytics():
    posts = get_instagram_posts()
    if not posts:
        print("No Instagram posts found.")
        return
    for idx, post in enumerate(posts):
        print(f"{idx + 1}. ID: {post['id']} | Timestamp: {post['timestamp']} | Caption: {post.get('caption', '')[:60]}")
    choice = int(input("Choose post number to analyze: ")) - 1
    post_id = posts[choice]["id"]
    metrics = get_instagram_post_metrics(post_id)
    print(f"\nLikes: {metrics.get('like_count', 0)}")
    print(f"Comments: {metrics.get('comments_count', 0)}")
    print(f"Caption: {metrics.get('caption', '')}")

    sentiments = get_instagram_comments(post_id)
    print("\nSentiment Analysis:")
    if not sentiments:
        print("No comments available for sentiment analysis.")
    else:
        for comment, sentiment in sentiments:
            print(f"- {sentiment.upper()}: {comment}")

# ---------------------- LINKEDIN ANALYTICS ---------------------- #
headers = {"Authorization": f"Bearer {LINKEDIN_TOKEN}"}

def get_linkedin_posts():
    url = f"https://api.linkedin.com/v2/shares?q=owners&owners=urn:li:organization:{LINKEDIN_ORG_ID}&sharesPerOwner=100"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json().get("elements", [])

def get_linkedin_post_metrics(urn):
    reactions_url = f"https://api.linkedin.com/v2/socialActions/{urn}/likes"
    comments_url = f"https://api.linkedin.com/v2/socialActions/{urn}/comments"

    reactions = requests.get(reactions_url, headers=headers).json()
    comments = requests.get(comments_url, headers=headers).json()

    reaction_count = reactions.get("paging", {}).get("total", 0)
    comment_data = comments.get("elements", [])
    comment_sentiments = [
        (c["message"]["text"], analyze_sentiment(c["message"]["text"]))
        for c in comment_data if "message" in c and "text" in c["message"]
    ]
    return reaction_count, len(comment_sentiments), comment_sentiments

def display_linkedin_analytics():
    posts = get_linkedin_posts()
    if not posts:
        print("No LinkedIn posts found.")
        return
    for idx, post in enumerate(posts):
        post_id = post.get("id", "").split(":")[-1]
        print(f"{idx + 1}. URN: {post['id']} | Text: {post.get('text', {}).get('text', 'No caption')[:60]}...")
    choice = int(input("Choose post number to analyze: ")) - 1
    urn = posts[choice]["id"]
    likes, comment_count, sentiments = get_linkedin_post_metrics(urn)

    print(f"\nLikes: {likes}")
    print(f"Comments: {comment_count}")
    print("\nSentiment Analysis:")
    if not sentiments:
        print("No comments available for sentiment analysis.")
    else:
        for comment, sentiment in sentiments:
            print(f"- {sentiment.upper()}: {comment}")

# ---------------------- MAIN FUNCTION ---------------------- #
def main():
    print("📊 Choose a platform to analyze:")
    print("1. Facebook")
    print("2. Instagram")
    print("3. LinkedIn")
    choice = input("Enter 1, 2 or 3: ").strip()
    if choice == "1":
        display_facebook_analytics()
    elif choice == "2":
        display_instagram_analytics()
    elif choice == "3":
        display_linkedin_analytics()
    else:
        print("❌ Invalid choice.")

if __name__ == "__main__":
    main()