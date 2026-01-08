# Competitor Product Release Tracking

The Healthcare UX News Agent automatically tracks and analyzes product releases from major competitors in healthcare and life sciences technology.

## Tracked Companies

### Tech Giants
- **Google** (Google Cloud, Google Health)
- **Microsoft** (Microsoft Healthcare, Cloud for Healthcare)
- **IBM** (Watson Health, IBM Cloud)
- **SAP** (SAP Health)
- **Salesforce** (Health Cloud)
- **AWS** (Amazon Web Services Healthcare)

### Healthcare/Life Sciences Firms
- **Epic** (Epic Systems)
- **Veeva Systems**
- **Medidata** (Dassault Systèmes)
- **Qlik** (Healthcare Solutions)
- **Informatica**
- **Philips** (Philips Healthcare)

## What Gets Tracked

The agent looks for announcements containing these keywords:
- Announces
- Launches
- Releases
- Introduces
- Unveils
- New feature
- New product
- Update
- Available now
- General availability
- Beta/Preview

## How It Works

### 1. Collection
- Searches News API for company announcements
- Checks company blogs and RSS feeds
- Looks back 14 days for releases (2x normal article window)
- Filters for healthcare/life sciences relevance

### 2. Analysis
The agent uses a specialized Claude AI prompt for product releases that:
- Summarizes what was released (1-2 sentences)
- Identifies UX implications for your team
- Extracts competitive insights
- Scores relevance for UX leaders (0.0-1.0)
- Tags by product category and company

### 3. Notion Formatting
Product releases get special treatment in Notion:
- 🚀 Blue callout badge showing "Product Release from [Company]"
- **What Was Released** section with brief summary
- **UX Implications & Competitive Insights** section with bullet points
- Company name in tags for easy filtering
- Same metadata as regular articles (date, score, URL)

## Example Output

```
🚀 Product Release from Microsoft

Title: Microsoft Announces New AI Features for Healthcare Cloud

What Was Released
Microsoft launched three new AI-powered features for their Cloud for
Healthcare platform, focusing on clinical documentation automation and
patient engagement tools.

UX Implications & Competitive Insights
• Automated clinical documentation reduces manual data entry - consider
  similar workflow optimizations for Oracle Health
• Patient engagement tools use conversational AI - trend toward more
  natural language interfaces in healthcare
• Integration with existing EHR systems via FHIR standards - highlights
  importance of interoperability in competitive positioning

Relevance Score: 0.85
Tags: Product Release, Microsoft, AI, Clinical Workflow, EHR Integration
```

## Customization

### Add/Remove Companies

Edit `src/config/settings.py`:

```python
competitor_companies: List[dict] = Field(default_factory=lambda: [
    {
        "name": "Your Company",
        "aliases": ["Company Alias 1", "Company Alias 2"],
        "blog_url": "https://company.com/blog"
    },
    # Add more companies here
])
```

### Adjust Release Keywords

Edit `src/config/settings.py`:

```python
release_keywords: List[str] = Field(default_factory=lambda: [
    "announces",
    "launches",
    # Add your keywords here
])
```

### Filter by Company in Notion

Use Notion's filter feature:
1. Click "Filter" in your database
2. Add filter: "Tags" → "Contains" → "Company Name"
3. View only releases from specific competitors

### Change Lookback Window

In `src/agents/healthcare_news_agent.py`, line 65:

```python
releases = self._collect_releases(days_back * 2)  # Default: 2x article window
```

Change the multiplier to adjust how far back to search for releases.

## Rate Limits

### News API (Free Tier)
- 100 requests per day
- The agent searches for ~3 keywords × 12 companies = ~36 requests per run
- Runs 2-3 times per day maximum with free tier

### Upgrade Options
- News API Developer ($449/month): 250,000 requests/month
- Or implement additional scrapers (RSS, direct API integrations)

## Competitive Intelligence Tips

### Weekly Review
1. Filter Notion by "Product Release" tag
2. Sort by "Relevance Score" (highest first)
3. Look for patterns across companies
4. Note UX trends or approaches

### Track by Category
Create views in Notion filtered by:
- "AI" or "Machine Learning" tags
- "Patient Experience" tags
- "Clinical Workflow" tags
- Specific competitor names

### Share with Team
- Export high-relevance releases to slides
- Share Notion database with UX team
- Set up Notion notifications for new releases
- Create weekly digest of top 5 releases

## Privacy & Ethics

- Only tracks publicly announced product information
- No scraping of private or confidential data
- All sources are public blogs, news sites, and press releases
- Respects robots.txt and rate limits

## Troubleshooting

### Not finding any releases?
- Verify News API key is configured
- Check that companies have made recent announcements
- Lower `MIN_RELEVANCE_SCORE` to see more results
- Increase lookback window (default: 14 days)

### Too many irrelevant releases?
- Raise `MIN_RELEVANCE_SCORE` in `.env`
- The agent filters for healthcare/life sciences keywords
- Claude AI removes non-UX-related announcements

### Missing a specific company?
- Add company to `competitor_companies` in settings
- Include company aliases for better detection
- Add company blog URL if they have an RSS feed

## Future Enhancements

Potential additions:
- [ ] Direct API integrations with company developer blogs
- [ ] GitHub release tracking for open-source healthcare projects
- [ ] Conference/event tracking (HIMSS, HLTH, etc.)
- [ ] Patent filing monitoring
- [ ] Acquisition and partnership announcements
- [ ] Leadership changes at competitor UX teams
