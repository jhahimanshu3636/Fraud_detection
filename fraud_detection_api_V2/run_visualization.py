#!/usr/bin/env python3
"""
Standalone Fraud Network Visualization Generator

Usage:
    python run_visualization.py <company_id> [output_file]

Example:
    python run_visualization.py c32
    python run_visualization.py c100 custom_output.html
"""

import os
import sys
import argparse
from visualization import create_visualization_for_company


def main():
    parser = argparse.ArgumentParser(
        description='Generate interactive fraud detection network visualization'
    )
    parser.add_argument(
        'company_id',
        help='Company ID to visualize (e.g., c32)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output HTML file path',
        default=None
    )
    parser.add_argument(
        '--neo4j-uri',
        default=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        help='Neo4j connection URI'
    )
    parser.add_argument(
        '--neo4j-user',
        default=os.getenv('NEO4J_USER', 'neo4j'),
        help='Neo4j username'
    )
    parser.add_argument(
        '--neo4j-password',
        default=os.getenv('NEO4J_PASSWORD', 'password'),
        help='Neo4j password'
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = f'fraud_network_{args.company_id}.html'
    
    print(f"🔍 Generating visualization for company: {args.company_id}")
    print(f"📊 Connecting to Neo4j at: {args.neo4j_uri}")
    
    try:
        # Generate visualization
        result_path = create_visualization_for_company(
            company_id=args.company_id,
            neo4j_uri=args.neo4j_uri,
            neo4j_user=args.neo4j_user,
            neo4j_password=args.neo4j_password,
            output_path=output_path
        )
        
        print(f"✅ Visualization generated successfully!")
        print(f"📁 Output file: {result_path}")
        print(f"\n🌐 Open the file in your browser to view the interactive network:")
        print(f"   file://{os.path.abspath(result_path)}")
        
    except Exception as e:
        print(f"❌ Error generating visualization: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
