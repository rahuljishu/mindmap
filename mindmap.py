import streamlit as st
from streamlit_draggable import st_draggable
from streamlit_custom_notification_box import custom_notification_box
import json
from datetime import datetime
import uuid

class MindmapNode:
    def __init__(self, text="", x=0, y=0):
        self.id = str(uuid.uuid4())
        self.text = text
        self.x = x
        self.y = y
        self.connections = []

def init_session_state():
    if 'nodes' not in st.session_state:
        st.session_state.nodes = {}
    if 'dragging' not in st.session_state:
        st.session_state.dragging = None
    if 'connecting' not in st.session_state:
        st.session_state.connecting = None
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'

def create_custom_css():
    return """
    <style>
        .mindmap-node {
            background-color: #ffffff;
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 10px;
            margin: 5px;
            cursor: move;
            position: absolute;
            min-width: 100px;
            max-width: 200px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        
        .mindmap-node:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transform: translateY(-2px);
        }
        
        .mindmap-canvas {
            position: relative;
            width: 100%;
            height: 800px;
            background-color: #f5f5f5;
            border-radius: 15px;
            overflow: hidden;
        }
        
        .connection-line {
            position: absolute;
            height: 2px;
            background-color: #4CAF50;
            transform-origin: left center;
            pointer-events: none;
        }
        
        .node-controls {
            display: flex;
            gap: 5px;
            margin-top: 5px;
        }
        
        .control-button {
            padding: 2px 8px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .connect-button {
            background-color: #2196F3;
            color: white;
        }
        
        .delete-button {
            background-color: #f44336;
            color: white;
        }
        
        .floating-menu {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
    </style>
    """

def main():
    st.set_page_config(layout="wide", page_title="Drag & Drop Mindmap")
    
    init_session_state()
    st.markdown(create_custom_css(), unsafe_allow_html=True)
    
    st.title("Interactive Drag & Drop Mindmap Creator")
    
    # Main layout with sidebar
    with st.sidebar:
        st.header("Controls")
        
        # Add new node
        new_node_text = st.text_input("New Node Text")
        if st.button("Add Node"):
            new_node = MindmapNode(new_node_text, x=50, y=50)
            st.session_state.nodes[new_node.id] = new_node
        
        # Theme switcher
        theme = st.selectbox("Theme", ['light', 'dark'], 
                           index=0 if st.session_state.theme == 'light' else 1)
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.experimental_rerun()
        
        # Export/Import
        if st.button("Export Mindmap"):
            data = {
                'nodes': {
                    nid: {
                        'text': node.text,
                        'x': node.x,
                        'y': node.y,
                        'connections': node.connections
                    } for nid, node in st.session_state.nodes.items()
                }
            }
            st.download_button(
                "Download JSON",
                json.dumps(data, indent=2),
                file_name=f"mindmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        uploaded_file = st.file_uploader("Import Mindmap", type="json")
        if uploaded_file:
            try:
                data = json.loads(uploaded_file.read())
                st.session_state.nodes = {
                    nid: MindmapNode(
                        node['text'],
                        node['x'],
                        node['y']
                    ) for nid, node in data['nodes'].items()
                }
                for nid, node_data in data['nodes'].items():
                    st.session_state.nodes[nid].connections = node_data['connections']
                st.success("Mindmap imported successfully!")
            except Exception as e:
                st.error(f"Error importing mindmap: {str(e)}")
    
    # Main canvas
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown('<div class="mindmap-canvas">', unsafe_allow_html=True)
        
        # Render nodes
        for node_id, node in st.session_state.nodes.items():
            dragged = st_draggable(
                key=f"node_{node_id}",
                data={"text": node.text, "id": node_id},
                container_class="mindmap-node",
            )
            
            if dragged:
                node.x = dragged['x']
                node.y = dragged['y']
            
            # Render node content
            st.markdown(f"""
                <div style="position: absolute; left: {node.x}px; top: {node.y}px;">
                    <div class="mindmap-node">
                        <div>{node.text}</div>
                        <div class="node-controls">
                            <button class="control-button connect-button" 
                                    onclick="connect('{node_id}')">
                                Connect
                            </button>
                            <button class="control-button delete-button" 
                                    onclick="deleteNode('{node_id}')">
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Render connections
        for node_id, node in st.session_state.nodes.items():
            for connection in node.connections:
                if connection in st.session_state.nodes:
                    target = st.session_state.nodes[connection]
                    # Calculate line properties
                    dx = target.x - node.x
                    dy = target.y - node.y
                    length = (dx**2 + dy**2)**0.5
                    angle = math.atan2(dy, dx)
                    
                    st.markdown(f"""
                        <div class="connection-line"
                             style="left: {node.x}px;
                                    top: {node.y}px;
                                    width: {length}px;
                                    transform: rotate({angle}rad);">
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Selected Node")
        if st.session_state.dragging:
            node = st.session_state.nodes[st.session_state.dragging]
            st.write(f"Text: {node.text}")
            st.write(f"Position: ({node.x}, {node.y})")
            if st.button("Edit Text"):
                new_text = st.text_input("New Text", node.text)
                if st.button("Save"):
                    node.text = new_text

if __name__ == "__main__":
    main()
