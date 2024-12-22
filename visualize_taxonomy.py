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
    
    # Add nodes
    added_nodes = set()
    for index, data in taxonomy.items():
        if data['content'] not in added_nodes:
            dot.node(data['content'], data['content'])
            added_nodes.add(data['content'])
    
    # Add edges
    for index, data in taxonomy.items():
        # Get parent index
        if '.' in index:
            parent_index = '.'.join(index.split('.')[:-1])
            if parent_index in taxonomy:
                dot.edge(taxonomy[parent_index]['content'], data['content'])
    
    return dot

def process_model_response(response_file):
    """Process the model response file and extract taxonomies"""
    with open(response_file, 'r') as f:
        data = json.load(f)
    
    # Extract the actual taxonomy text from the response
    # This might need adjustment based on the exact format of your response
    taxonomies = []
    for conversation in data:
        for message in conversation[-1:]:  # Look at the last message
            if isinstance(message, dict) and 'content' in message:
                content = message['content']
                # Find the taxonomy part (after any instructions)
                if '1.' in content:
                    taxonomy_text = content[content.find('1.'):]
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
    
    # Create visualizations for each taxonomy
    for i, taxonomy_text in enumerate(taxonomies):
        # Parse the taxonomy
        taxonomy_dict = parse_taxonomy(taxonomy_text)
        
        # Create the graph
        dot = create_graph(taxonomy_dict)
        
        # Save the visualization
        output_path = os.path.join(args.output_dir, f'taxonomy_{i+1}')
        dot.render(output_path, format='pdf', cleanup=True)
        print(f'Generated {output_path}.pdf')

if __name__ == '__main__':
    main()
