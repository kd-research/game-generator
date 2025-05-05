import os

from lib.techiecrews import get_crew

def customize_game(workspace_path: str, request: str):
    """Placeholder function to customize game assets in the workspace.

    Assumes the workspace is already prepared with existing game files.

    Args:
        workspace_path: The path to the temporary workspace directory.
        request: The text description of the modifications requested.
    """
    hierarchy_crew = get_crew("hierarchy_crew_v2", workspace_path)
    html5_crew = get_crew("html5_crew", workspace_path)

    hierarchy_crew.kickoff(inputs={"request": request})
    html5_crew.kickoff(inputs={"request": request})