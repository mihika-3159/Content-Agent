import os
import requests
from textblob import TextBlob
import streamlit as st
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
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
analyzer = SentimentIntensityAnalyzer()
def analyze_sentiment(text):
    score = analyzer.polarity_scores(text)
    if score["compound"] >= 0.05:
        return "positive"
    elif score["compound"] <= -0.05:
        return "negative"
    else:
        return "neutral"

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


def visualize_analytics():

    st.set_page_config(page_title="Post Analytics", layout="centered")
    st.title("📊 Social Media Post Analytics")

    platforms = {
        "Facebook": {
            "get_posts": get_facebook_posts,
            "get_metrics": get_facebook_post_metrics,
            "get_comments": get_facebook_comments
        },
        "Instagram": {
            "get_posts": get_instagram_posts,
            "get_metrics": get_instagram_post_metrics,
            "get_comments": get_instagram_comments
        },
        "LinkedIn": {
            "get_posts": get_linkedin_posts,
            "get_metrics": get_linkedin_post_metrics,
            "get_comments": lambda urn: []  # comments handled in metrics
        }
    }

    platform = st.selectbox("Choose a platform", list(platforms.keys()))
    post_data = platforms[platform]["get_posts"]()

    if not post_data:
        st.warning(f"No posts found for {platform}.")
        return

    post_labels = [
        f"{i + 1}. {p.get('id')} - {p.get('caption', '')[:40] or p.get('message', '')[:40]}"
        for i, p in enumerate(post_data)
    ]
    selected = st.selectbox("Select a post", post_labels)
    selected_post = post_data[int(selected.split(".")[0]) - 1]
    post_id = selected_post["id"]

    st.subheader("📈 Metrics")

    if platform == "LinkedIn":
        likes, comment_count, sentiments = platforms[platform]["get_metrics"](post_id)
        st.metric("👍 Likes", likes)
        st.metric("💬 Comments", comment_count)
        views = None
    else:
        metrics = platforms[platform]["get_metrics"](post_id)
        likes = metrics.get("likes", {}).get("summary", {}).get("total_count", 0)
        comments = metrics.get("comments", {}).get("summary", {}).get("total_count", 0)
        views = metrics.get("insights", {}).get("data", [{}])[0].get("values", [{}])[0].get("value", 0) if platform == "Facebook" else None

        st.metric("👍 Likes", likes)
        st.metric("💬 Comments", comments)
        if views is not None:
            st.metric("👀 Views", views)

        sentiments = platforms[platform]["get_comments"](post_id)

    st.subheader("🧠 Sentiment Analysis")

    if not sentiments:
        st.info("No comments to analyze.")
    else:
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        for _, sentiment in sentiments:
            sentiment_counts[sentiment] += 1

        fig, ax = plt.subplots()
        ax.bar(sentiment_counts.keys(), sentiment_counts.values(), color=["green", "gray", "red"])
        ax.set_ylabel("Number of Comments")
        ax.set_title("Comment Sentiment Distribution")
        st.pyplot(fig)

        with st.expander("🗣 View Comments"):
            for comment, sentiment in sentiments:
                st.markdown(f"**{sentiment.upper()}**: {comment}")

# ---------------------- COMPARE ALL PLATFORMS ---------------------- #
def compare_all_platforms():
    print("\n📊 Comparing top posts from Facebook, Instagram, and LinkedIn...\n")

    try:
        # Facebook
        fb_post = get_facebook_posts()[0]
        fb_metrics = get_facebook_post_metrics(fb_post["id"])
        fb_likes = fb_metrics.get("likes", {}).get("summary", {}).get("total_count", 0)
        fb_comments = fb_metrics.get("comments", {}).get("summary", {}).get("total_count", 0)
        fb_views = fb_metrics.get("insights", {}).get("data", [{}])[0].get("values", [{}])[0].get("value", 0)

        # Instagram
        ig_post = get_instagram_posts()[0]
        ig_metrics = get_instagram_post_metrics(ig_post["id"])
        ig_likes = ig_metrics.get("like_count", 0)
        ig_comments = ig_metrics.get("comments_count", 0)

        # LinkedIn
        li_post = get_linkedin_posts()[0]
        li_likes, li_comments, _ = get_linkedin_post_metrics(li_post["id"])

        print(f"{'Platform':<12} | {'Likes':<6} | {'Comments':<9} | {'Views':<6}")
        print("-" * 45)
        print(f"{'Facebook':<12} | {fb_likes:<6} | {fb_comments:<9} | {fb_views}")
        print(f"{'Instagram':<12} | {ig_likes:<6} | {ig_comments:<9} | {'N/A'}")
        print(f"{'LinkedIn':<12} | {li_likes:<6} | {li_comments:<9} | {'N/A'}")

    except Exception as e:
        print(f"⚠️ Error while comparing posts: {e}")

# ---------------------- MAIN FUNCTION ---------------------- #
def main():
    import sys

    print("\n📊 Choose what you want to do:")
    print("1. Analyze Facebook in CLI")
    print("2. Analyze Instagram in CLI")
    print("3. Analyze LinkedIn in CLI")
    print("4. Compare top post across all platforms")
    print("5. Launch visual dashboard (Streamlit)")

    choice = input("Enter 1, 2, 3, 4, or 5: ").strip()

    if choice == "1":
        display_facebook_analytics()
    elif choice == "2":
        display_instagram_analytics()
    elif choice == "3":
        display_linkedin_analytics()
    elif choice == "4":
        compare_all_platforms()
    elif choice == "5":
        print("🔁 Launching Streamlit app...")
        import subprocess
        subprocess.run(["streamlit", "run", __file__, "visualize"])
    else:
        print("❌ Invalid choice.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "visualize":
        visualize_analytics()
    else:
        main()