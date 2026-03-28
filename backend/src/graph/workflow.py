"""
Workflow Definition for the Brand Guardian AI.

This module defines the Directed Acyclic Graph (DAG) that orchestrates the
video compliance audit process. It connects the nodes (functional units)
using the StateGraph primitive from LangGraph.

Architecture:
    [START] -> [index_video_node] -> [audit_content_node] -> [END]
""" 
# The workflow is designed to be modular and extensible, allowing for easy addition of 
# new nodes or modification of existing ones without disrupting the overall structure.
# Each node is responsible for a specific task in the video auditing process,
# and the edges define the flow of data and execution between these tasks. 
# The use of a StateGraph ensures that the state is consistently passed and updated across all nodes,
# maintaining a clear and organized data flow throughout the workflow.
from langgraph.graph import StateGraph, END # Import the State Schema

# Import the State Schema
from backend.src.graph.state import VideoAuditState

# Import the Functional Nodes (Workers) that perform the actual processing tasks in the workflow.
from backend.src.graph.nodes import (
    index_video_node,
    audit_content_node
)
# The nodes are designed to be reusable and can be easily swapped out or modified as needed.
# This function constructs the graph by defining the nodes and their connections, and then compiles it into 
# a runnable app that can be executed to perform the video compliance audit.
def create_graph():
    """
    Constructs and compiles the LangGraph workflow.

    Returns:
        CompiledGraph: A runnable graph object ready for execution.
    """
    # 1. Initialize the Graph with the State Schema
    # This ensures all nodes adhere to the 'VideoAuditState' data structure.
    workflow = StateGraph(VideoAuditState) # Initialize the graph with the defined state schema, ensuring that all nodes
    #will read and update the state in a consistent manner. 
    # This is crucial for maintaining data integrity and ensuring that the workflow operates smoothly,
    # as each node will have a clear understanding of the data it can access and modify.

    # 2. Add Nodes (The Workers)
    # The first argument is the unique name of the node in the graph.
    # The second argument is the function to execute.
    workflow.add_node("indexer", index_video_node) # This node is responsible for ingesting the video and extracting 
    # relevant data such as metadata, transcript, and OCR text.
    workflow.add_node("auditor", audit_content_node) # This node takes the extracted data and performs the 
    # compliance audit, updating the state with any issues found and the final report.

    # 3. Define Edges (The Logic Flow)
    # Define the entry point: When the graph starts, go to 'indexer'.
    workflow.set_entry_point("indexer") # This sets the starting point of the workflow, 
    # indicating that the first node to execute when the graph runs will be the 'indexer' node.

    # Connect 'indexer' -> 'auditor'
    # Once the video is indexed (transcript extracted), move to compliance auditing.
    workflow.add_edge("indexer", "auditor") # This defines the flow of execution from the 'indexer' node to the 
    # 'auditor' node,
    # indicating that once the indexing process is complete, the workflow should proceed to the auditing step

    # Connect 'auditor' -> END
    # Once the audit is complete, the workflow finishes.
    workflow.add_edge("auditor", END) # This indicates that after the 'auditor' node has completed its processing,
    # the workflow will reach its end state, signifying that all tasks have been completed and the final results are 
    # ready for output.

    # 4. Compile the Graph
    # This validates the connections and creates the executable runnable.
    app = workflow.compile() # Compiles the graph, validating the structure and preparing it for execution.

    return app

# Expose the runnable app for import by the API or CLI
app = create_graph()