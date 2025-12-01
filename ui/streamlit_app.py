"""Streamlit UI for AI Fashion Consultant"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from orchestrator import FashionAgentOrchestrator
from PIL import Image
import io

# Page config
st.set_page_config(
    page_title="AI Fashion Consultant",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
         /* -webkit-text-fill-color: transparent;  */
        margin-bottom: 2rem;
    }
    .outfit-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .stat-card {
        padding: 1rem;
        border-radius: 8px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    div[data-testid="stButton"] button {
        border: none;
        padding: 0.2rem 0.6rem;
    }
    button[title="Delete Item"] {
        color: #ff4b4b;
        font-weight: bold;
        border: 1px solid #ff4b4b !important;
    }
    button[title="Delete Item"]:hover {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    .wear-button {
        background-color: #28a745 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION CALLBACK ---
def navigate_to(page_name):
    """Callback to update page state safely"""
    st.session_state.page = page_name

# Initialize session state
if 'orchestrator' not in st.session_state:
    with st.spinner("🚀 Initializing AI Fashion Consultant..."):
        try:
            st.session_state.orchestrator = FashionAgentOrchestrator()
            st.session_state.current_outfit = None
            st.session_state.outfit_confirmed = False
            st.session_state.wardrobe_loaded = False
            st.session_state.outfit_history = []
        except Exception as e:
            st.error(f"❌ Failed to initialize: {str(e)}")
            st.stop()

# Ensure page state exists
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

def get_wardrobe_count():
    try:
        result = st.session_state.orchestrator.catalog.get_wardrobe_stats()
        return result['stats']['total_items'] if result['success'] else 0
    except:
        return 0

def get_coverage_score():
    try:
        result = st.session_state.orchestrator.catalog.analyze_wardrobe_coverage()
        return result['coverage_score'] if result['success'] else 0.0
    except:
        return 0.0

def _render_outfit_card(outfit):
    """Helper to render the visual outfit card"""
    item_cols = st.columns(3)
    
    def display_item(label, item):
        st.markdown(f"**{label}**")
        if isinstance(item, dict):
            display_text = f"{item.get('color', '').title()} {item.get('garment_type', '').title()}"
            st.write(display_text)
            img_path = item.get('image_path')
            if img_path:
                try:
                    st.image(img_path, use_column_width=True)
                except:
                    st.caption("Image not found")
        else:
            st.write(item or 'N/A')

    with item_cols[0]:
        display_item("👕 Top", outfit.get('top'))
    
    with item_cols[1]:
        display_item("👖 Bottom", outfit.get('bottom'))
    
    with item_cols[2]:
        display_item("👞 Shoes", outfit.get('shoes'))
    
    if outfit.get('outerwear'):
        st.markdown("**🧥 Outerwear:**")
        if isinstance(outfit['outerwear'], dict):
                st.write(f"{outfit['outerwear'].get('color', '').title()} {outfit['outerwear'].get('garment_type', '').title()}")
                if outfit['outerwear'].get('image_path'):
                    try:
                        st.image(outfit['outerwear']['image_path'], width=150)
                    except:
                        pass
        else:
                st.write(outfit['outerwear'])
    
    if outfit.get('accessories'):
        st.markdown(f"**📿 Accessories:** {', '.join(outfit['accessories']) if isinstance(outfit['accessories'], list) else outfit['accessories']}")

# --- PAGE FUNCTIONS ---

def show_home():
    """Home page"""
    st.markdown("## 🎯 Welcome to Your Personal AI Stylist!")
    st.markdown("Transform your wardrobe management with AI-powered outfit recommendations.")
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("👕 Wardrobe Items", get_wardrobe_count())
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("✨ Outfits Generated", len(st.session_state.outfit_history))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("📈 Coverage Score", f"{get_coverage_score():.0%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("🎯 Agents Active", "7")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    
    # UPDATED: Changed to 4 columns to include "Manage Items"
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.button(
            "➕ Add Wardrobe Items", 
            use_container_width=True, 
            type="primary",
            on_click=navigate_to,
            args=["👕 Add Wardrobe"]
        )
    
    with col2:
        # NEW BUTTON
        st.button(
            "🗑️ Manage Items", 
            use_container_width=True, 
            type="primary",
            on_click=navigate_to,
            args=["🗑️ Manage Items"]
        )
    
    with col3:
        st.button(
            "✨ Generate Outfit", 
            use_container_width=True, 
            type="primary",
            on_click=navigate_to,
            args=["✨ Generate Outfit"]
        )
    
    with col4:
        st.button(
            "🛍️ Shopping Suggestions", 
            use_container_width=True, 
            type="primary",
            on_click=navigate_to,
            args=["🛍️ Recommendations"]
        )

def show_add_wardrobe():
    """Add wardrobe items page"""
    st.markdown("## 👕 Add Wardrobe Items")
    st.markdown("Upload photos of your clothing items and let AI analyze them automatically.")
    
    st.info("💡 **Tip:** Take clear, well-lit photos with plain backgrounds for best results.")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose clothing images",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Upload one or more images of clothing items"
    )
    
    if uploaded_files:
        st.markdown(f"### 📸 {len(uploaded_files)} Images Selected")
        
        # Show preview in grid
        cols = st.columns(4)
        for idx, file in enumerate(uploaded_files[:12]):
            with cols[idx % 4]:
                image = Image.open(file)
                st.image(image, caption=file.name, use_column_width=True)
        
        if len(uploaded_files) > 12:
            st.caption(f"... and {len(uploaded_files) - 12} more images")
        
        st.markdown("---")
        
        # Process button
        if st.button("🚀 Process Images with AI", type="primary", use_container_width=True):
            with st.spinner("🔍 Analyzing images with Gemini Vision AI..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Save temp files and process
                temp_paths = []
                for idx, file in enumerate(uploaded_files):
                    progress = (idx + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {file.name}")
                    
                    temp_path = f"data/temp_{file.name}"
                    image = Image.open(file)
                    image.save(temp_path)
                    temp_paths.append(temp_path)
                
                # Process through orchestrator
                status_text.text("🤖 Running multi-agent analysis...")
                result = st.session_state.orchestrator.ingest_wardrobe(temp_paths)
                
                progress_bar.empty()
                status_text.empty()
                
                if result['success']:
                    st.success(f"✅ Successfully added {result['items_stored']} items to your wardrobe!")
                    st.balloons()
                    st.session_state.wardrobe_loaded = True
                else:
                    st.error(f"❌ Failed to process images: {result.get('message', 'Unknown error')}")

def show_manage_wardrobe():
    """Page to view and delete wardrobe items with category grouping"""
    st.markdown("## 🗑️ Manage Wardrobe")
    st.markdown("Browse items by category and click the **X** to remove them.")

    # Fetch all items
    result = st.session_state.orchestrator.catalog.get_wardrobe()
    
    if result['success'] and result['items']:
        items = result['items']
        
        # Group items by category (Garment Type)
        grouped_items = {}
        for item in items:
            category = item.get('garment_type', 'Uncategorized')
            if category not in grouped_items:
                grouped_items[category] = []
            grouped_items[category].append(item)
            
        # Display by Category
        for category, cat_items in grouped_items.items():
            st.markdown(f"### {category.title()} ({len(cat_items)})")
            st.markdown("---")
            
            # Create a grid for items (3 items per row)
            cols = st.columns(3)
            
            for idx, item in enumerate(cat_items):
                col = cols[idx % 3]
                
                with col:
                    with st.container(border=True):
                        # Top Row: ID and Delete Button (X)
                        c1, c2 = st.columns([5, 1])
                        
                        with c1:
                            header_text = f"#{item['id']} {item.get('color', '').title()}"
                            st.markdown(f"**{header_text}**")
                        
                        with c2:
                            if st.button("✕", key=f"del_{item['id']}", help="Delete Item"):
                                if hasattr(st.session_state.orchestrator, 'delete_wardrobe_item'):
                                    del_result = st.session_state.orchestrator.delete_wardrobe_item(item['id'])
                                    if del_result['success']:
                                        st.toast(f"Deleted Item #{item['id']}")
                                        st.rerun()
                                    else:
                                        st.error("Failed")
                                else:
                                    st.error("Orchestrator update needed")
                        
                        # Middle: Image
                        if item.get('image_path'):
                            try:
                                st.image(item['image_path'], use_column_width=True)
                            except:
                                st.caption("📷 Image missing")
                        else:
                            st.caption("📷 No image uploaded")
                        
                        # Bottom: Details
                        st.caption(f"{item.get('season', ['all'])[0].title()} • {item.get('formality', 'casual').title()}")

    else:
        st.info("Your wardrobe is empty. Go to 'Add Wardrobe' to get started!")

def show_generate_outfit():
    """Generate outfit page"""
    st.markdown("## ✨ Generate Today's Outfit")
    st.markdown("Get AI-powered outfit recommendations tailored to your preferences, weather, and occasion.")
    
    wardrobe_count = get_wardrobe_count()
    if wardrobe_count == 0:
        st.warning("⚠️ Your wardrobe is empty. Please add some clothing items first!")
        return
    
    if st.session_state.outfit_confirmed:
        st.success("✅ You have selected your outfit for today!")
        if st.button("Start Over (Clear Selection)"):
            st.session_state.outfit_confirmed = False
            st.session_state.current_outfit = None
            st.rerun()
        
        if st.session_state.current_outfit:
             _render_outfit_card(st.session_state.current_outfit['outfit'])
        return

    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### 🎯 Preferences")
        occasion = st.selectbox(
            "Occasion",
            ["casual", "work", "formal", "party", "date", "travel", "wedding", "festival"]
        )
        st.markdown("### 🌤️ Weather")
        st.info(f"📍 Getting weather for **{st.session_state.user_profile['city']}**...")
    
    with col1:
        btn_label = "🎨 Generate Outfit" if not st.session_state.current_outfit else "🔄 Generate Different Outfit"
        
        if st.button(btn_label, type="primary", use_container_width=True):
            with st.spinner("🤖 AI agents are styling your outfit..."):
                user_profile = {
                    **st.session_state.user_profile,
                    'occasion': occasion
                }
                
                result = st.session_state.orchestrator.generate_daily_outfit(user_profile)
                
                if result['success']:
                    st.session_state.current_outfit = result
                    st.session_state.outfit_history.append(result)
                    st.rerun()
                else:
                    st.error(f"❌ Failed: {result.get('message', 'Unknown error')}")

    if st.session_state.current_outfit:
        result = st.session_state.current_outfit
        st.markdown("---")
        st.success("✅ Outfit Suggestion Ready!")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ Wear This Today", use_container_width=True):
                if 'outfit_id' in result:
                     st.session_state.orchestrator.confirm_outfit_choice(result['outfit_id'])
                st.session_state.outfit_confirmed = True
                st.balloons()
                st.rerun()
                
        with col_b:
             st.info("Don't like it? Click 'Generate Different Outfit' above.")

        st.markdown('<div class="outfit-card">', unsafe_allow_html=True)
        st.markdown("### 👔 Your Outfit")
        
        outfit = result['outfit']
        _render_outfit_card(outfit)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 💡 Why This Outfit Works")
        st.write(result['reasoning'])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🌡️ Weather")
            st.write(f"{result['weather']['temperature']}°F, {result['weather']['description']}")
        with col2:
            st.markdown("### 🎯 Confidence")
            st.progress(result['confidence_score'])
            st.write(f"{result['confidence_score']*100:.0f}% Match")

def show_recommendations():
    """Purchase recommendations page"""
    st.markdown("## 🛍️ Smart Purchase Recommendations")
    
    col1, col2 = st.columns(2)
    with col1:
        budget = st.select_slider("Budget Range", options=["low", "moderate", "high"], value="moderate")
    with col2:
        focus_occasion = st.selectbox("Focus Occasion", ["all", "casual", "work", "formal", "party"])
    
    if st.button("🔍 Analyze Wardrobe & Get Suggestions", type="primary", use_container_width=True):
        with st.spinner("🤖 Analyzing your wardrobe with AI..."):
            user_profile = {
                **st.session_state.user_profile,
                'budget': budget,
                'occasions': ['casual', 'work'] if focus_occasion == 'all' else [focus_occasion]
            }
            
            result = st.session_state.orchestrator.get_purchase_recommendations(user_profile)
            
            if result['success']:
                st.markdown("### 📊 Wardrobe Analysis")
                analysis = result['wardrobe_analysis']
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Total Items", analysis['total_items'])
                with col2: st.metric("Coverage Score", f"{analysis['coverage_score']*100:.0f}%")
                with col3: st.metric("Gaps Found", analysis['gaps_identified'])
                
                st.markdown("### 🎯 Recommended Purchases")
                if result['recommendations']:
                    for idx, rec in enumerate(result['recommendations'][:5], 1):
                        with st.container():
                            st.markdown(f'<div class="recommendation-card">', unsafe_allow_html=True)
                            st.markdown(f"**#{idx} {rec.get('item_type', 'Item').title()}** - {rec.get('priority', 'medium').upper()} priority")
                            st.write(rec.get('reason', ''))
                            st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.success("🎉 Your wardrobe is well-stocked!")
            else:
                st.error("Failed to generate recommendations.")

def show_feedback():
    """Feedback page"""
    st.markdown("## 💬 Provide Feedback")
    
    if st.session_state.current_outfit:
        st.markdown("### Rate Your Last Outfit")
        rating = st.slider("How much did you like this outfit?", 1, 5, 3)
        feedback_text = st.text_area("Comments (optional)")
        
        if st.button("Submit Feedback", type="primary"):
            with st.spinner("Processing feedback..."):
                result = st.session_state.orchestrator.process_outfit_feedback(
                    len(st.session_state.outfit_history),
                    feedback_text if feedback_text else f"Rating: {rating}/5",
                    rating
                )
                if result['success']:
                    st.success("✅ Feedback recorded!")
                else:
                    st.error("❌ Failed to save feedback")
    else:
        st.info("Generate an outfit first to provide feedback!")

def show_analytics():
    """Analytics page"""
    st.markdown("## 📊 Wardrobe Analytics")
    
    stats_result = st.session_state.orchestrator.catalog.get_wardrobe_stats()
    coverage_result = st.session_state.orchestrator.catalog.analyze_wardrobe_coverage()
    
    if stats_result['success']:
        stats = stats_result['stats']
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Items", stats['total_items'])
        with col2: st.metric("Avg Worn", f"{stats['average_times_worn']:.1f}")
        with col3: st.metric("Categories", len(stats['by_type']))
        with col4: 
             if coverage_result['success']:
                 st.metric("Coverage", f"{coverage_result['coverage_score']*100:.0f}%")

        st.markdown("### 📦 Items by Category")
        if stats['by_type']:
            st.bar_chart(stats['by_type'])
    
    st.markdown("### 🎨 Your Style Profile")
    profile_result = st.session_state.orchestrator.personalization.get_style_profile()
    if profile_result['success']:
        profile = profile_result['style_profile']
        st.info(f"**Style Description:** {profile['description']}")
        if profile['favorite_colors']:
            st.write(f"**Favorite Colors:** {', '.join(profile['favorite_colors'])}")

def show_system_status():
    """System status page"""
    st.markdown("## ⚙️ System Status")
    
    # Get status from orchestrator
    status = st.session_state.orchestrator.get_system_status()
    st.success(f"Orchestrator: {status['status'].upper()}")

    st.markdown("### Multi-Agent Swarm Status")
    
    # Create a simple grid for agents
    agents = list(status['agents'].items())
    # Create rows of 3
    rows = [agents[i:i + 3] for i in range(0, len(agents), 3)]
    
    for row in rows:
        cols = st.columns(3)
        for idx, (agent_name, agent_info) in enumerate(row):
            with cols[idx]:
                with st.container(border=True):
                    # Header with Icon
                    icon = "🟢" if agent_info['ready'] else "🔴"
                    st.markdown(f"### {icon} {agent_info['name']}")
                    
                    # Details
                    st.caption(f"**Status:** {agent_info['status'].upper()}")
                    st.progress(100 if agent_info['ready'] else 0)
                    
                    # Capabilities (Show ALL, no truncation)
                    st.markdown("**Capabilities:**")
                    # Loop through all capabilities
                    tags = " ".join([f"`{cap}`" for cap in agent_info['capabilities']])
                    st.markdown(tags)

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">👔 AI Fashion Consultant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">Your Multi-Agent Personal Stylist</p>', unsafe_allow_html=True)
    
    # Define MAIN navigation options (excluding System Status)
    NAV_OPTIONS = ["🏠 Home", "👕 Add Wardrobe", "🗑️ Manage Items", "✨ Generate Outfit", "🛍️ Recommendations", "💬 Feedback", "📊 Analytics"]
    
    # Sidebar
    with st.sidebar:
        st.markdown("###  AI Fashion Consultant")
        st.markdown("---")
        
        # Logic to handle the radio button selection state decoupled from page state
        try:
            default_index = NAV_OPTIONS.index(st.session_state.page)
        except ValueError:
            default_index = None
            
        st.radio(
            "📍 Navigation",
            NAV_OPTIONS,
            index=default_index,
            key="nav_selection",
            on_change=lambda: navigate_to(st.session_state.nav_selection)
        )
        
        st.markdown("---")
        st.markdown("### 👤 User Profile")
        gender = st.selectbox("Gender", ["unisex", "male", "female"], key="gender_select")
        city = st.text_input("City", "New York", key="city_input")
        
        st.session_state.user_profile = {
            'gender': gender,
            'city': city
        }
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        try:
            wardrobe_count = get_wardrobe_count()
            st.metric("Wardrobe Items", wardrobe_count)
            coverage = get_coverage_score()
            st.metric("Coverage", f"{coverage:.0%}")
        except:
            st.metric("Wardrobe Items", "0")
            st.metric("Coverage", "0%")
        
        st.markdown("---")
        
        # SYSTEM STATUS BUTTON AT BOTTOM
        is_system_active = st.session_state.page == "⚙️ System Status"
        if st.button("⚙️ System Status", use_container_width=True, type="primary" if is_system_active else "secondary"):
            navigate_to("⚙️ System Status")
            st.rerun()
            
       
        st.caption("Multi-Agent AI System")
    
    # Main content routing
    current_page = st.session_state.page
    
    if current_page == "🏠 Home":
        show_home()
    elif current_page == "👕 Add Wardrobe":
        show_add_wardrobe()
    elif current_page == "🗑️ Manage Items":
        show_manage_wardrobe()
    elif current_page == "✨ Generate Outfit":
        show_generate_outfit()
    elif current_page == "🛍️ Recommendations":
        show_recommendations()
    elif current_page == "💬 Feedback":
        show_feedback()
    elif current_page == "📊 Analytics":
        show_analytics()
    elif current_page == "⚙️ System Status":
        show_system_status()

if __name__ == "__main__":
    main()