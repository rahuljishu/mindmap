# app.py
import streamlit as st
import graphviz

def create_mindmap():
    # Create a new directed graph
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR')  # Left to right layout
    
    # Set graph attributes for better visualization
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    dot.attr('edge', color='#666666')
    
    # Add central node
    dot.node('mind_map', 'What is a\nMind Map?', fillcolor='#FF69B4', fontcolor='white')
    
    # Define main topics and their colors
    main_topics = {
        'writing': ('#48D1CC', [
            'Articles', 'Thesis', 'Novels', 'Blogs', 'Essays', 'Scripts'
        ]),
        'organizing': ('#FF6347', [
            'Structure & Relationships', 'Outline & Framework Design', 
            'Organizational Charts'
        ]),
        'more': ('#FFD700', [
            'Expressing Creativity', 'Team Building', 'Family Trees'
        ]),
        'capturing_ideas': ('#FFA500', [
            'Problem Solving', 'Projects', 'Brainstorming'
        ]),
        'planning': ('#87CEEB', [
            'Shopping Lists', 'Vacation Checklists', 'Project Management',
            'Weekly Goals', 'Family Chores', 'Homework'
        ]),
        'note_taking': ('#DDA0DD', [
            'Courses', 'Presentations', 'Lectures', 'Studying'
        ])
    }
    
    # Add main topics and their subtopics
    for topic, (color, subtopics) in main_topics.items():
        # Add main topic node
        topic_name = topic.replace('_', ' ').title()
        dot.node(topic, topic_name, fillcolor=color, fontcolor='white')
        dot.edge('mind_map', topic)
        
        # Add subtopics
        for idx, subtopic in enumerate(subtopics):
            subtopic_id = f"{topic}_{idx}"
            dot.node(subtopic_id, subtopic, fillcolor=color, fontcolor='white')
            dot.edge(topic, subtopic_id)
    
    return dot

def main():
    st.set_page_config(page_title="Mind Map Creator", layout="wide")
    
    # Add custom styling
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .main {
            padding: 2rem;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Interactive Mind Map Creator")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Mind Map View", "About"])
    
    with tab1:
        # Create and display the mind map
        mind_map = create_mindmap()
        st.graphviz_chart(mind_map)
        
        # Add download button
        st.download_button(
            label="Download Mind Map as PDF",
            data=mind_map.pipe(format='pdf'),
            file_name="mindmap.pdf",
            mime="application/pdf"
        )
    
    with tab2:
        st.markdown("""
        ### About Mind Mapping
        
        Mind mapping is a powerful brainstorming and organization tool that helps you:
        - Organize information visually
        - Generate creative ideas
        - Connect related concepts
        - Improve memory and retention
        - Plan projects effectively
        
        This tool allows you to visualize mind maps in an intuitive way. You can:
        - View the complete mind map structure
        - Download the mind map as a PDF
        - Use it for various purposes like planning, note-taking, and brainstorming
        """)

if __name__ == "__main__":
    main()
