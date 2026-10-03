"""Command Line Interface - AgentFlow Simple"""

import asyncio
import argparse
import sys
import logging
import yaml
from pathlib import Path

from .researcher import BiologicalResearcher



def show_help():
    """Show help information"""
    print("""
📚 AgentFlow Simple - User Guide

🔍 Supported Query Types:
  • Basic biomedical knowledge queries
    Example: "What is autophagy?"
    Example: "What is the function of mTOR signaling pathway?"
  
  • Mechanism analysis queries
    Example: "How is autophagy regulated?"
    Example: "How does AMPK activate autophagy?"
  
  • Protein function queries
    Example: "Role of LC3 protein in autophagy"
    Example: "Function of p62 protein"
  
  • Comparative analysis queries
    Example: "Difference between autophagy and apoptosis"
    Example: "Difference between macroautophagy and microautophagy"

💡 Usage Tips:
  • Use specific biomedical terminology
  • Questions can be asked in Chinese or English
  • Complex questions will be automatically decomposed
  • System will automatically search multiple data sources

🛠️ Commands:
  • help/h - Show this help information
  • quit/exit/q - Exit the program
    """)


async def run_single_query(researcher: BiologicalResearcher, query: str):
    """Run single query"""
    print(f"🤖 Processing query: {query}")
    
    final_answer = await researcher.research(query)

    print("\n📋 Final Answer:")
    print("-" * 60)
    print(final_answer)
    print("-" * 60)

async def run_interactive_mode(researcher: BiologicalResearcher):
    """Run interactive mode"""
    print("🧬 AlphaAutophagy")
    print("=" * 60)
    print('Enter "q", "quit", or "exit" to exit the program')
    print('Enter "h" or "help" to view help information')
    print("-" * 60)
    
    while True:
        try:
            query = input("\nPlease enter your query: ").strip()
            
            # Handle exit commands
            if query.lower() in ['quit', 'exit', '退出', 'q']:
                print("\n👋 Goodbye! Thank you for using AgentFlow Simple!")
                break
            
            # Handle help commands
            if query.lower() in ['help', '帮助', 'h']:
                show_help()
                continue
            
            # Handle empty input
            if not query:
                continue
            
            print(f"\n🤖 Processing query: {query}")
            print("-" * 60)
            
            # Execute research
            final_answer = await researcher.research(query)

            print("\n📋 Final Answer:")
            print("-" * 60)
            print(final_answer)
            print("-" * 60)

        except KeyboardInterrupt:
            print("\n\n⚠️ User interrupted operation")
            break
        except Exception as e:
            raise e

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="AgentFlow Simple - Biomedical Research Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python -m agentflow_simple.main                    # Interactive mode
  python -m agentflow_simple.main "What is autophagy?"        # Single query
  python -m agentflow_simple.main -q "Autophagy mechanism" -o result.md  # Query and save results
        """
    )
    
    parser.add_argument(
        "query", 
        nargs="?", 
        help="Question to query (if not provided, enter interactive mode)"
    )

    parser.add_argument(
        "-c", "--config", 
        default="config/config.yaml",
        help="Configuration file path"
    )

    args = parser.parse_args()
    
    try:
        # Load configuration
        print(f"📄 Loading configuration from: {args.config}")
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Display startup information
        print("🚀 Starting AlphaAutophagy...")
        print(f"🤖 Using model: {config['llm']['model']}")
        
        # Create researcher instance
        researcher = BiologicalResearcher(config)
        
        if args.query:  # Single query mode
            await run_single_query(researcher, args.query)
        else:  # Interactive mode
            await run_interactive_mode(researcher)
    
    except KeyboardInterrupt:
        print("\n👋 User canceled, program exiting")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
