# Quick Start Guide

Get your Healthcare UX News Agent up and running in 5 minutes.

## Step 1: Install Dependencies

```bash
# Run the setup script (Mac/Linux)
bash setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Get API Keys

### Anthropic Claude API
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new key
5. Copy it to your `.env` file

### Notion Integration
1. Go to https://www.notion.so/my-integrations
2. Click "+ New integration"
3. Name: "Healthcare UX News Agent"
4. Copy the token to your `.env` file

### News API (Optional)
1. Go to https://newsapi.org/
2. Sign up for free account
3. Copy API key to your `.env` file

## Step 3: Set Up Notion Database

### Create Database
1. Open Notion
2. Create a new page
3. Type `/database` and select "Table - Full page"
4. Name it "Healthcare UX News"

### Add Properties
Click "+ Add a property" and create:

- **Title** (already exists) - keep as is
- **URL** - Type: URL
- **Published** - Type: Date
- **Source** - Type: Text
- **Relevance Score** - Type: Number
- **Tags** - Type: Multi-select

### Share with Integration
1. Click "..." menu (top right)
2. Click "Connections"
3. Add "Healthcare UX News Agent"

### Get Database ID
1. Copy the database URL
2. Extract ID: `https://notion.so/workspace/{DATABASE_ID}?v=...`
3. Add to `.env` file

## Step 4: Configure Environment

Edit `.env` file:

```env
ANTHROPIC_API_KEY=sk-ant-...
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=abc123...

# Optional
NEWS_API_KEY=...

# Settings
AGENT_RUN_INTERVAL_HOURS=24
MAX_ARTICLES_PER_RUN=20
MIN_RELEVANCE_SCORE=0.7
```

## Step 5: Verify Setup

```bash
python -m src.main verify
```

You should see: ✓ Setup verification successful!

## Step 6: Run the Agent

### One-time run:
```bash
python -m src.main run
```

### Scheduled run (every 24 hours):
```bash
python -m src.main schedule
```

## What Happens Next?

The agent will:
1. ✅ Collect articles from RSS feeds and web search
2. ✅ Analyze each article with Claude AI
3. ✅ Score relevance to healthcare UX (0.0-1.0)
4. ✅ Extract key insights for UX leaders
5. ✅ Publish top articles to your Notion database

## Troubleshooting

### No articles appearing?
- Check logs: `python -m src.main run --log-level DEBUG`
- Try lower relevance score: edit `MIN_RELEVANCE_SCORE` in `.env`
- Verify Notion database is shared with integration

### API errors?
- Check API keys are correct in `.env`
- Verify Anthropic account has credits
- Check Notion integration has access

### Rate limits?
- Free tier limits: 50 Claude requests/min, 100 News API/day
- Reduce `MAX_ARTICLES_PER_RUN` in `.env`
- Run less frequently

## Next Steps

### Customize sources
Edit `config/sources.yaml` to add RSS feeds or keywords

### Deploy to server
Run on a cloud server for 24/7 operation:
```bash
# Using tmux or screen
tmux new -s news-agent
python -m src.main schedule
# Ctrl+B, then D to detach
```

### Set up systemd service (Linux)
See README.md for systemd service configuration

## Need Help?

- Full documentation: `README.md`
- Check logs: `--log-level DEBUG`
- Verify setup: `python -m src.main verify`

Enjoy your curated healthcare UX news! 🎉
