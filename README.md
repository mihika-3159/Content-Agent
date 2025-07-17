# content-agent-langgraph

This project implements a LangGraph agent designed to generate engaging social media content and automate posting across various platforms. 

## Project Structure

```
content-agent-langgraph/
├── src/               ← LangGraph logic & agents
│   ├── agent.py
│   ├── utils/social_media.py
│   └── types/index.py
├── web/               ← Flask UI server & frontend
│   ├── app.py
│   ├── static/
│   │   ├── styles.css
│   │   └── logo.png
│   └── templates/
│       └── index.html
├── .env
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd content-agent-langgraph
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your API keys and tokens:
   ```
   OPENAI_API_KEY=your_openai_api_key
   FACEBOOK_PAGE_ID=your_facebook_page_id
   FACEBOOK_PAGE_TOKEN=your_facebook_page_token
   INSTAGRAM_USER_ID=your_instagram_user_id
   LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
   LINKEDIN_ORGANIZATION_ID=your_linkedin_organization_id
   ```

## Generation of Tokens Instructions

1. **Facebook and Instagram:**
   - Go to Meta for developers
   - Create an app using the facebook account you intend to post on
   - Add the following use cases to the app
      -> Manage everything on your page
      -> Manage messaging and content on Instagram
   - Use the Graph API explorer to generate the access token and IDs
   - Add the following permissions: pages_read_engagement, pages_manage_posts, instagram_basic, instagram_content_publish, pages_show_list
   - Run this: me/accounts
   - The data in the 'id' field is your page id
   - The data in the 'access token' field is your page access token
   - Run this: /{enter_your_page_id}?fields=instagram_business_account
   - The data in the 'id' field is your instagram account ID (must be a business account)

2. **LinkedIn:**
   - Go to LinkedIn for developers
   - Create an app with the Community Management API (requires company page, company LinkedIn account, and approval)
   - Go to OAuth 2.0 tools
   - Generate a new access token as an Admin of the company page
   - Run this in Postman: https://api.linkedin.com/v2/organizationAcls?q=roleAssignee&role=ADMINISTRATOR
   - Add a header 'Authorization' with value 'Bearer enter_access_token'
   - The data in the 'organization' field is your Company URN

## Usage

1. **Run the agent:**
   Execute the main script to start generating captions and posting to social media:
   ```bash
   python src/agent.py
   ```

2. **Follow the prompts:**
   The agent will ask for the topic you want to post about and the platforms you wish to use.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.