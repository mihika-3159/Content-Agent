from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import TypedDict, Optional, List
from utils.social_media import post_to_facebook, post_to_instagram, post_to_linkedin, schedule_to_platforms, convert_gst_to_utc
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests, openai, time, os, pytz
from datetime import datetime, timedelta
import analytics_agent
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4o-mini")

# Define the shared state
class State(TypedDict):
    topic: str
    caption: Optional[str]
    content: Optional[str]
    image_url: Optional[str]
    platforms: List[str]
    schedule_time: Optional[str]  # in GST
    retrieved_docs: Optional[str]

# Step 1: Crawl website
def crawl_site(state: State) -> State:
    def is_valid_url(url, domain):
        return urlparse(url).netloc == urlparse(domain).netloc

    start_url = "https://cloudjune.com"
    visited = set()
    to_visit = [start_url]
    pages = []
    while to_visit and len(visited) < 10:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try:
            response = requests.get(url, timeout=10)
            visited.add(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                pages.append({"url": url, "content": text})
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    if is_valid_url(full_url, start_url) and full_url not in visited:
                        to_visit.append(full_url)
        except Exception as e:
            print("Error crawling:", e)
        time.sleep(1)

    content = "\n".join([p["content"] for p in pages[:3]])
    state["retrieved_docs"] = content
    return state

# Step 2: Generate caption & content
def generate_text(state: State) -> State:
    topic = state["topic"]
    context = state["retrieved_docs"]
    prompt = f"""
You are a B2B content strategist. Write:
CAPTION (max 250 characters)
CONTENT (80-150 words)

Topic: {topic}
Context:
{context}

Format:
CAPTION: <caption>
CONTENT: <content>
"""
    result = model.invoke([HumanMessage(content=prompt)])
    text = result.content
    if "CAPTION:" in text and "CONTENT:" in text:
        state["caption"] = text.split("CAPTION:")[1].split("CONTENT:")[0].strip()
        state["content"] = text.split("CONTENT:")[1].strip()
    else:
        state["caption"] = "⚠️ Could not parse caption"
        state["content"] = text
    return state

# Step 3: Generate image
def generate_image(state: dict) -> dict:
    prompt = state["topic"]
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        img = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024")
        state["image_url"] = img.data[0].url
        print("✅ Image generated.")
    except Exception as e:
        print("❌ Failed to generate image:", e)
        state["image_url"] = None
    return state

# Step 4: Post or schedule
def post_or_schedule(state: State) -> State:
    caption = state["caption"]
    content = state["content"]
    image_url = state["image_url"]
    platforms = state["platforms"]

    body = f"{caption}\n\n{content}"
    if state["schedule_time"]:
        try:
            utc_time = convert_gst_to_utc(state["schedule_time"])
            now = datetime.now(pytz.utc)
            if utc_time <= now + timedelta(minutes=20):
                raise ValueError("Post must be scheduled at least 20 minutes in the future.")
            schedule_to_platforms(caption, image_url, platforms, utc_time)
        except Exception as e:
            print("❌ Scheduling failed:", e)
    else:
        if "facebook" in platforms:
            post_to_facebook(body, image_url)
        if "instagram" in platforms:
            post_to_instagram(body, image_url)
        if "linkedin" in platforms:
            post_to_linkedin(body)

    return state
def ask_caption_edit(state: State) -> State:
    print(f"\nGenerated Caption:\n{state['caption']}")
    print(f"Generated Content:\n{state['content']}")
    edit = input("\nWould you like to edit the caption or content? (yes/no): ").strip().lower()

    if edit != "yes":
        return state

    while True:
        method = input("Would you like to enter your own caption and content? (yes/no): ").strip().lower()

        if method == "yes":
            state["caption"] = input("Enter your own caption: ").strip()
            state["content"] = input("Enter your own content: ").strip()

        else:
            instruction = input("Describe how you'd like to change the caption and content: ").strip()
            prompt = f"""
You are a professional social media content editor.

Original caption:
{state['caption']}

Original content:
{state['content']}

Edit instruction from user:
{instruction}

Now rewrite both the caption and the content according to the instruction. Use the following format:

CAPTION: <your edited caption>
CONTENT: <your edited content>
"""
            result = model.invoke([HumanMessage(content=prompt)])
            text = result.content

            if "CAPTION:" in text and "CONTENT:" in text:
                state["caption"] = text.split("CAPTION:")[1].split("CONTENT:")[0].strip()
                state["content"] = text.split("CONTENT:")[1].strip()
            else:
                print("⚠️ Could not parse model output. Keeping original.")
                continue

        print(f"\n📢 Updated Caption:\n{state['caption']}")
        print(f"📝 Updated Content:\n{state['content']}")
        approve = input("Are you happy with this version? (yes/no): ").strip().lower()
        if approve == "yes":
            break

    return state
def add_mentions_to_post(state: State) -> State:
    mention = input("\nWould you like to mention or tag anyone in the post? (yes/no): ").strip().lower()
    if mention == "yes":
        mention_text = input("Type how you'd like to mention them (e.g., '@JohnDoe', 'Thanks to Jane'): ")
        if mention_text:
            state["caption"] += f"\n\n{mention_text}"
    return state

# 📊 LangGraph wiring
graph = StateGraph(State)

# 🔹 Add all nodes
graph.add_node("crawl", crawl_site)
graph.add_node("generate_text", generate_text)
graph.add_node("ask_edits", ask_caption_edit)
graph.add_node("add_mentions", add_mentions_to_post)
graph.add_node("generate_image", generate_image)
graph.add_node("finalize", post_or_schedule)

# 🔹 Define clean sequential flow
graph.set_entry_point("crawl")
graph.add_edge("crawl", "generate_text")
graph.add_edge("generate_text", "ask_edits")
graph.add_edge("ask_edits", "add_mentions")
graph.add_edge("add_mentions", "generate_image")
graph.add_edge("generate_image", "finalize")
graph.set_finish_point("finalize")

# 🔹 Compile
app = graph.compile()

# 🚀 Run it manually
if __name__ == "__main__":
    print("Welcome to the Content Agent! What would you like to do?")
    print("1. Post new content")
    print("2. View analytics for existing posts")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        topic = input("Enter topic: ")
        platforms = input("Enter platforms (facebook, instagram, linkedin): ").replace(" ", "").split(",")
        schedule = input("Schedule post? (y/n): ").lower()
        schedule_time = None
        if schedule == "y":
            schedule_time = input("Enter time in GST (YYYY-MM-DD HH:MM): ")

        initial_state = {
            "topic": topic,
            "platforms": platforms,
            "schedule_time": schedule_time,
            "caption": None,
            "content": None,
            "image_url": None,
            "retrieved_docs": None
        }
        app.invoke(initial_state)
        print("✅ Post complete!")

    elif choice == "2":
        analytics_agent_main = getattr(analytics_agent, "__main__", None)
        if analytics_agent_main:
            analytics_agent_main()
        else:
            print("⚠️ Could not find analytics main function.")
    else:
        print("❌ Invalid choice. Exiting.")