"""Transcript cleaning and one-line short summaries for Slack."""

import os
import re
import requests as http_requests


URL_PATTERN = re.compile(r'https?://\S+|www\.\S+|bit\.ly/\S+', re.I)
BLOCK_CHAR_PATTERN = re.compile(r'[▀▄█░▬═]{4,}')
MUSIC_TAG_PATTERN = re.compile(r'\[(?:music|applause|laughter)\]', re.I)


def clean_transcript(text: str) -> str:
    """Remove URLs, decorative chars, and normalize whitespace."""
    if not text:
        return ''
    text = MUSIC_TAG_PATTERN.sub(' ', text)
    text = URL_PATTERN.sub(' ', text)
    text = BLOCK_CHAR_PATTERN.sub(' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_low_quality_transcript(text: str, title: str = '') -> bool:
    """Detect sponsor boilerplate, descriptions, or garbage transcripts."""
    if not text:
        return True
    cleaned = clean_transcript(text)
    if len(cleaned) < 40:
        return True
    if URL_PATTERN.search(text):
        return True
    if BLOCK_CHAR_PATTERN.search(text):
        return True
    if title and cleaned.lower() == title.strip().lower():
        return True
    # Common sponsor / CTA phrases in descriptions mistaken as transcript
    lower = cleaned.lower()
    sponsor_markers = (
        'find your perfect credit card',
        'we are hiring',
        'subscribe to',
        'use code ',
        'link in description',
        'webveda is the smartest subscription',
    )
    if any(marker in lower for marker in sponsor_markers) and len(cleaned) < 120:
        return True
    return False


def summarize_short_with_openai(
    transcript: str,
    title: str,
    channel: str = '',
    thumbnail_text: str = '',
) -> str:
    """Use OpenAI to produce a factual one-line summary from spoken transcript."""
    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not api_key:
        print("  ⚠️ OPENAI_API_KEY not set")
        return ''

    cleaned = clean_transcript(transcript)
    thumb = clean_transcript(thumbnail_text)
    if len(cleaned) < 40 and len(thumb) >= 20:
        cleaned = thumb

    if len(cleaned) < 40:
        print(f"  ⚠️ Transcript too short ({len(cleaned)} chars) for OpenAI: {title[:40]}")
        return ''

    model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    system_prompt = (
        "You write one-line summaries for YouTube Shorts in an internal team Slack channel. "
        "Write exactly ONE sentence, maximum 120 characters, describing the main topic or story "
        "based on the SPOKEN transcript. Ignore sponsor mentions, ads, promotional links, CTAs, "
        "intro music, and channel boilerplate. Be specific and factual about the content. "
        "Do not start with 'This video' or 'In this short'. Do not include URLs or hashtags. "
        "Never repeat or lightly rephrase the title — explain what happens in the video."
    )
    user_prompt = f"Channel: {channel or 'Unknown'}\nTitle: {title}\n\nTranscript:\n{cleaned[:6000]}"
    if thumb and thumb not in cleaned:
        user_prompt += f"\n\nOn-screen/thumbnail text (supplementary):\n{thumb[:500]}"

    try:
        response = http_requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                'max_tokens': 80,
                'temperature': 0.2,
            },
            timeout=30,
        )
        if response.status_code != 200:
            print(f"  ⚠️ OpenAI error {response.status_code}: {response.text[:200]}")
            return ''

        summary = response.json()['choices'][0]['message']['content'].strip()
        summary = summary.strip('"\'')
        summary = URL_PATTERN.sub('', summary).strip()
        if len(summary) > 140:
            summary = summary[:140].rsplit(' ', 1)[0].rstrip('.,!?') + '...'
        if title and summary.lower().strip(' .') == title.lower().strip(' .'):
            print(f"  ⚠️ OpenAI echoed title for: {title[:40]}")
            return ''
        return summary
    except Exception as e:
        print(f"  ⚠️ OpenAI summarization failed: {e}")
        return ''


def fallback_summary(transcript: str, title: str) -> str:
    """Simple fallback when OpenAI is unavailable."""
    cleaned = clean_transcript(transcript)
    if not cleaned:
        return 'Summary unavailable'
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) >= 30 and not is_low_quality_transcript(sentence, title):
            if title and sentence.lower().strip(' .') == title.lower().strip(' .'):
                continue
            if len(sentence) > 140:
                sentence = sentence[:140].rsplit(' ', 1)[0].rstrip('.,!?') + '...'
            return sentence
    return 'Summary unavailable'
