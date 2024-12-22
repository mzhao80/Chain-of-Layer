import json
import graphviz
import argparse
import os

def parse_taxonomy(text):
    """Parse the taxonomy text into a hierarchical structure"""
    lines = text.strip().split('\n')
    taxonomy = {}
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Split index from content
        parts = line.strip().split(' ', 1)
        if len(parts) != 2:
            continue
            
        index, content = parts
        level = len(index.rstrip('.').split('.'))
        taxonomy[index] = {
            'content': content.strip(),  # Clean up any extra whitespace
            'level': level
        }
    
    return taxonomy

def create_graph(taxonomy):
    """Create a graphviz graph from the taxonomy"""
    dot = graphviz.Digraph(comment='Taxonomy')
    dot.attr(rankdir='TB')  # Top to bottom layout
    dot.attr('node', shape='box', style='rounded')  # Use rounded boxes for nodes
    dot.attr('graph', ranksep='0.5', nodesep='0.3')  # Adjust spacing
    dot.attr('edge', arrowsize='0.5')  # Smaller arrows
    
    # Add nodes level by level
    level_nodes = {}
    max_level = max(data['level'] for data in taxonomy.values())
    
    for level in range(1, max_level + 1):
        # Create subgraph for this level to ensure same rank
        with dot.subgraph() as s:
            s.attr(rank='same')
            # Add all nodes for this level
            for index, data in taxonomy.items():
                if data['level'] == level:
                    node_id = f"{index}_{data['content']}"
                    s.node(node_id, data['content'])
                    level_nodes[index] = node_id
    
    # Add edges
    for index, data in taxonomy.items():
        if '.' in index:
            parent_index = '.'.join(index.split('.')[:-1])
            if parent_index in level_nodes:
                dot.edge(level_nodes[parent_index], level_nodes[index])
    
    return dot

def get_final_taxonomy(model_response):
    """Extract the final taxonomy from the filtered results"""
    if isinstance(model_response, list) and len(model_response) > 0:
        # Get the last conversation in the first item
        if isinstance(model_response[0], list) and len(model_response[0]) > 0:
            last_conversation = model_response[0][-1]
            # Look for the final taxonomy in the messages
            for message in reversed(last_conversation):
                if isinstance(message, dict) and 'content' in message:
                    content = message['content']
                    if '1.' in content:
                        # Extract the taxonomy part
                        start_idx = content.find('1.')
                        end_idx = content.find('Check:') if 'Check:' in content else None
                        taxonomy_text = content[start_idx:end_idx].strip()
                        return taxonomy_text
    return None

def main():
    parser = argparse.ArgumentParser(description='Visualize taxonomy from model response')
    parser.add_argument('--input_dir', type=str, required=True, help='Base directory containing results')
    parser.add_argument('--output_dir', type=str, default='visualizations', help='Output dire