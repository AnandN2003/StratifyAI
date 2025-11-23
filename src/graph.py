from typing import TypedDict, List, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from tavily import TavilyClient
import os
import json
from operator import add


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

REVIEWER_SYSTEM_PROMPT = """You are a skeptical data auditor. Your only task is to compare all provided facts about the company and strictly look for numerical or factual discrepancies (e.g., conflicting revenue, different CEO names, contradictory strategic goals).

Analyze the research data carefully and determine if there are any contradictions or conflicts.

Respond ONLY with a valid JSON object in this exact format:
{
    "conflict_detected": true or false,
    "clarification_question": "Your question here if conflict detected, otherwise empty string"
}

Do not include any other text, explanations, or markdown formatting. Only output the JSON object."""

WRITER_SYSTEM_PROMPT = """
You are a highly analytical and experienced Sales Strategist and Account Planning Specialist.
Your task is to take the validated company research data and synthesize it into a formal, structured Account Plan document.

**CRITICAL RULE:** The output MUST be formatted strictly as **Markdown**. Use clear headings (#, ##) and bullet points.

**Account Plan Structure (Mandatory Headings):**

# Account Plan: [Company Name]
## Executive Summary
(1-2 concise paragraphs summarizing the company's current financial health and strategic direction.)

## Key Financial & Operational Insights
* **Annual Revenue (Latest):** [Insert validated number]
* **CEO/Key Decision Maker:** [Insert validated name]
* **Recent News (Last 6 Months):** [Synthesize the 2 most relevant non-conflicting news items.]
* **Strategic Direction/Pain Point:** [What is their primary business goal or major challenge right now?]

## SWOT Analysis (For Sales Strategy)
| Category | Summary |
|:---|:---|
| **Strengths** | (Internal advantages) |
| **Weaknesses** | (Internal limitations/Pain points your product could solve) |
| **Opportunities** | (Market trends they can exploit) |
| **Threats** | (Competitors, market risks) |

## Conversation Starters for Sales Team
(Provide 3 specific, non-generic questions based directly on the research to start a sales dialogue.)
1. ...
2. ...
3. ...

**DATA SOURCE:** Only use the validated, non-conflicting research data provided in the state. Do not invent any facts.
"""


# ============================================================================
# STATE DEFINITION
# ============================================================================


class AgentState(TypedDict):
    """
    State structure for the research agent.
    
    Attributes:
        messages: Conversation history and agent communications
        company_name: Target company for research
        research_data: Accumulated research findings
        conflicting_info: Flag indicating if contradictory information was found
        clarification_question: Question to ask human when conflict detected
        conflicting_data: Details about the conflicting information
        final_report: Generated account plan report
        human_resolution: Human's decision when conflict occurs
    """
    messages: List[str]  # Changed from Annotated to prevent accumulation
    company_name: str
    research_data: List[dict]  # Changed from Annotated to prevent accumulation
    conflicting_info: bool
    clarification_question: str
    conflicting_data: str
    final_report: str
    human_resolution: str


def research_node(state: AgentState) -> AgentState:
    """
    Research Node: Uses Tavily to search for company information.
    
    Args:
        state: Current agent state containing company_name
        
    Returns:
        Updated state with research_data populated
    """
    company_name = state.get("company_name", "")
    messages = state.get("messages", []).copy()
    
    if not company_name:
        messages.append("ERROR: No company name provided for research")
        return {**state, "messages": messages}
    
    # Initialize Tavily client
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        messages.append("ERROR: TAVILY_API_KEY not found in environment")
        return {**state, "messages": messages}
    
    tavily_client = TavilyClient(api_key=tavily_api_key)
    
    # Research queries
    queries = [
        f"{company_name} company overview and business model",
        f"{company_name} recent news and developments",
        f"{company_name} products and services",
        f"{company_name} market position and competitors"
    ]
    
    messages.append(f"🔍 Starting research on: {company_name}")
    
    research_results = []
    
    for query in queries:
        try:
            messages.append(f"  → Searching: {query}")
            
            # Perform search
            response = tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=3
            )
            
            # Extract relevant information
            for result in response.get("results", []):
                research_results.append({
                    "query": query,
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0)
                })
            
            messages.append(f"  ✓ Found {len(response.get('results', []))} results")
            
        except Exception as e:
            messages.append(f"  ✗ Error searching '{query}': {str(e)}")
    
    # Update state
    messages.append(f"\n📊 Research complete: {len(research_results)} total findings")
    
    return {**state, "messages": messages, "research_data": research_results}


# ============================================================================
# REVIEWER NODE
# ============================================================================

def reviewer_node(state: AgentState) -> AgentState:
    """
    Reviewer Node: Analyzes research data for conflicts and contradictions.
    
    Uses Gemini LLM to detect factual discrepancies in the research findings.
    
    Args:
        state: Current agent state containing research_data
        
    Returns:
        Updated state with conflicting_info flag set
    """
    messages = state.get("messages", []).copy()
    messages.append("\n🔍 REVIEWER: Analyzing research data for conflicts...")
    
    research_data = state.get("research_data", [])
    
    if not research_data:
        messages.append("  ⚠️  No research data to review")
        return {**state, "messages": messages, "conflicting_info": False}
    
    # Prepare research summary for LLM
    research_summary = "\n\n".join([
        f"Finding {idx + 1}:\nTitle: {item['title']}\nContent: {item['content']}\nURL: {item['url']}"
        for idx, item in enumerate(research_data[:10])  # Limit to first 10 to avoid token limits
    ])
    
    try:
        llm = get_llm()
        
        messages.append("  → Sending data to Gemini for analysis...")
        
        # Get LLM response
        llm_messages = [
            SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
            HumanMessage(content=f"Analyze this research data about {state['company_name']}:\n\n{research_summary}")
        ]
        response = llm.invoke(llm_messages)
        response_text = response.content.strip()
        
        messages.append(f"  ✓ Gemini response received")
        
        # Parse JSON response
        try:
            # Clean up response if it has markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            conflict_detected = result.get("conflict_detected", False)
            clarification_question = result.get("clarification_question", "")
            
            if conflict_detected:
                messages.append(f"\n⚠️  CONFLICT DETECTED!")
                messages.append(f"  Question: {clarification_question}")
            else:
                messages.append(f"\n✅ No conflicts detected - data appears consistent")
            
            return {
                **state, 
                "messages": messages, 
                "conflicting_info": conflict_detected,
                "clarification_question": clarification_question if conflict_detected else "",
                "conflicting_data": research_summary[:500] if conflict_detected else ""
            }
                
        except json.JSONDecodeError as e:
            messages.append(f"  ✗ Error parsing Gemini response: {str(e)}")
            messages.append(f"  Raw response: {response_text[:200]}...")
            return {**state, "messages": messages, "conflicting_info": False}
            
    except Exception as e:
        messages.append(f"  ✗ Error during review: {str(e)}")
        return {**state, "messages": messages, "conflicting_info": False}


# ============================================================================
# ROUTING LOGIC
# ============================================================================

def route_decision(state: AgentState) -> Literal["needs_human_review", "continue_to_writer"]:
    """
    Routing function to determine next step based on conflict detection.
    
    Args:
        state: Current agent state
        
    Returns:
        String indicating next node: "needs_human_review" or "continue_to_writer"
    """
    if state.get("conflicting_info", False):
        return "needs_human_review"
    else:
        return "continue_to_writer"


# ============================================================================
# HUMAN NODE (STUB)
# ============================================================================

def human_node(state: AgentState) -> AgentState:
    """
    Human-in-the-Loop Node: Interrupts execution for Streamlit UI to handle.
    This node just marks that human review is needed - actual resolution happens in Streamlit.
    
    Args:
        state: Current agent state
        
    Returns:
        State marked for human review (execution will pause here)
    """
    messages = state.get("messages", []).copy()
    messages.append("\n👤 HUMAN REVIEW REQUIRED - Execution paused for Streamlit UI")
    
    # Return state unchanged - the interrupt will pause execution here
    # Streamlit will resume by calling continue_agent() with updated state
    return {**state, "messages": messages}


# ============================================================================
# WRITER NODE (STUB)
# ============================================================================

def writer_node(state: AgentState) -> AgentState:
    """
    Writer Node: Generates final account plan report.
    
    Uses Gemini LLM to synthesize research data into a structured account plan.
    
    Args:
        state: Current agent state
        
    Returns:
        State with final_report populated
    """
    messages = state.get("messages", []).copy()
    messages.append("\n✍️  WRITER NODE: Generating account plan...")
    
    research_data = state.get("research_data", [])
    company_name = state.get("company_name", "Unknown Company")
    
    if not research_data:
        messages.append("  ⚠️  No research data available for report generation")
        final_report = f"# Account Plan: {company_name}\n\nInsufficient data for analysis."
        return {**state, "messages": messages, "final_report": final_report}
    
    # Prepare research summary for LLM
    research_summary = "\n\n".join([
        f"Finding {idx + 1}:\nTitle: {item['title']}\nContent: {item['content']}\nSource: {item['url']}"
        for idx, item in enumerate(research_data[:15])  # Use top 15 findings
    ])
    
    try:
        llm = get_llm()
        
        # Create messages for the LLM
        llm_messages = [
            SystemMessage(content=WRITER_SYSTEM_PROMPT),
            HumanMessage(content=f"Generate an Account Plan for {company_name} based on this research data:\n\n{research_summary}")
        ]
        
        messages.append("  → Sending data to Gemini for synthesis...")
        
        # Get LLM response
        response = llm.invoke(llm_messages)
        report = response.content.strip()
        
        # Clean up markdown code blocks if present
        if "```markdown" in report:
            report = report.split("```markdown")[1].split("```")[0].strip()
        elif "```" in report:
            # Remove any other code block markers
            report = report.replace("```", "").strip()
        
        messages.append(f"  ✓ Account plan generated successfully ({len(report)} characters)")
        
        return {**state, "messages": messages, "final_report": report}
        
    except Exception as e:
        messages.append(f"  ✗ Error generating report: {str(e)}")
        final_report = f"# Account Plan: {company_name}\n\nError generating report: {str(e)}"
        return {**state, "messages": messages, "final_report": final_report}


# ============================================================================
# GRAPH CREATION
# ============================================================================

def route_after_human(state: AgentState) -> Literal["writer", "end"]:
    """
    Routing after human review.
    
    Args:
        state: Current agent state
        
    Returns:
        "writer" if human approved continuation, "end" if stopped
    """
    human_resolution = state.get("human_resolution", "")
    
    # Check if human chose to stop
    if human_resolution == "stop":
        return "end"
    else:
        return "writer"


# ============================================================================
# GRAPH CREATION
# ============================================================================

def create_research_graph():
    """
    Creates the research agent graph with checkpointer for interrupts.
    
    Flow: Researcher → Reviewer → [Human Review OR Writer] → END
    
    Returns:
        Compiled StateGraph with interrupt capability
    """
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("researcher", research_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("human_review", human_node)
    workflow.add_node("writer", writer_node)
    
    # Set entry point
    workflow.set_entry_point("researcher")
    
    # Define edges
    workflow.add_edge("researcher", "reviewer")
    
    # Conditional edge from reviewer based on conflict detection
    workflow.add_conditional_edges(
        "reviewer",
        route_decision,
        {
            "needs_human_review": "human_review",
            "continue_to_writer": "writer"
        }
    )
    
    # After human review, route to writer or end
    workflow.add_conditional_edges(
        "human_review",
        route_after_human,
        {
            "writer": "writer",
            "end": END
        }
    )
    
    # Writer always ends
    workflow.add_edge("writer", END)
    
    # Compile with checkpointer and interrupt before human_review
    checkpointer = MemorySaver()
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"]
    )


# Initialize LLM (for future nodes)
def get_llm():
    """
    Initialize Google Gemini LLM.
    
    Returns:
        ChatGoogleGenerativeAI instance
    """
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        google_api_key=google_api_key
    )
