from lib.techiecrews import get_crew


def generate_game(workspace_path: str, request: str):
    """Placeholder function to generate game assets in the workspace.

    Args:
        workspace_path: The path to the temporary workspace directory.
        request: The text description of the game to generate.
    """
    hierarchy_crew = get_crew("hierarchy_crew_v2", workspace_path)
    html5_crew = get_crew("html5_crew", workspace_path)

    hierarchy_crew.kickoff(inputs={"request": request})
    html5_crew.kickoff(inputs={"request": request})