# app.py
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import random

def generate_random_color():
    """Generate a random hex color."""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def create_mindmap():
    st.title("Interactive Mind Map Creator")
    st.sidebar.header("Mind Map Controls")

    # Create nodes
    nodes = []
    edges = []
    
    # Central node
    central_node = Node(id="mind_map", 
                       label="What is a Mind Map?",
                       size=25,
                       color="#FF69B4")  # Pink color for central node
    nodes.append(central_node)

    # Main branches
    main_topics = {
        "writing": "#48D1CC",  # Turquoise
        "organizing": "#FF6347",  # Tomato
        "more": "#FFD700",  # Gold
        "capturing_ideas": "#FFA500",  # Orange
        "planning": "#87CEEB",  # Sky Blue
        "note_taking": "#DDA0DD"  # Plum
    }

    # Add main topic nodes and connect to central node
    for topic, color in main_topics.items():
        node = Node(id=topic,
                   label=topic.replace("_", " ").title(),
                   size=20,
                   color=color)
        nodes.append(node)
        edges.append(Edge(source="mind_map", target=topic, color=color))

    # Subtopics
    subtopics = {
        "writing": ["Articles", "Thesis", "Novels", "Blogs", "Essays", "Scripts"],
        "organizing": ["Structure & Relationships", "Outline & Framework Design", "Organizational Charts"],
        "more": ["Expressing Creativity", "Team Building", "Family Trees"],
        "capturing_ideas": ["Problem Solving", "Projects", "Brainstorming"],
        "planning": ["Shopping Lists", "Vacation Checklists", "Project Management", 
                    "Weekly Goals", "Family Chores", "Homework"],
        "note_taking": ["Courses", "Presentations", "Lectures", "Studying"]
    }

    # Add subtopic nodes and connect to main topics
    for main_topic, sub_list in subtopics.items():
        main_color = main_topics[main_topic]
        for subtopic in sub_list:
            subtopic_id = f"{main_topic}_{subtopic.lower().replace(' ', '_')}"
            node = Node(id=subtopic_id,
                       label=subtopic,
                       size=15,
                       color=main_color)
            nodes.append(node)
            edges.append(Edge(source=main_topic, target=subtopic_id, color=main_color))

    # Configuration for the graph
    config = Config(width=1000,
                   height=800,
                   directed=False,
                   physics=True,
                   hierarchical=False,
                   nodeHighlightBehavior=True,
                   highlightColor="#F7A7A6",
                   collapsible=True,
                   node={'labelProperty': 'label'},
                   link={'labelProperty': 'label', 'renderLabel': False},
                   maxZoom=2,
                   minZoom=0.1,
                   staticGraphWithDragAndDrop=False,
                   staticGraph=False,
                   initialZoom=0.8)

    # Render the graph
    return agraph(nodes=nodes, 
                 edges=edges, 
                 config=config)

def main():
    st.set_page_config(layout="wide", page_title="Mind Map Creator")
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .st-emotion-cache-18ni7ap {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    create_mindmap()

if __name__ == "__main__":
    main()
