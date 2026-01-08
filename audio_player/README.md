# Healthcare UX News Audio Player

A web-based audio player that reads your Notion articles aloud with full playback controls.

## Features

✅ **Full Playback Controls**
- Play/Pause with spacebar
- Skip between articles (⏮/⏭)
- 15-second skip forward/back (⏪/⏩)
- Progress bar with scrubbing
- Speed control (0.75x to 2x)

✅ **Smart Reading**
- Reads article titles, sections, and content
- Announces article number and source
- Handles product releases specially
- Skips non-text content

✅ **Keyboard Shortcuts**
- Space: Play/Pause
- ← →: Skip 15s back/forward
- ↑ ↓: Previous/Next article

✅ **Mobile Friendly**
- Responsive design
- Touch controls
- Works on iPhone/iPad/Android

## How to Use

### Option 1: Open Directly (Simple)

1. Double-click `index.html` in Finder
2. It will open in your default browser
3. Articles load automatically from Notion
4. Click play and enjoy!

### Option 2: Run with Local Server (Better)

```bash
cd ~/DUXTest/audio_player
python3 -m http.server 8000
```

Then open: http://localhost:8000

### Option 3: Deploy Online

Deploy to Netlify, Vercel, or GitHub Pages for access anywhere:

**Netlify (Free):**
```bash
cd ~/DUXTest/audio_player
netlify deploy --dir=. --prod
```

## Controls

### Mouse/Touch
- **Play/Pause button**: Start/stop playback
- **Progress bar**: Click to jump to position
- **Speed buttons**: Adjust playback speed
- **Playlist items**: Click to jump to article

### Keyboard
- `Space`: Play/Pause
- `←`: Rewind 15 seconds
- `→`: Forward 15 seconds
- `↑`: Previous article
- `↓`: Next article

## How It Works

1. **Fetches** articles from your Notion database via API
2. **Extracts** title, source, content, and tags
3. **Converts** text to speech using Web Speech API (built into browser)
4. **Plays** article content section by section
5. **Tracks** progress through each article
6. **Auto-advances** to next article when finished

## Voice Quality

The player uses your browser's built-in text-to-speech:

**Best voices:**
- **macOS Safari**: Uses Siri voices (excellent quality)
- **macOS Chrome**: Uses system voices
- **Windows**: Uses Microsoft voices
- **iOS/Android**: Uses system voices

## Customization

### Change Voices

Edit `player.js` line ~155:

```javascript
// Try to use a good English voice
const voices = speechSynthesis.getVoices();
const goodVoice = voices.find(v => v.name === 'Samantha') // macOS
                || voices.find(v => v.name === 'Microsoft Zira') // Windows
                || voices.find(v => v.lang.startsWith('en'));
```

### Change Colors

Edit `index.html` CSS section:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Change to your preferred gradient */
```

### Add Filters

Edit `player.js` Notion query (line ~60):

```javascript
body: JSON.stringify({
    sorts: [{ property: 'Published', direction: 'descending' }],
    filter: {
        property: 'Tags',
        multi_select: { contains: 'Product Release' }  // Only releases
    },
    page_size: 20
})
```

## Troubleshooting

**No sound?**
- Check browser volume
- Try clicking Play twice
- Reload the page
- Try Safari instead of Chrome

**Robotic voice?**
- macOS: System Settings → Accessibility → Spoken Content → System Voice
- Choose "Samantha" or "Alex" for better quality
- Or use Safari (has best voices)

**Articles not loading?**
- Check browser console (F12) for errors
- Verify Notion API key is correct
- Check database ID is correct
- Ensure database is shared with integration

**Progress bar not working?**
- Progress is estimated (15 seconds per section)
- Speech synthesis doesn't provide real-time progress
- This is a browser limitation

## Future Enhancements

Want these features? Let me know:
- [ ] Cloud TTS (ElevenLabs, Google) for better voices
- [ ] Download articles as MP3 files
- [ ] Offline mode with cached articles
- [ ] Chapter markers in progress bar
- [ ] Volume control
- [ ] Sleep timer
- [ ] Bookmarks/favorites

## Technical Details

- **No server required**: Runs entirely in browser
- **Direct Notion API**: Fetches articles on demand
- **Web Speech API**: Free, built-in TTS
- **Local Storage**: Remembers your position (coming soon)
- **No tracking**: 100% private

## Browser Compatibility

✅ Safari (macOS, iOS) - Best voices
✅ Chrome (desktop, Android)
✅ Edge (Windows)
✅ Firefox (with caveats)

---

Enjoy your personalized healthcare UX news podcast! 🎧
