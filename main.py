"""Main CLI interface for AI Fashion Consultant"""

import os
import sys
import logging
from pathlib import Path
from orchestrator import FashionAgentOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                                                           ║
    ║              AI FASHION CONSULTANT                        ║
    ║           Multi-Agent Personal Stylist                    ║
    ║                                                           ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_menu():
    """Print main menu"""
    menu = """
    ┌───────────────────────────────────────┐
    │          MAIN MENU                    │
    ├───────────────────────────────────────┤
    │  1. Add Wardrobe Items                │
    │  2. Generate Daily Outfit             │
    │  3. Get Purchase Recommendations      │
    │  4. View Wardrobe Statistics          │
    │  5. Provide Outfit Feedback           │
    │  6. View Style Profile                │
    │  7. Seasonal Rotation                 │
    │  8. System Status                     │
    │  9. Exit                              │
    └───────────────────────────────────────┘
    """
    print(menu)

def add_wardrobe_items(orchestrator):
    """Add items to wardrobe"""
    print("\n📸 ADD WARDROBE ITEMS")
    print("=" * 60)
    
    # Check if sample wardrobe exists
    sample_dir = Path("data/sample_wardrobe")
    if sample_dir.exists() and any(sample_dir.iterdir()):
        print(f"\n✓ Found sample wardrobe directory: {sample_dir}")
        use_sample = input("Use sample images? (y/n): ").lower()
        
        if use_sample == 'y':
            image_files = list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.png"))
            if image_files:
                print(f"\n📂 Processing {len(image_files)} images...")
                image_paths = [str(f) for f in image_files[:10]]  # Limit to 10 for demo
                
                result = orchestrator.ingest_wardrobe(image_paths)
                
                if result['success']:
                    print(f"\n✓ SUCCESS!")
                    print(f"   Images processed: {result['images_processed']}")
                    print(f"   Items stored: {result['items_stored']}")
                    print(f"   Total wardrobe: {result['wardrobe_stats']['total_items']} items")
                else:
                    print(f"\n✗ Failed: {result['message']}")
                return
    
    # Manual entry
    print("\nEnter image paths (one per line, empty line to finish):")
    image_paths = []
    while True:
        path = input("Image path: ").strip()
        if not path:
            break
        if os.path.exists(path):
            image_paths.append(path)
            print(f"  ✓ Added: {path}")
        else:
            print(f"  ✗ File not found: {path}")
    
    if image_paths:
        print(f"\n📂 Processing {len(image_paths)} images...")
        result = orchestrator.ingest_wardrobe(image_paths)
        
        if result['success']:
            print(f"\n✓ SUCCESS!")
            print(f"   Items stored: {result['items_stored']}")
        else:
            print(f"\n✗ Failed: {result['message']}")
    else:
        print("\n⚠ No images provided")

def generate_daily_outfit(orchestrator):
    """Generate outfit for today"""
    print("\n👔 GENERATE DAILY OUTFIT")
    print("=" * 60)
    
    # Get user preferences
    print("\nProfile Setup:")
    gender = input("Gender (male/female/unisex) [unisex]: ").strip() or "unisex"
    occasion = input("Occasion (casual/work/formal/party) [casual]: ").strip() or "casual"
    city = input("City for weather [New York]: ").strip() or "New York"
    
    user_profile = {
        'gender': gender,
        'occasion': occasion,
        'city': city
    }
    
    print("\n🎨 Generating outfit...")
    result = orchestrator.generate_daily_outfit(user_profile)
    
    if result['success']:
        print("\n✓ OUTFIT GENERATED!")
        print("=" * 60)
        
        outfit = result['outfit']
        print(f"\n👕 Top: {outfit.get('top', 'N/A')}")
        print(f"👖 Bottom: {outfit.get('bottom', 'N/A')}")
        print(f"👞 Shoes: {outfit.get('shoes', 'N/A')}")
        if outfit.get('outerwear'):
            print(f"🧥 Outerwear: {outfit['outerwear']}")
        if outfit.get('accessories'):
            print(f"📿 Accessories: {', '.join(outfit['accessories'])}")
        
        print(f"\n💡 REASONING:")
        print(f"   {result['reasoning']}")
        
        print(f"\n🌤 WEATHER:")
        weather = result['weather']
        print(f"   {weather['temperature']}°F, {weather['description']}")
        
        print(f"\n🎯 CONFIDENCE: {result['confidence_score']*100:.0f}%")
        
        if result.get('styling_tips'):
            print(f"\n💎 STYLING TIPS:")
            for tip in result['styling_tips']:
                print(f"   • {tip}")
        
    else:
        print(f"\n✗ Failed: {result['message']}")

def get_purchase_recommendations(orchestrator):
    """Get shopping recommendations"""
    print("\n🛍️ PURCHASE RECOMMENDATIONS")
    print("=" * 60)
    
    gender = input("Gender (male/female/unisex) [unisex]: ").strip() or "unisex"
    budget = input("Budget (low/moderate/high) [moderate]: ").strip() or "moderate"
    
    user_profile = {
        'gender': gender,
        'budget': budget,
        'occasions': ['casual', 'work']
    }
    
    print("\n🔍 Analyzing wardrobe gaps...")
    result = orchestrator.get_purchase_recommendations(user_profile)
    
    if result['success']:
        print("\n✓ RECOMMENDATIONS:")
        print("=" * 60)
        
        analysis = result['wardrobe_analysis']
        print(f"\n📊 Wardrobe Coverage: {analysis['coverage_score']*100:.0f}%")
        print(f"   Total Items: {analysis['total_items']}")
        print(f"   Gaps Identified: {analysis['gaps_identified']}")
        
        recommendations = result['recommendations']
        if recommendations:
            print(f"\n🎯 TOP RECOMMENDATIONS:")
            for idx, rec in enumerate(recommendations[:5], 1):
                print(f"\n{idx}. {rec.get('item_type', 'Item').upper()}")
                print(f"   Priority: {rec.get('priority', 'medium')}")
                print(f"   Reason: {rec.get('reason', 'Fills wardrobe gap')}")
                if rec.get('color_preference'):
                    print(f"   Suggested Color: {rec['color_preference']}")
                if rec.get('estimated_price_range'):
                    print(f"   Price Range: {rec['estimated_price_range']}")
        else:
            print("\n✓ Your wardrobe is well-stocked!")
    else:
        print(f"\n✗ Failed: {result['message']}")

def view_wardrobe_stats(orchestrator):
    """View wardrobe statistics"""
    print("\n📊 WARDROBE STATISTICS")
    print("=" * 60)
    
    stats_result = orchestrator.catalog.get_wardrobe_stats()
    coverage_result = orchestrator.catalog.analyze_wardrobe_coverage()
    
    if stats_result['success']:
        stats = stats_result['stats']
        
        print(f"\n📦 Total Items: {stats['total_items']}")
        print(f"📈 Average Times Worn: {stats['average_times_worn']}")
        
        print(f"\n📋 BY CATEGORY:")
        for category, count in sorted(stats['by_type'].items()):
            print(f"   {category.title()}: {count}")
        
        if coverage_result['success']:
            print(f"\n🎯 COVERAGE ANALYSIS:")
            print(f"   Coverage Score: {coverage_result['coverage_score']*100:.0f}%")
            
            gaps = coverage_result.get('gaps', {})
            if gaps:
                print(f"\n⚠️  GAPS DETECTED:")
                for category, needed in gaps.items():
                    print(f"   Need {needed} more {category}(s)")
    else:
        print(f"\n✗ Failed to retrieve statistics")

def provide_feedback(orchestrator):
    """Provide feedback on outfit"""
    print("\n💬 PROVIDE OUTFIT FEEDBACK")
    print("=" * 60)
    
    outfit_id = input("Outfit ID (or press Enter for last outfit): ").strip()
    outfit_id = int(outfit_id) if outfit_id else 1
    
    print("\nRate the outfit (1-5): ")
    rating = int(input("Rating: ").strip())
    
    feedback_text = input("Comments (optional): ").strip()
    
    if not feedback_text:
        if rating >= 4:
            feedback_text = "I loved this outfit!"
        elif rating >= 3:
            feedback_text = "It was okay."
        else:
            feedback_text = "Not my style."
    
    print("\n💾 Processing feedback...")
    result = orchestrator.process_outfit_feedback(outfit_id, feedback_text, rating)
    
    if result['success']:
        print(f"\n✓ FEEDBACK RECORDED!")
        print(f"   Sentiment: {result.get('sentiment', 'neutral')}")
        print(f"   Preferences Updated: {'Yes' if result.get('preferences_updated') else 'No'}")
    else:
        print(f"\n✗ Failed: {result['message']}")

def view_style_profile(orchestrator):
    """View learned style profile"""
    print("\n🎨 YOUR STYLE PROFILE")
    print("=" * 60)
    
    profile_result = orchestrator.personalization.get_style_profile()
    
    if profile_result['success']:
        profile = profile_result['style_profile']
        
        print(f"\n📝 Description: {profile['description']}")
        print(f"\n🎯 Confidence: {profile['confidence']*100:.0f}%")
        print(f"   (Based on {profile['total_feedbacks']} feedbacks)")
        
        if profile['favorite_colors']:
            print(f"\n❤️  Favorite Colors:")
            for color in profile['favorite_colors']:
                print(f"   • {color.title()}")
        
        if profile['avoided_colors']:
            print(f"\n🚫 Avoided Colors:")
            for color in profile['avoided_colors']:
                print(f"   • {color.title()}")
        
        if profile['preferred_styles']:
            print(f"\n✨ Preferred Styles:")
            for style in profile['preferred_styles']:
                print(f"   • {style.title()}")
    else:
        print("\n⚠️  No style profile yet - provide more feedback to build your profile!")

def seasonal_rotation(orchestrator):
    """Run seasonal rotation"""
    print("\n🍂 SEASONAL ROTATION")
    print("=" * 60)
    
    print("\nSelect current season:")
    print("1. Spring")
    print("2. Summer")
    print("3. Fall")
    print("4. Winter")
    
    choice = input("\nChoice: ").strip()
    seasons = {
        '1': 'spring',
        '2': 'summer',
        '3': 'fall',
        '4': 'winter'
    }
    
    season = seasons.get(choice, 'spring')
    
    print(f"\n🔄 Rotating wardrobe for {season}...")
    result = orchestrator.run_seasonal_rotation(season)
    
    if result['success']:
        print(f"\n✓ ROTATION COMPLETE!")
        print(f"   Active Items: {result['active_items']}")
        print(f"   Storage Items: {result['storage_items']}")
        print(f"   Rarely Worn: {result['rarely_worn']}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        recs = result.get('recommendations', {})
        if recs.get('consider_donating'):
            print(f"   Consider donating {len(recs['consider_donating'])} rarely worn items")
    else:
        print(f"\n✗ Failed: {result['message']}")

def system_status(orchestrator):
    """Show system status"""
    print("\n⚙️  SYSTEM STATUS")
    print("=" * 60)
    
    status = orchestrator.get_system_status()
    
    print(f"\n🤖 Orchestrator: {status['status'].upper()}")
    print(f"\n📋 AGENTS:")
    
    for agent_name, agent_info in status['agents'].items():
        status_icon = "✓" if agent_info['ready'] else "✗"
        print(f"   {status_icon} {agent_info['name']}: {agent_info['status']}")
        print(f"      Capabilities: {len(agent_info['capabilities'])}")

def main():
    """Main application loop"""
    print_banner()
    
    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️  WARNING: GEMINI_API_KEY not found in environment!")
        print("   Please set your API key in .env file")
        print("   Copy .env.example to .env and add your key")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Initialize orchestrator
    print("\n🚀 Initializing AI Fashion Consultant...")
    try:
        orchestrator = FashionAgentOrchestrator()
        print("✓ All systems ready!\n")
    except Exception as e:
        print(f"\n✗ Initialization failed: {str(e)}")
        return
    
    # Main loop
    while True:
        print_menu()
        choice = input("\nSelect option (1-9): ").strip()
        
        try:
            if choice == '1':
                add_wardrobe_items(orchestrator)
            elif choice == '2':
                generate_daily_outfit(orchestrator)
            elif choice == '3':
                get_purchase_recommendations(orchestrator)
            elif choice == '4':
                view_wardrobe_stats(orchestrator)
            elif choice == '5':
                provide_feedback(orchestrator)
            elif choice == '6':
                view_style_profile(orchestrator)
            elif choice == '7':
                seasonal_rotation(orchestrator)
            elif choice == '8':
                system_status(orchestrator)
            elif choice == '9':
                print("\n👋 Thank you for using AI Fashion Consultant!")
                print("   Stay stylish! ✨\n")
                break
            else:
                print("\n⚠️  Invalid option. Please select 1-9.")
            
            input("\nPress Enter to continue...")
            print("\n" * 2)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()