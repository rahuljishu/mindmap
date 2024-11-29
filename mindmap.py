import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.add_vertical_space import add_vertical_space
import json
from datetime import datetime
import plotly.graph_objects as go
import networkx as nx
import base64

class MindMap:
    def __init__(self):
        if 'nodes' not in st.session_state:
            st.session_state.nodes = {}
        if 'connections' not in st.session_state:
            st.session_state.connections = set()
        if 'selected_node' not in st.session_state:
            st.session_state.selected_node = None
            
    def add_node(self, text, x=0, y=0):
        node_id = str(len(st.session_state.nodes))
        st.session_state.nodes[node_id] = {
            'text': text,
            'x': x,
            'y': y
        }
        return node_id
    
    def add_connection(self, from_id, to_id):
        if from_id != to_id:
            connection = tuple(sorted([from_id, to_id]))
            st.session_state.connections.add(connection)
            return True
        return False
    
    def remove_node(self, node_id):
        if node_id in st.session_state.nodes:
            del st.session_state.nodes[node_id]
            # Remove connections involving this node
            st.session_state.connections = {
                conn for conn in st.session_state.connections 
                if node_id not in conn
            }
    
    def get_graph(self):
        G = nx.Graph()
        
        # Add nodes
        for node_id, node_data in st.session_state.nodes.items():
            G.add_node(node_id, 
                      pos=(node_data['x'], node_data['y']),
                      text=node_data['text'])
        
        # Add edges
        for conn in st.session_state.connections:
            G.add_edge(conn[0], conn[1])
        
        return G
    
    def create_visualization(self):
        if not st.session_state.nodes:
            return None
            
        G = self.get_graph()
        pos = nx.spring_layout(G)
        
        # Update node positions
        for node_id in G.nodes():
            st.session_state.nodes[node_id]['x'] = pos[node_id][0]
            st.session_state.nodes[node_id]['y'] = pos[node_id][1]
        
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
            line=dict(width=2, color='#888'),
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
                size=40,
                color='#1f77b4',
                line=dict(width=2, color='#fff')
            ))

        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=[dict(
                               text="Interactive Mindmap",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           plot_bgcolor='rgba(255,255,255,0)',
                           paper_bgcolor='rgba(255,255,255,0)',
                       ))
        
        # Make it interactive
        fig.update_layout(
            dragmode='pan',
            height=600,
        )
        
        return fig
    
    def export_data(self):
        data = {
            'nodes': st.session_state.nodes,
            'connections': list(st.session_state.connections)
        }
        return json.dumps(data, indent=2)
    
    def import_data(self, json_str):
        try:
            data = json.loads(json_str)
            st.session_state.nodes = data['nodes']
            st.session_state.connections = set(tuple(x) for x in data['connections'])
            return True
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
            return False

def main():
    st.set_page_config(layout="wide", page_title="MindMap Creator")
    
    # Initialize mindmap
    mindmap = MindMap()
    
    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
        }
        .main .block-container {
            padding-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.title("📝 Interactive MindMap Creator")
    
    # Main layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Add New Node")
        
        # Add new node
        node_text = st.text_input("Enter node text", key="new_node_text")
        if st.button("➕ Add Node", key="add_node"):
            if node_text:
                mindmap.add_node(node_text)
                st.success("Node added!")
                st.session_state.new_node_text = ""
        
        # Node connections
        if st.session_state.nodes:
            st.subheader("Connect Nodes")
            nodes = st.session_state.nodes
            node_labels = {k: v['text'] for k, v in nodes.items()}
            
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                from_node = st.selectbox("From", options=list(node_labels.keys()),
                                       format_func=lambda x: node_labels[x],
                                       key="from_node")
            with col1_2:
                to_node = st.selectbox("To", options=list(node_labels.keys()),
                                     format_func=lambda x: node_labels[x],
                                     key="to_node")
            
            if st.button("🔗 Connect Nodes"):
                if mindmap.add_connection(from_node, to_node):
                    st.success("Nodes connected!")
                else:
                    st.error("Cannot connect a node to itself!")
        
        # Export/Import
        st.subheader("Export/Import")
        if st.session_state.nodes:
            if st.button("💾 Export Mindmap"):
                json_str = mindmap.export_data()
                b64 = base64.b64encode(json_str.encode()).decode()
                href = f'<a href="data:file/json;base64,{b64}" download="mindmap.json">Download Mindmap JSON</a>'
                st.markdown(href, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Import Mindmap", type="json")
        if uploaded_file:
            json_str = uploaded_file.read().decode()
            if mindmap.import_data(json_str):
                st.success("Mindmap imported successfully!")
    
    with col2:
        # Visualization
        fig = mindmap.create_visualization()
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add some nodes to start creating your mindmap!")
            
        # Node Management
        if st.session_state.nodes:
            st.subheader("Manage Nodes")
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                node_to_edit = st.selectbox(
                    "Select node to manage",
                    options=list(st.session_state.nodes.keys()),
                    format_func=lambda x: st.session_state.nodes[x]['text']
                )
            
            with col2_2:
                if st.button("🗑️ Delete Node"):
                    mindmap.remove_node(node_to_edit)
                    st.success("Node deleted!")
                    st.experimental_rerun()
            
            # Edit node text
            new_text = st.text_input(
                "Edit node text",
                value=st.session_state.nodes[node_to_edit]['text']
            )
            if st.button("✏️ Update Node"):
                st.session_state.nodes[node_to_edit]['text'] = new_text
                st.success("Node updated!")

if __name__ == "__main__":
    main()
