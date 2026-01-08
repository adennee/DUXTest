# Healthcare UX News Agent

An intelligent agent that automatically collects, analyzes, and curates relevant news and research about UX design in healthcare and life sciences, delivering insights directly to your Notion workspace.

## Overview

This agent helps Senior UX leaders stay informed about the latest trends, research, and best practices in healthcare and life sciences user experience design. It:

- 🔍 **Collects** news from curated RSS feeds and web sources
- 🚀 **Tracks** product releases from major competitors (Google, Microsoft, AWS, Epic, Veeva, etc.)
- 🤖 **Analyzes** content using Claude AI to determine relevance to healthcare UX
- 📊 **Scores** articles based on their value for UX professionals
- 📝 **Extracts** key insights and actionable takeaways
- 🎯 **Identifies** competitive intelligence and UX implications
- 📚 **Publishes** to Notion in a clean, readable format
- ⏰ **Runs** automatically on a schedule you define

## Features

### Content Sources
- Healthcare IT news (HealthcareITNews, MobiHealthNews, HealthTech Magazine)
- UX design publications (Nielsen Norman Group, UX Matters)
- **Competitor product releases** from:
  - **Tech Giants**: Google, Microsoft, IBM, SAP, Salesforce, AWS
  - **Healthcare/Life Sciences**: Epic, Veeva Systems, Medidata, Qlik, Informatica, Philips
- Keyword-based search for emerging topics
- Configurable RSS feeds and search terms

### Intelligent Analysis
- Relevance scoring (0.0-1.0) using Claude AI
- Automatic summarization for quick reading
- Key insights extraction for UX professionals
- **Specialized analysis for product releases** with competitive insights
- Context-aware tagging and categorization
- UX implications analysis for competitor features

### Notion Integration
- Clean, structured article pages
- **Visual badges for product releases** (🚀)
- Rich metadata (source, date, relevance score, tags)
- Direct links to original articles
- Optimized for reading or text-to-speech
- Separate sections for "What Was Released" and "UX Implications"

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Notion account and integration token
- (Optional) News API key for web search

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DUXTest
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key
   NOTION_API_KEY=your_notion_integration_token
   NOTION_DATABASE_ID=your_notion_database_id
   ```

### Notion Setup

1. **Create a Notion Integration**
   - Go to https://www.notion.so/my-integrations
   - Click "+ New integration"
   - Name it "Healthcare UX News Agent"
   - Copy the "Internal Integration Token" to your `.env` file

2. **Create a Notion Database**
   - Create a new database in Notion (full page or inline)
   - Add the following properties:

   | Property Name | Type | Description |
   |--------------|------|-------------|
   | Title | Title | Article title |
   | URL | URL | Link to article |
   | Published | Date | Publication date |
   | Source | Text | News source |
   | Relevance Score | Number | 0-1 relevance score |
   | Tags | Multi-select | Article categories |

3. **Share Database with Integration**
   - Click "..." menu on your database
   - Click "Connections"
   - Add your "Healthcare UX News Agent" integration

4. **Get Database ID**
   - Copy the database URL: `https://notion.so/workspace/DATABASE_ID?v=...`
   - Extract the `DATABASE_ID` part (32-character alphanumeric string)
   - Add it to your `.env` file

### Verify Setup

```bash
python -m src.main verify
```

This will check that all integrations are configured correctly.

## Usage

### Run Once

Collect and publish articles once, then exit:

```bash
python -m src.main run
```

Options:
- `--days 7` - Look back 7 days for articles (default)
- `--log-level INFO` - Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file logs/agent.log` - Write logs to file

### Run on Schedule

Run the agent continuously on a schedule:

```bash
python -m src.main schedule
```

The agent will:
1. Run immediately on start
2. Run again every N hours (configured in `.env`)
3. Continue until stopped (Ctrl+C)

### Configuration

Edit `.env` to customize behavior:

```env
# How often to run (in hours)
AGENT_RUN_INTERVAL_HOURS=24

# Maximum articles to publish per run
MAX_ARTICLES_PER_RUN=20

# Minimum relevance score (0.0-1.0)
MIN_RELEVANCE_SCORE=0.7

# Logging level
LOG_LEVEL=INFO
```

### Customize Sources

Edit `src/config/settings.py` to add RSS feeds or search keywords:

```python
rss_feeds: List[str] = Field(default_factory=lambda: [
    "https://www.healthcareitnews.com/rss.xml",
    "https://your-custom-feed.com/rss",
    # Add more feeds here
])

search_keywords: List[str] = Field(default_factory=lambda: [
    "healthcare UX",
    "your custom keyword",
    # Add more keywords here
])
```

## Project Structure

```
DUXTest/
├── src/
│   ├── agents/              # Main agent logic
│   │   └── healthcare_news_agent.py
│   ├── config/              # Configuration
│   │   └── settings.py
│   ├── integrations/        # External API clients
│   │   ├── claude_analyzer.py
│   │   └── notion_client.py
│   ├── scrapers/            # Content collection
│   │   ├── rss_scraper.py
│   │   └── web_scraper.py
│   ├── models/              # Data models
│   │   └── news.py
│   ├── utils/               # Utilities
│   │   └── logging_config.py
│   └── main.py              # Entry point
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Notion Tips for Reading/Listening

### For Reading
- Use Notion's "Focus mode" for distraction-free reading
- Filter by "Relevance Score" to see most important articles first
- Sort by "Published" date to see newest first
- Use tags to group by topic

### For Listening
- Use Notion's built-in text-to-speech (not available on all platforms)
- Export pages to PDF and use a PDF reader with TTS
- Use browser extensions like "Read Aloud" or "Natural Reader"
- On mobile: iOS "Speak Screen" or Android "Select to Speak"

## Troubleshooting

### "Notion database not accessible"
- Verify the database is shared with your integration
- Check that `NOTION_DATABASE_ID` is correct (32 characters, no dashes)
- Ensure `NOTION_API_KEY` is the integration token, not your user token

### "No articles collected"
- Check your internet connection
- Verify RSS feeds are accessible
- Try increasing `days_back` parameter
- Check logs for specific errors

### "Low relevance scores"
- The agent is working correctly - most articles aren't relevant
- Lower `MIN_RELEVANCE_SCORE` in `.env` to see more articles
- Add more specific keywords to `search_keywords`
- Add more targeted RSS feeds

### Rate limiting
- Claude API: 50 requests/minute on free tier
- Notion API: 3 requests/second
- News API: 100 requests/day on free tier
- The agent respects these limits automatically

## Development

### Running Tests
```bash
pytest tests/
```

### Adding a New News Source

1. Create a new scraper in `src/scrapers/`
2. Implement the scraping logic
3. Add to agent in `src/agents/healthcare_news_agent.py`

### Contributing

Contributions welcome! Please:
- Follow existing code style
- Add tests for new features
- Update documentation

## License

[Your license here]

## Support

For issues and questions:
- Check the troubleshooting section above
- Review logs with `--log-level DEBUG`
- Open an issue on GitHub

## Roadmap

Future enhancements:
- [ ] Email digest summaries
- [ ] Slack/Teams notifications
- [ ] Advanced filtering by topic
- [ ] Historical trend analysis
- [ ] Custom LLM prompts
- [ ] Multi-language support
- [ ] PDF/research paper processing

---

Built with ❤️ for UX leaders in healthcare and life sciences.
