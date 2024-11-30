import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import json
import os

def create_network():
    # Create a network with pyvis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Add some physics to make it look better
    net.force_atlas_2based()
    net.show_buttons(filter_=['physics'])
    return net

def save_network(net, path='temp_network.html'):
    # Save the network to a html file
    net.save_graph(path)
    
def load_network_html(path='temp_network.html'):
    # Load the saved html file
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    # Remove the unnecessary buttons and keep only the network
    html = html.replace('height: 750px;', 'height: 600px;')
    return html

def main():
    st.set_page_config(page_title="Mind Map Creator", layout="wide")
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f5f5;
        }
        .main {
            padding: 2rem;
        }
        .stButton button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Interactive Mind Map Creator")
    
    # Initialize session state
    if 'nodes' not in st.session_state:
        st.session_state.nodes = []
    if 'edges' not in st.session_state:
        st.session_state.edges = []
    if 'central_node_added' not in st.session_state:
        st.session_state.central_node_added = False
        
    # Create two columns
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("Add Node")
        
        # Add central node first
        if not st.session_state.central_node_added:
            central_title = st.text_input("Central Topic", "What is a Mind Map?")
            if st.button("Add Central Topic"):
                st.session_state.nodes.append({
                    "id": 0,
                    "label": central_title,
                    "color": "#FF69B4"
                })
                st.session_state.central_node_added = True
                st.experimental_rerun()
        
        # Only show other options if central node is added
        if st.session_state.central_node_added:
            node_title = st.text_input("Node Title")
            
            # Create color picker for nodes
            node_color = st.color_picker("Node Color", "#1f77b4")
            
            # Parent node selection
            if st.session_state.nodes:
                parent_nodes = [node["label"] for node in st.session_state.nodes]
                parent = st.selectbox("Connect to", options=parent_nodes)
                parent_idx = parent_nodes.index(parent)
            
            if st.button("Add Node"):
                if node_title:
                    # Add node
                    new_node_id = len(st.session_state.nodes)
                    st.session_state.nodes.append({
                        "id": new_node_id,
                        "label": node_title,
                        "color": node_color
                    })
                    # Add edge
                    st.session_state.edges.append({
                        "from": parent_idx,
                        "to": new_node_id
                    })
                    st.experimental_rerun()
        
        if st.button("Clear Mind Map"):
            st.session_state.nodes = []
            st.session_state.edges = []
            st.session_state.central_node_added = False
            st.experimental_rerun()
    
    with col1:
        # Create network
        net = create_network()
        
        # Add nodes and edges from session state
        for node in st.session_state.nodes:
            net.add_node(node["id"], label=node["label"], color=node["color"])
        
        for edge in st.session_state.edges:
            net.add_edge(edge["from"], edge["to"])
        
        # Save and display network
        save_network(net)
        components.html(load_network_html(), height=600)
        
        # Clean up the temporary file
        if os.path.exists('temp_network.html'):
            os.remove('temp_network.html')

if __name__ == "__main__":
    main()
