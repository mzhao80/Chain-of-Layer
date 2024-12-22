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
    parser.add_argument('--output_dir', type=str, default='visualizations', help='Output directory for PDFs')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find the filtered results directory
    filtered_dir = os.path.join(args.input_dir, 'taxo_ChainofLayers_filter_init')
    if not os.path.exists(filtered_dir):
        print(f"Error: Could not find filtered results in {filtered_dir}")
        return
        
    # Find the model response file
    response_file = None
    for root, dirs, files in os.walk(filtered_dir):
        if 'model_response.json' in files:
            response_file = os.path.join(root, 'model_response.json')
            break
    
    if not response_file:
        print("Error: Could not find model_response.json in filtered results")
        return
        
    print(f"Found filtered results in: {response_file}")
    
    # Load and process the response
    with open(response_file, 'r') as f:
        model_response = json.load(f)
    
    # Get the final taxonomy
    taxonomy_text = get_final_taxonomy(model_response)
    
    if not taxonomy_text:
        print("Error: Could not find final taxonomy in the response")
        return
    
    # Parse and visualize the taxonomy
    taxonomy_dict = parse_taxonomy(taxonomy_text)
    
    if not taxonomy_dict:
        print("Error: Failed to parse taxonomy")
        return
        
    print(f"Processing final taxonomy with {len(taxonomy_dict)} nodes")
    
    # Create the graph
    dot = create_graph(taxonomy_dict)
    
    # Save the visualization
    output_path = os.path.join(args.output_dir, 'final_taxonomy')
    dot.render(output_path, format='pdf', cleanup=True)
    print(f'Generated {output_path}.pdf')

if __name__ == '__main__':
    main()
