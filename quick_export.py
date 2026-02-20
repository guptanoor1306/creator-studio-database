"""
Quick Export Script
Simple script to quickly export CS data to Excel
"""

from cs_data_exporter import CSDataExporter
from datetime import datetime, timedelta

# PASTE YOUR BEARER TOKEN HERE
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODZkMGM0MjMyMWNkNDZiZWFhMDU5MTUiLCJleHAiOjE3ODcxMTc1ODZ9.sHS-ZkuRjQ4gp-_hrnFeVQtVbe31Lmbln-oXXicgbUc"

def main():
    """Main export function"""
    
    print("=" * 60)
    print("Creator Studio Data Exporter")
    print("=" * 60)
    print("\n📝 Note: Transcripts are automatically fetched for all videos!")
    print("   This ensures complete data but may take a few minutes.\n")
    
    # Initialize exporter
    exporter = CSDataExporter(BEARER_TOKEN)
    
    # Simple menu
    print("\nWhat would you like to export?")
    print("1. Last 7 days")
    print("2. Last 30 days")
    print("3. Custom date range")
    print("4. Today's data")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n📊 Exporting last 7 days...")
        exporter.quick_export_last_n_days(days=7)
    
    elif choice == "2":
        print("\n📊 Exporting last 30 days...")
        exporter.quick_export_last_n_days(days=30)
    
    elif choice == "3":
        start = input("Enter start date (YYYY-MM-DD): ").strip()
        end = input("Enter end date (YYYY-MM-DD): ").strip()
        
        print(f"\n📊 Exporting data from {start} to {end}...")
        videos = exporter.fetch_videos(start_date=start, end_date=end)
        if videos:
            exporter.export_to_excel(videos)
    
    elif choice == "4":
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"\n📊 Exporting today's data ({today})...")
        videos = exporter.fetch_videos(start_date=today, end_date=today)
        if videos:
            exporter.export_to_excel(videos, filename=f"today_{today}.xlsx")
    
    else:
        print("❌ Invalid choice")
        return
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
