"""
Non-interactive export script - runs directly without prompts
"""

from cs_data_exporter import CSDataExporter

# Bearer token
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODZkMGM0MjMyMWNkNDZiZWFhMDU5MTUiLCJleHAiOjE3ODcxMTc1ODZ9.sHS-ZkuRjQ4gp-_hrnFeVQtVbe31Lmbln-oXXicgbUc"

print("=" * 70)
print("Creator Studio Data Exporter - Automated Run")
print("=" * 70)
print("\n📝 This will export the last 7 days of data with transcripts.\n")

# Initialize exporter
exporter = CSDataExporter(BEARER_TOKEN)

# Export last 7 days with transcripts
try:
    exporter.quick_export_last_n_days(days=7, filename="cs_export_last_7_days.xlsx")
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Your data has been exported.")
    print("=" * 70)
    print("\n📁 File created: cs_export_last_7_days.xlsx")
    print("📍 Location: /Users/noorgupta/Downloads/Cursor/csdb/")
    print("\nThe Excel file contains:")
    print("  • All videos from the last 7 days")
    print("  • Full transcripts for each video")
    print("  • Views, likes, comments, outlier scores")
    print("  • Summary statistics")
    print("\n🎉 Ready to analyze!\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPlease check:")
    print("  1. Your Bearer token is valid")
    print("  2. You have internet connection")
    print("  3. The Creator Studio API is accessible")
