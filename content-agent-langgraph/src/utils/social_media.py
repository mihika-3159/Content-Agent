import os
import requests
import tweepy
from dotenv import load_dotenv
import mimetypes
load_dotenv()
# Load environment variables
FACEBOOK_PAGE_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
COMPANY_URN = os.getenv("COMPANY_URN")
FACEBOOK_PAGE_ID= os.getenv("FACEBOOK_PAGE_ID")

# Post to Facebook using Graph API
def post_to_facebook(message: str, image_url: str = None):
    try:
        if image_url:
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            # Guess the content type from the URL or response headers
            content_type = img_response.headers.get('Content-Type') or mimetypes.guess_type(image_url)[0] or 'image/jpeg'
            files = {
                'source': ('image.jpg', img_response.content, content_type)
            }
            payload = {
                'caption': message,
                'access_token': FACEBOOK_PAGE_TOKEN
            }
            res = requests.post(
                f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/photos",
                data=payload,
                files=files
            )
        else:
            payload = {
                'message': message,
                'access_token': FACEBOOK_PAGE_TOKEN
            }
            res = requests.post(
                f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed",
                data=payload
            )
        res.raise_for_status()
        if not res.ok:
            print("Facebook error details:", res.text)
        print("✅ Facebook post successful!")
    except Exception as e:
        print("❌ Facebook post failed:", e)
        if hasattr(e, 'response') and e.response is not None:
            print("Response content:", e.response.text)

# Post to Instagram (must be image post)
def post_to_instagram(caption: str, image_url: str):
    graph_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media"
    create_post_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media_publish"

    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': FACEBOOK_PAGE_TOKEN
    }
    media_res = requests.post(graph_url, data=payload).json()
    creation_id = media_res.get("id")
    if creation_id:
        publish_payload = {
            'creation_id': creation_id,
            'access_token': FACEBOOK_PAGE_TOKEN
        }
        publish_res = requests.post(create_post_url, data=publish_payload)
        if publish_res.status_code == 200:
            print("Posted to Instagram!")
        else:
            print("Instagram post failed:", publish_res.text)
    else:
        print("Instagram media creation failed:", media_res)

# Post to Twitter using tweepy
def post_to_twitter(message: str):
    try:
        auth = tweepy.OAuth1UserHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth)
        api.update_status(status=message)
        print("Tweet posted successfully!")
    except tweepy.TweepyException as e:
        print("Tweeting failed:", e)

# Post to LinkedIn
def post_to_linkedin(caption: str, image_url: str):
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    # Step 1: Register the image for upload
    upload_request = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": COMPANY_URN,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    response = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=headers,
        json=upload_request
    )
    response.raise_for_status()
    data = response.json()
    upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    image_asset_urn = data["value"]["asset"]

    # Step 2: Upload the image
    image_data = requests.get(image_url).content
    upload_headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    upload_response = requests.put(upload_url, headers=upload_headers, data=image_data)
    upload_response.raise_for_status()

    # Step 3: Create the company post
    post_data = {
        "author": COMPANY_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": caption},
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "description": {"text": "Company post image"},
                    "media": image_asset_urn,
                    "title": {"text": "Post Image"}
                }]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    post_response = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=post_data)
    post_response.raise_for_status()
    print("Posted to LinkedIn!")
import datetime
import pytz

def convert_gst_to_utc(gst_datetime_str):
    """Convert GST time string to UTC datetime."""
    gst = pytz.timezone('Asia/Dubai') 
    gst_time = datetime.datetime.strptime(gst_datetime_str, "%Y-%m-%d %H:%M")
    gst_time = gst.localize(gst_time)
    return gst_time.astimezone(pytz.utc)

def create_instagram_container(image_url, caption):
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": FACEBOOK_PAGE_TOKEN
    }
    res = requests.post(url, data=payload)
    data = res.json()
    print("Instagram container response:", data)  # <-- Add this line
    return data.get("id")

def schedule_instagram_post(container_id, scheduled_time_utc):
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media_publish"
    payload = {
        "creation_id": container_id,
        "access_token": FACEBOOK_PAGE_TOKEN,
        "published": False,
        "scheduled_publish_time": int(scheduled_time_utc.timestamp())
    }
    res = requests.post(url, data=payload)
    print("Instagram scheduling response:", res.json())  # <-- Add this line
    return res.json()

def schedule_facebook_post(image_url, caption, scheduled_time_utc):
    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "caption": caption,
        "published": False,
        "scheduled_publish_time": int(scheduled_time_utc.timestamp()),
        "access_token": FACEBOOK_PAGE_TOKEN
    }
    res = requests.post(url, data=payload)
    return res.json()

def schedule_to_platforms(caption: str, image_url: str, platforms: list, scheduled_time_utc: datetime):
    """Schedule posts to the given platforms."""
    if "facebook" in platforms:
        response = schedule_facebook_post(image_url, caption, scheduled_time_utc)
        print("✅ Facebook post scheduled:", response)

    if "instagram" in platforms:
        container_id = create_instagram_container(image_url, caption)
        response = schedule_instagram_post(container_id, scheduled_time_utc)
        print("✅ Instagram post scheduled:", response)

    if "twitter" in platforms:
        print("⚠️ Twitter scheduling is not supported via API.")

    if "linkedin" in platforms:
        print("⚠️ LinkedIn scheduling is not supported via API.")