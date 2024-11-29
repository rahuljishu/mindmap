import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.add_vertical_space import add_vertical_space
import json
from datetime import datetime
import uuid
import plotly.graph_objects as go
import networkx as nx

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
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None
    if 'connecting_mode' not in st.session_state:
        st.session_state.connecting_mode = False
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'

def create_mindmap_graph():
    G = nx.Graph()
    
    # Add nodes
    for node_id, node in st.session_state.nodes.items():
        G.add_node(node_id, pos=(node.x, node.y), text=node.text)
    
    # Add edges
    for node_id, node in st.session_state.nodes.items():
        for connection in node.connections:
            if connection in st.session_state.nodes:
                G.add_edge(node_id, connection)
    
    return G

def create_plotly_figure(G):
    pos = nx.get_node_attributes(G, 'pos')
    
    # Create edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    # Create nodes
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(G.nodes[node]['text'])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="bottom center",
        marker=dict(
            showscale=False,
            size=30,
            line_width=2))

    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=0, l=0, r=0, t=0),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                   )
    
    # Make it interactive
    fig.update_layout(
        dragmode='pan',
        clickmode='event+select'
    )
    
    return fig

def main():
    st.set_page_config(layout="wide", page_title="Interactive Mindmap")
    
    init_session_state()
    
    st.title("Interactive Mindmap Creator")
    
    # Main layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Controls")
        
        # Add new node
        new_node_text = st.text_input("Node Text")
        if st.button("Add Node"):
            if new_node_text:
                new_node = MindmapNode(new_node_text, 
                                     x=len(st.session_state.nodes) * 1.0,
                                     y=len(st.session_state.nodes) * 1.0)
                st.session_state.nodes[new_node.id] = new_node
                st.success(f"Added node: {new_node_text}")
        
        # Node selection for connections
        if st.session_state.nodes:
            st.subheader("Connect Nodes")
            
            node_names = {node_id: node.text for node_id, node 
                         in st.session_state.nodes.items()}
            
            source_node = st.selectbox("From Node", 
                                     options=list(node_names.keys()),
                                     format_func=lambda x: node_names[x],
                                     key="source")
            
            target_node = st.selectbox("To Node", 
                                     options=list(node_names.keys()),
                                     format_func=lambda x: node_names[x],
                                     key="target")
            
            if st.button("Connect Nodes"):
                if source_node != target_node:
                    source = st.session_state.nodes[source_node]
                    if target_node not in source.connections:
                        source.connections.append(target_node)
                        st.success("Nodes connected!")
                else:
                    st.error("Cannot connect a node to itself!")
        
        # Export/Import
        st.subheader("Export/Import")
        
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
    
    with col2:
        st.subheader("Mindmap Visualization")
        
        if st.session_state.nodes:
            # Create and display the graph
            G = create_mindmap_graph()
            fig = create_plotly_figure(G)
            
            # Make the plot interactive
            selected_points = plotly_events(fig, click_event=True)
            
            if selected_points:
                point = selected_points[0]
                node_idx = point['pointIndex']
                node_id = list(st.session_state.nodes.keys())[node_idx]
                st.session_state.selected_node = node_id
        else:
            st.info("Add some nodes to start creating your mindmap!")
        
        # Node editing
        if st.session_state.selected_node:
            st.subheader("Edit Selected Node")
            node = st.session_state.nodes[st.session_state.selected_node]
            
            new_text = st.text_input("Edit Text", node.text)
            if st.button("Update Node"):
                node.text = new_text
                st.success("Node updated!")
            
            if st.button("Delete Node"):
                # Remove connections to this node
                for other_node in st.session_state.nodes.values():
                    if st.session_state.selected_node in other_node.connections:
                        other_node.connections.remove(st.session_state.selected_node)
                
                # Remove the node
                del st.session_state.nodes[st.session_state.selected_node]
                st.session_state.selected_node = None
                st.success("Node deleted!")
                st.experimental_rerun()

if __name__ == "__main__":
    main()
