from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
NOTION_VERSION = '2022-06-28'

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """Fetch articles from Notion database."""
    try:
        # Query Notion database
        response = requests.post(
            f'https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query',
            headers={
                'Authorization': f'Bearer {NOTION_API_KEY}',
                'Notion-Version': NOTION_VERSION,
                'Content-Type': 'application/json'
            },
            json={
                'sorts': [{'property': 'Published', 'direction': 'descending'}],
                'page_size': 20
            }
        )

        if response.status_code != 200:
            return jsonify({'error': f'Notion API error: {response.text}'}), response.status_code

        data = response.json()

        # Parse articles
        articles = []
        for page in data.get('results', []):
            article = {
                'id': page['id'],
                'title': page['properties'].get('Title', {}).get('title', [{}])[0].get('plain_text', 'Untitled'),
                'source': page['properties'].get('Source', {}).get('rich_text', [{}])[0].get('plain_text', ''),
                'tags': [tag['name'] for tag in page['properties'].get('Tags', {}).get('multi_select', [])],
                'score': page['properties'].get('Relevance Score', {}).get('number', 0),
                'url': page['properties'].get('URL', {}).get('url', '')
            }
            articles.append(article)

        return jsonify({'articles': articles})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/article/<page_id>', methods=['GET'])
def get_article_content(page_id):
    """Fetch article content blocks from Notion."""
    try:
        response = requests.get(
            f'https://api.notion.com/v1/blocks/{page_id}/children',
            headers={
                'Authorization': f'Bearer {NOTION_API_KEY}',
                'Notion-Version': NOTION_VERSION
            }
        )

        if response.status_code != 200:
            return jsonify({'error': f'Notion API error: {response.text}'}), response.status_code

        data = response.json()
        content = []

        for block in data.get('results', []):
            if block['type'] == 'heading_2':
                text = block.get('heading_2', {}).get('rich_text', [{}])[0].get('plain_text')
                if text:
                    content.append({'type': 'heading', 'text': text})
            elif block['type'] == 'paragraph':
                text = block.get('paragraph', {}).get('rich_text', [{}])[0].get('plain_text')
                if text and text.strip():
                    content.append({'type': 'text', 'text': text})
            elif block['type'] == 'callout':
                text = block.get('callout', {}).get('rich_text', [{}])[0].get('plain_text')
                if text:
                    content.append({'type': 'callout', 'text': text})

        return jsonify({'content': content})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("ERROR: Missing NOTION_API_KEY or NOTION_DATABASE_ID in .env file")
        exit(1)

    print("Starting Healthcare UX News API Server...")
    print("Audio player will be available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
