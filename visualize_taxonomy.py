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
            'content': content,
            'level': level
        }
    
    return taxonomy

def create_graph(taxonomy):
    """Create a graphviz graph from the taxonomy"""
    dot = graphviz.Digraph(comment='Taxonomy')
    dot.attr(rankdir='TB')  # Top to bottom layout
    dot.attr('node', shape='box')  # Use boxes for nodes
    dot.attr('graph', ranksep='1')  # Increase vertical spacing
    
    # Add nodes
    added_nodes = set()
    for index, data in taxonomy.items():
        node_id = f"{index}_{data['content']}"  # Create unique node ID
        if node_id not in added_nodes:
            dot.node(node_id, data['content'])
            added_nodes.add(node_id)
    
    # Add edges
    for index, data in taxonomy.items():
        # Get parent index
        if '.' in index:
            parent_index = '.'.join(index.split('.')[:-1])
            if parent_index in taxonomy:
                child_id = f"{index}_{data['content']}"
                parent_id = f"{parent_index}_{taxonomy[parent_index]['content']}"
                dot.edge(parent_id, child_id)
    
    return dot

def process_model_response(response_file):
    """Process the model response file and extract taxonomies"""
    with open(response_file, 'r') as f:
        data = json.load(f)
    
    # The response is a list of taxonomies in text format
    taxonomies = []
    for item in data:
        if isinstance(item, list) and len(item) > 0:
            # Each item is a list where the first element is the taxonomy text
            taxonomy_text = item[0]
            if isinstance(taxonomy_text, str) and taxonomy_text.startswith('1.'):
                taxonomies.append(taxonomy_text)
    
    return taxonomies

def main():
    parser = argparse.ArgumentParser(description='Visualize taxonomy from model response')
    parser.add_argument('--input', type=str, required=True, help='Path to model_response.json')
    parser.add_argument('--output_dir', type=str, default='visualizations', help='Output directory for PDFs')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process the model response
    taxonomies = process_model_response(args.input)
    
    if not taxonomies:
        print("No taxonomies found in the input file!")
        return
        
    print(f"Found {len(taxonomies)} taxonomies")
    
    # Create visualizations for each taxonomy
    for i, taxonomy_text in enumerate(taxonomies):
        # Parse the taxonomy
        taxonomy_dict = parse_taxonomy(taxonomy_text)
        
        if not taxonomy_dict:
            print(f"Warning: Taxonomy {i+1} is empty")
            continue
            
        print(f"Processing taxonomy {i+1} with {len(taxonomy_dict)} nodes")
        
        # Create the graph
        dot = create_graph(taxonomy_dict)
        
        # Save the visualization
        output_path = os.path.join(args.output_dir, f'taxonomy_{i+1}')
        dot.render(output_path, format='pdf', cleanup=True)
        print(f'Generated {output_path}.pdf')

if __name__ == '__main__':
    main()
