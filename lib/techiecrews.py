import os

from techies.tools import get_all_tools
from techies.agent import Agent
from techies.task import Task
from techies.crew import Crew

def get_crew(crew_name:str, workspace_path:str):
    os.environ["TECHIES_RUNTIME"] = os.path.dirname(__file__) + "/essential-crew"

    tools = get_all_tools()
    for tool in tools.values():
        tool.base_dir = workspace_path

    agent_pool = Agent.eager_load_all(tools)
    task_pool = Task.eager_load_all(agent_pool)
    return Crew(crew_name, agent_pool=agent_pool, task_pool=task_pool, introduce_only=False)