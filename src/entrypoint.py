import os
from dotenv import load_dotenv
from graph import create_research_graph, AgentState

# Load environment variables
load_dotenv()


def test_research(company_name: str):
    """
    Test the research node functionality.
    
    Args:
        company_name: Name of the company to research
    """
    print("=" * 60)
    print("🚀 StratifyAI - Autonomous Company Research Agent")
    print("=" * 60)
    print(f"\n📌 Target Company: {company_name}\n")
    
    # Initialize state
    initial_state: AgentState = {
        "messages": [],
        "company_name": company_name,
        "research_data": [],
        "conflicting_info": False,
        "final_report": ""
    }
    
    # Create and run graph
    graph = create_research_graph()
    
    print("🔄 Executing research workflow...\n")
    result = graph.invoke(initial_state)
    
    # Display results
    print("\n" + "=" * 60)
    print("📋 EXECUTION LOG")
    print("=" * 60)
    for msg in result["messages"]:
        print(msg)
    
    print("\n" + "=" * 60)
    print("🎯 WORKFLOW DECISION")
    print("=" * 60)
    if result.get("conflicting_info", False):
        print("❌ Reviewer detected a conflict. PAUSED for human review.")
    else:
        print("✅ Reviewer found no conflicts. Proceeding to writer...")
    
    print("\n" + "=" * 60)
    print("📊 RESEARCH FINDINGS")
    print("=" * 60)
    print(f"Total Results: {len(result['research_data'])}\n")
    
    for idx, finding in enumerate(result["research_data"][:5], 1):  # Show first 5
        print(f"\n[{idx}] {finding['title']}")
        print(f"    Score: {finding['score']:.2f}")
        print(f"    URL: {finding['url']}")
        print(f"    Preview: {finding['content'][:150]}...")
    
    if len(result["research_data"]) > 5:
        print(f"\n... and {len(result['research_data']) - 5} more results")
    
    if result.get("final_report"):
        print("\n" + "=" * 60)
        print("📄 FINAL REPORT")
        print("=" * 60)
        print(result["final_report"])
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Interactive company input
    print("=" * 60)
    print("🚀 StratifyAI - Autonomous Company Research Agent")
    print("=" * 60)
    print()
    
    # Get company name from user
    company_name = input("Enter company name to research: ").strip()
    
    if not company_name:
        print("❌ No company name provided. Exiting.")
        exit(1)
    
    print()
    test_research(company_name)
