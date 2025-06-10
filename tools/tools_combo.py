from tools.pushover import record_user_details_json, record_unknown_question_json
from tools.pubs_rag import rag_agent_json

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": rag_agent_json}
]
