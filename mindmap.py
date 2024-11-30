import streamlit as st
import graphviz
import json
from datetime import datetime

def init_session_state():
    if 'nodes' not in st.session_state:
        st.session_state.nodes = []
    if 'connections' not in st.session_state:
        st.session_state.connections = []
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None

def create_mindmap(nodes, connections):
    # Create a new directed graph
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR')
    
    # Add nodes
    for node in nodes:
        dot.node(node['id'], node['text'], 
                shape='box', 
                style='rounded,filled', 
                fillcolor='lightblue')
    
    # Add connections
    for conn in connections:
        dot.edge(conn['from'], conn['to'])
    
    return dot

def export_mindmap_data():
    data = {
        'nodes': st.session_state.nodes,
        'connections': st.session_state.connections
    }
    return json.dumps(data, indent=2)

def main():
    st.title("Interactive Mindmap Creator")
    
    # Initialize session state
    init_session_state()
    
    # Sidebar for adding nodes and connections
    with st.sidebar:
        st.header("Add New Node")
        node_text = st.text_input("Node Text")
        if st.button("Add Node"):
            node_id = f"node_{len(st.session_state.nodes)}"
            st.session_state.nodes.append({
                'id': node_id,
                'text': node_text
            })
        
        st.header("Add Connection")
        if st.session_state.nodes:
            node_ids = [node['id'] for node in st.session_state.nodes]
            from_node = st.selectbox("From Node", node_ids, key='from_node')
            to_node = st.selectbox("To Node", node_ids, key='to_node')
            
            if st.button("Add Connection"):
                if from_node != to_node:
                    new_connection = {'from': from_node, 'to': to_node}
                    if new_connection not in st.session_state.connections:
                        st.session_state.connections.append(new_connection)
                else:
                    st.warning("Cannot connect a node to itself!")
        else:
            st.warning("Add some nodes first!")
    
    # Main area for displaying the mindmap
    if st.session_state.nodes:
        try:
            mindmap = create_mindmap(st.session_state.nodes, st.session_state.connections)
            st.graphviz_chart(mindmap)
            
            # Export options
            st.header("Export Options")
            
            # Download as JSON
            json_data = export_mindmap_data()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="Download Mindmap Data (JSON)",
                data=json_data,
                file_name=f"mindmap_{timestamp}.json",
                mime="application/json"
            )
            
            # Download as DOT file
            st.download_button(
                label="Download Mindmap (DOT)",
                data=mindmap.source,
                file_name=f"mindmap_{timestamp}.dot",
                mime="text/vnd.graphviz"
            )
            
            # Clear mindmap button
            if st.button("Clear Mindmap"):
                st.session_state.nodes = []
                st.session_state.connections = []
                st.experimental_rerun()
                
        except Exception as e:
            st.error(f"Error creating mindmap: {str(e)}")
    else:
        st.info("Start by adding some nodes in the sidebar!")

if __name__ == "__main__":
    main()
