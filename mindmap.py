import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from streamlit_agraph import agraph, Node, Edge, Config
import json
from datetime import datetime
import uuid
import pandas as pd
from streamlit_javascript import st_javascript
import streamlit_nested_layout

class MindMap:
    def __init__(self):
        if 'nodes' not in st.session_state:
            st.session_state.nodes = []
        if 'edges' not in st.session_state:
            st.session_state.edges = []
        if 'selected_node' not in st.session_state:
            st.session_state.selected_node = None
        if 'node_colors' not in st.session_state:
            st.session_state.node_colors = {}
        if 'current_path' not in st.session_state:
            st.session_state.current_path = []

    def generate_id(self):
        return str(uuid.uuid4())

    def add_node(self, text, parent_id=None, color="#1f77b4"):
        node_id = self.generate_id()
        st.session_state.nodes.append({
            "id": node_id,
            "label": text,
            "color": color,
            "size": 25
        })
        if parent_id:
            st.session_state.edges.append({
                "source": parent_id,
                "target": node_id,
                "type": "STRAIGHT"
            })
        return node_id

    def remove_node(self, node_id):
        # Remove the node
        st.session_state.nodes = [n for n in st.session_state.nodes if n["id"] != node_id]
        # Remove all edges connected to this node
        st.session_state.edges = [e for e in st.session_state.edges 
                                if e["source"] != node_id and e["target"] != node_id]

    def get_node_children(self, node_id):
        return [edge["target"] for edge in st.session_state.edges if edge["source"] == node_id]

    def get_node_by_id(self, node_id):
        for node in st.session_state.nodes:
            if node["id"] == node_id:
                return node
        return None

    def export_to_json(self):
        data = {
            "nodes": st.session_state.nodes,
            "edges": st.session_state.edges
        }
        return json.dumps(data, indent=2)

    def import_from_json(self, json_str):
        try:
            data = json.loads(json_str)
            st.session_state.nodes = data["nodes"]
            st.session_state.edges = data["edges"]
            return True
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
            return False

    def render(self):
        config = Config(
            width=750,
            height=950,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#F7A7A6",
            collapsible=True
        )

        return agraph(
            nodes=[Node(**node) for node in st.session_state.nodes],
            edges=[Edge(**edge) for edge in st.session_state.edges],
            config=config
        )

def create_node_path(mindmap, text, parent_id=None):
    cols = st.columns([3, 1, 1])
    with cols[0]:
        node_text = st.text_input("Node text", text, key=f"text_{uuid.uuid4()}")
    with cols[1]:
        color = st.color_picker("Color", "#1f77b4", key=f"color_{uuid.uuid4()}")
    with cols[2]:
        if st.button("Add", key=f"add_{uuid.uuid4()}"):
            node_id = mindmap.add_node(node_text, parent_id, color)
            st.session_state.current_path.append(node_id)
            st.experimental_rerun()

def render_node_controls(mindmap, node_id):
    node = mindmap.get_node_by_id(node_id)
    if node:
        cols = st.columns([3, 1, 1, 1])
        with cols[0]:
            st.text(node["label"])
        with cols[1]:
            if st.button("Add Child", key=f"add_child_{node_id}"):
                st.session_state.current_path.append(node_id)
                st.experimental_rerun()
        with cols[2]:
            if st.button("Remove", key=f"remove_{node_id}"):
                mindmap.remove_node(node_id)
                st.experimental_rerun()
        with cols[3]:
            if st.button("Edit", key=f"edit_{node_id}"):
                st.session_state.selected_node = node_id
                st.experimental_rerun()

def main():
    st.set_page_config(layout="wide", page_title="Advanced Mindmap Creator")
    
    st.title("Advanced Interactive Mindmap Creator")
    
    mindmap = MindMap()
    
    # Main layout
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Controls")
        
        # Add root node
        if not st.session_state.nodes:
            st.write("Create root node:")
            create_node_path(mindmap, "Root")
        
        # Node controls
        st.write("Existing nodes:")
        for node in st.session_state.nodes:
            render_node_controls(mindmap, node["id"])
        
        # Import/Export
        st.subheader("Import/Export")
        
        # Export
        if st.button("Export Mindmap"):
            json_str = mindmap.export_to_json()
            st.download_button(
                "Download JSON",
                json_str,
                file_name=f"mindmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Import
        uploaded_file = st.file_uploader("Import Mindmap", type="json")
        if uploaded_file:
            json_str = uploaded_file.read().decode()
            if mindmap.import_from_json(json_str):
                st.success("Mindmap imported successfully!")
                st.experimental_rerun()
    
    with col2:
        st.subheader("Mindmap Visualization")
        mindmap.render()

if __name__ == "__main__":
    main()
