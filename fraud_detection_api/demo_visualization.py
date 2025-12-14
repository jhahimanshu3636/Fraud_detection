#!/usr/bin/env python3
"""
Demo script for Fraud Detection Network Visualization

This script demonstrates how to use the visualization module
and provides example use cases.
"""

import os
from visualization import FraudNetworkVisualizer, create_visualization_for_company


def demo_basic_usage():
    """Demo 1: Basic usage - generate visualization for a single company."""
    print("=" * 70)
    print("DEMO 1: Basic Visualization Generation")
    print("=" * 70)
    
    company_id = "c32"
    print(f"\nGenerating visualization for company: {company_id}")
    
    output_file = create_visualization_for_company(
        company_id=company_id,
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    print(f"✅ Visualization generated: {output_file}")
    print(f"📂 Open in browser: file://{os.path.abspath(output_file)}\n")


def demo_batch_processing():
    """Demo 2: Batch processing - generate visualizations for multiple companies."""
    print("=" * 70)
    print("DEMO 2: Batch Processing Multiple Companies")
    print("=" * 70)
    
    companies = ["c32", "c45", "c78"]  # Example company IDs
    
    print(f"\nProcessing {len(companies)} companies...\n")
    
    for idx, company_id in enumerate(companies, 1):
        try:
            output_file = create_visualization_for_company(
                company_id=company_id,
                output_path=f"batch_viz_{company_id}.html"
            )
            print(f"[{idx}/{len(companies)}] ✅ {company_id}: {output_file}")
        except Exception as e:
            print(f"[{idx}/{len(companies)}] ❌ {company_id}: {str(e)}")
    
    print("\n✅ Batch processing complete!\n")


def demo_custom_analysis():
    """Demo 3: Custom analysis - use the visualizer class directly."""
    print("=" * 70)
    print("DEMO 3: Custom Analysis with Direct Class Usage")
    print("=" * 70)
    
    company_id = "c32"
    
    # Initialize visualizer
    visualizer = FraudNetworkVisualizer(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        print(f"\nAnalyzing company: {company_id}")
        
        # Build network graph
        network_data = visualizer.build_network_graph(company_id)
        
        # Print summary
        print("\n📊 Network Summary:")
        print(f"   Risk Score: {network_data['risk_score']:.2f}")
        print(f"   Opportunity Score: {network_data['opportunity_score']:.2f}")
        print(f"   Total Nodes: {network_data['stats']['total_nodes']}")
        print(f"   Total Edges: {network_data['stats']['total_edges']}")
        print(f"   High Risk Nodes: {network_data['stats']['high_risk_nodes']}")
        
        # Print pattern summary
        print("\n🔍 Detected Patterns:")
        shell_count = len(network_data['patterns']['shell_chains'])
        circular_count = len(network_data['patterns']['circular_trade'])
        hidden_count = len(network_data['patterns']['hidden_influence'])
        
        print(f"   Shell Company Chains: {shell_count}")
        print(f"   Circular Trade Cycles: {circular_count}")
        print(f"   Hidden Influence: {hidden_count}")
        
        # Generate visualization
        output_file = visualizer.generate_html_visualization(
            company_id=company_id,
            output_path=f"custom_analysis_{company_id}.html"
        )
        
        print(f"\n✅ Visualization saved: {output_file}\n")
        
    finally:
        visualizer.close()


def demo_api_integration():
    """Demo 4: API integration example (FastAPI)."""
    print("=" * 70)
    print("DEMO 4: API Integration Example")
    print("=" * 70)
    
    print("\n📝 To use the API endpoints, start the FastAPI server:")
    print("\n   uvicorn app:app --reload --port 8000")
    print("\n🌐 Then access these endpoints:")
    print("\n   GET  http://localhost:8000/company/c32")
    print("        → Returns JSON with risk scores and patterns")
    print("\n   GET  http://localhost:8000/company/c32/visualize")
    print("        → Returns interactive HTML visualization")
    print("\n   GET  http://localhost:8000/health")
    print("        → Health check endpoint")
    
    print("\n💡 Example curl commands:")
    print("\n   # Get JSON data")
    print("   curl http://localhost:8000/company/c32")
    print("\n   # Get visualization (save to file)")
    print("   curl http://localhost:8000/company/c32/visualize > viz.html")
    print()


def demo_networkx_analysis():
    """Demo 5: Advanced NetworkX analysis."""
    print("=" * 70)
    print("DEMO 5: Advanced NetworkX Graph Analysis")
    print("=" * 70)
    
    company_id = "c32"
    
    visualizer = FraudNetworkVisualizer(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password")
    )
    
    try:
        # Build network
        network_data = visualizer.build_network_graph(company_id)
        graph = visualizer.graph
        
        print(f"\n🔬 NetworkX Graph Analysis for {company_id}:")
        
        # Basic metrics
        print(f"\n   Nodes: {graph.number_of_nodes()}")
        print(f"   Edges: {graph.number_of_edges()}")
        print(f"   Density: {len(graph.edges()) / (len(graph.nodes()) * (len(graph.nodes()) - 1)) * 2:.3f}")
        
        # Degree analysis
        if graph.number_of_nodes() > 0:
            degrees = dict(graph.degree())
            avg_degree = sum(degrees.values()) / len(degrees)
            print(f"   Average Degree: {avg_degree:.2f}")
            
            # Find most connected nodes
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:3]
            print("\n   Most Connected Entities:")
            for node_id, degree in top_nodes:
                node_data = graph.nodes[node_id]
                print(f"      {node_id} ({node_data['node_type']}): {degree} connections")
        
        # Connected components
        num_components = len(list(visualizer.graph.subgraph(c) for c in 
                                  visualizer.graph.__class__(visualizer.graph).subgraph(c) 
                                  for c in [visualizer.graph.nodes()]))
        print(f"\n   Connected Components: 1")  # Since it's a 2-hop from center
        
        print()
        
    finally:
        visualizer.close()


def main():
    """Run all demos."""
    print("\n🎯 Fraud Detection Network Visualization - Demo Suite\n")
    
    demos = [
        ("Basic Usage", demo_basic_usage),
        ("Batch Processing", demo_batch_processing),
        ("Custom Analysis", demo_custom_analysis),
        ("API Integration", demo_api_integration),
        ("NetworkX Analysis", demo_networkx_analysis)
    ]
    
    print("Available demos:")
    for idx, (name, _) in enumerate(demos, 1):
        print(f"  {idx}. {name}")
    print(f"  {len(demos) + 1}. Run all demos")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nSelect demo (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            
            choice_idx = int(choice)
            
            if choice_idx == len(demos) + 1:
                # Run all demos
                for name, demo_func in demos:
                    try:
                        demo_func()
                    except Exception as e:
                        print(f"\n❌ Demo failed: {str(e)}\n")
                    input("\nPress Enter to continue...")
                break
            elif 1 <= choice_idx <= len(demos):
                # Run selected demo
                name, demo_func = demos[choice_idx - 1]
                try:
                    demo_func()
                except Exception as e:
                    print(f"\n❌ Demo failed: {str(e)}\n")
                input("\nPress Enter to continue...")
            else:
                print("Invalid choice. Please select 0-6.")
        
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
