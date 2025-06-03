# content-agent-langgraph

This project implements a LangGraph agent designed to generate engaging social media content and automate posting across various platforms. 

## Project Structure

```
content-agent-langgraph
├── src
│   ├── agent.py          # Main logic for the LangGraph agent
│   ├── utils
│   │   └── social_media.py # Utility functions for social media API interactions
│   └── types
│       └── index.py      # Custom types and interfaces for type safety
├── .env                  # Environment variables for API keys and tokens
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
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
   TWITTER_CONSUMER_KEY=your_twitter_consumer_key
   TWITTER_CONSUMER_SECRET=your_twitter_consumer_secret
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_SECRET=your_twitter_access_secret
   PIXABAY_API_KEY=your_pixabay_api_key
   LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
   LINKEDIN_ORGANIZATION_ID=your_linkedin_organization_id
   ```

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