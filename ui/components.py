"""Reusable UI components for Streamlit"""

import streamlit as st
from typing import Dict, List

def render_outfit_card(outfit: Dict, reasoning: str = "", weather: Dict = None):
    """
    Render an outfit display card
    
    Args:
        outfit: Outfit dictionary
        reasoning: Why this outfit works
        weather: Weather context
    """
    st.markdown('<div class="outfit-card">', unsafe_allow_html=True)
    
    st.markdown("### 👔 Your Outfit")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**👕 Top**")
        st.write(outfit.get('top', 'N/A'))
    
    with col2:
        st.markdown("**👖 Bottom**")
        st.write(outfit.get('bottom', 'N/A'))
    
    with col3:
        st.markdown("**👞 Shoes**")
        st.write(outfit.get('shoes', 'N/A'))
    
    if outfit.get('outerwear'):
        st.markdown(f"**🧥 Outerwear:** {outfit['outerwear']}")
    
    if outfit.get('accessories'):
        st.markdown(f"**📿 Accessories:** {', '.join(outfit['accessories'])}")
    
    if reasoning:
        st.markdown("### 💡 Why This Works")
        st.write(reasoning)
    
    if weather:
        st.markdown("### 🌤️ Weather Context")
        st.write(f"{weather['temperature']}°F, {weather['description']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_stats_card(label: str, value: str, delta: str = None):
    """Render a statistics card"""
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.metric(label, value, delta=delta)
    st.markdown('</div>', unsafe_allow_html=True)

def render_recommendation_card(rec: Dict, index: int):
    """Render a purchase recommendation card"""
    priority = rec.get('priority', 'medium')
    priority_emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
    
    st.markdown(f'<div class="recommendation-card">', unsafe_allow_html=True)
    
    st.markdown(f"### {priority_emoji} #{index} - {rec.get('item_type', 'Item').title()}")
    st.write(f"**Reason:** {rec.get('reason', 'Fills wardrobe gap')}")
    
    if rec.get('color_preference'):
        st.write(f"**Suggested Color:** {rec['color_preference'].title()}")
    
    if rec.get('estimated_price_range'):
        st.write(f"**Price Range:** {rec['estimated_price_range']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_agent_status(agent_info: Dict):
    """Render agent status display"""
    status_class = "status-active" if agent_info['ready'] else "status-inactive"
    status_text = "✅ Active" if agent_info['ready'] else "❌ Inactive"
    
    st.markdown(f'<span class="agent-status {status_class}">{status_text}</span>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Status:** {agent_info['status'].title()}")
        st.write(f"**Ready:** {'Yes' if agent_info['ready'] else 'No'}")
    
    with col2:
        st.write(f"**Capabilities:** {len(agent_info['capabilities'])}")
        if agent_info.get('model'):
            st.write(f"**Model:** {agent_info['model']}")