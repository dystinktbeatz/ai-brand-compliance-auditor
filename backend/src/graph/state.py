import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict

# Define the schema for a single compliance result
# Error reporting should be structured and standardized to allow for easy interpretation and actionability.
# Each compliance issue should include the following fields.
# This also prevents the AI from generating unstructured error messages that may be difficult to parse and act upon.
class ComplianceIssue(TypedDict):
    category : str
    description : str # specific detail of violation
    severity : str # Critical | Warning
    timestamp : Optional[str]
    
# Define global graph state.
# This state will be passed to each node in the graph, allowing them to read and update the state as needed.

class VideoAuditState(TypedDict):
    """
    Define the data schema for langgraph execution content
    Main container for all data related to the video auditing process, including input parameters, intermediate results, 
    and final deliverables.
    
    """
    # input parameters
    video_url : str
    video_id : str
    
    # Ingestion and Extraction of data. This includes all raw data obtained from the video, such as metadata, 
    # transcripts, OCR text, etc.
    local_file_path : Optional[str]
    video_metadata : Optional[Dict[str, Any]] # e.g. duration, resolution, codec, etc. eg - {"duration": "2 mins", "resolution": "1080p", "codec": "H.264"}
    transcript : Optional[str] # full transcript of the video
    ocr_text : List[str] # text extracted from video frames
    
    # Analysis output
    # Stores the list of all the violations found in the video, along with their details.
    # This allows for a comprehensive report of all compliance issues identified during the audit.
    compliance_results : Annotated[List[ComplianceIssue], operator.add] # list of compliance issues found in the video.
    # This field is crucial for understanding the specific compliance issues identified in the video,
    # their severity, and when they were detected. 
    # New issues can be appended to this list as they are discovered during the analysis process,
    # allowing for a cumulative record of all compliance violations found in the video.
    
    # Final deliverables that the user will receive at the end of the audit process. This includes a summary report of all compliance issues,
    # a final compliance status (pass/fail), and any other relevant deliverables such as a detailed report or
    # recommendations for remediation.
    final_status : str # Pass | Fail
    final_report : str # summary report of all compliance issues found in the video, including details and recommendations for remediation.
    
    # System observability
    # Captures any errors encountered during the processing of the video,
    # which is essential for debugging and improving the system(system level crashes).
    # Errors: API timeouts, processing errors, system level errors, etc.
    errors : Annotated[List[str], operator.add] # list of error messages encountered during processing