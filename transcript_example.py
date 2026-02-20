"""
Transcript Fetching Example
Shows how transcripts are automatically fetched and included in exports
"""

from cs_data_exporter import CSDataExporter

# Replace with your actual Bearer token
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR_TOKEN_HERE"

# Initialize the exporter
exporter = CSDataExporter(BEARER_TOKEN)

print("=" * 70)
print("TRANSCRIPT FETCHING DEMO")
print("=" * 70)

# ===== EXAMPLE 1: With Transcripts (Default) =====
print("\n📝 EXAMPLE 1: Fetching videos WITH transcripts (default behavior)")
print("-" * 70)

videos_with_transcripts = exporter.fetch_videos(
    start_date="2026-01-18",
    end_date="2026-01-19",
    limit=5  # Just fetch 5 videos for demo
)

print(f"\nFetched {len(videos_with_transcripts)} videos")

# Show transcript data for first video
if videos_with_transcripts:
    first_video = videos_with_transcripts[0]
    print(f"\nFirst video: {first_video.get('title', 'N/A')}")
    print(f"Transcript available: {'Yes' if first_video.get('transcript_text') else 'No'}")
    
    if first_video.get('transcript_text'):
        transcript_preview = first_video.get('transcript_text', '')[:200]
        print(f"Transcript preview: {transcript_preview}...")
        print(f"Transcript language: {first_video.get('transcript_language', 'N/A')}")

# Export to Excel
exporter.export_to_excel(
    videos_with_transcripts,
    filename="with_transcripts_demo.xlsx"
)

# ===== EXAMPLE 2: Without Transcripts (Faster) =====
print("\n\n⚡ EXAMPLE 2: Fetching videos WITHOUT transcripts (faster)")
print("-" * 70)

videos_without_transcripts = exporter.fetch_videos(
    start_date="2026-01-18",
    end_date="2026-01-19",
    limit=5,
    include_transcripts=False  # Skip transcripts for faster export
)

print(f"\nFetched {len(videos_without_transcripts)} videos (no transcripts)")

# Export to Excel
exporter.export_to_excel(
    videos_without_transcripts,
    filename="without_transcripts_demo.xlsx"
)

print("\n" + "=" * 70)
print("✅ DEMO COMPLETE!")
print("=" * 70)
print("\nCheck the generated Excel files:")
print("  - with_transcripts_demo.xlsx (includes transcript column)")
print("  - without_transcripts_demo.xlsx (empty transcript column)")
print("\n💡 TIP: Use include_transcripts=False when you need quick exports")
print("        without transcript data.\n")
