import tempfile
import os
import shutil
import zipfile
import base64
from typing import Dict, Optional
from werkzeug.datastructures import FileStorage

def initialize_workspace() -> str:
    """Creates a temporary directory for processing.

    Returns:
        The absolute path to the created temporary directory.
    """
    tempdir = tempfile.mkdtemp()
    print(f"Initialized workspace: {tempdir}")
    return tempdir

def prepare_workspace(
    tempdir: str,
    game_bundle: FileStorage,
    game_icon: Optional[FileStorage] = None,
    game_splash: Optional[FileStorage] = None,
) -> str:
    """Prepares the workspace by unzipping the bundle and placing assets.

    Args:
        tempdir: The path to the temporary workspace directory.
        game_bundle: The game bundle zip file (Flask FileStorage object).
        game_icon: The optional game icon file (Flask FileStorage object).
        game_splash: The optional game splash file (Flask FileStorage object).

    Returns:
        The path to the prepared temporary directory.
    """
    external_path = os.path.join(tempdir, "external")
    os.makedirs(external_path, exist_ok=True)
    print(f"Created external assets directory: {external_path}")

    # Unzip the bundle
    bundle_zip_path = os.path.join(tempdir, "_bundle.zip")
    game_bundle.save(bundle_zip_path)
    try:
        with zipfile.ZipFile(bundle_zip_path, 'r') as zip_ref:
            zip_ref.extractall(tempdir)
        print(f"Unzipped game bundle into: {tempdir}")
    except zipfile.BadZipFile:
        print(f"Error: Uploaded bundle is not a valid zip file: {game_bundle.filename}")
        # Consider raising an exception here for the route to handle
        raise ValueError("Invalid game bundle format.")
    finally:
        os.remove(bundle_zip_path) # Clean up the temporary zip file

    # Copy icon if provided
    if game_icon:
        icon_path = os.path.join(external_path, "icon.png")
        game_icon.save(icon_path)
        print(f"Saved game icon to: {icon_path}")

    # Copy splash if provided
    if game_splash:
        splash_path = os.path.join(external_path, "splash.png")
        game_splash.save(splash_path)
        print(f"Saved game splash to: {splash_path}")

    return tempdir

def finalize_workspace(tempdir: str) -> Dict[str, Optional[str]]:
    """Finalizes the workspace by collecting assets, zipping, and cleaning up.

    Args:
        tempdir: The path to the temporary workspace directory.

    Returns:
        A dictionary containing base64 encoded assets, status, and message.
    """
    results = {
        "icon_base64Data": None,
        "splash_base64Data": None,
        "bundle_base64Data": None,
        "status": "FAILURE", # Default to failure
        "message": "Processing script did not produce a result file.", # Default message
    }
    external_path = os.path.join(tempdir, "external")
    result_file_path = os.path.join(external_path, "result")

    def read_and_encode(file_path: str) -> Optional[str]:
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Error reading/encoding file {file_path}: {e}")
            return None

    def parse_result_file(file_path: str) -> Dict[str, Optional[str]]:
        status = "FAILURE"
        message = f"Result file found ({file_path}) but could not be parsed."
        if not os.path.exists(file_path):
            return {"status": status, "message": f"Result file not found: {file_path}"}
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) >= 1:
                    parsed_status = lines[0].strip().upper()
                    valid_statuses = ["SUCCESS", "PARTIAL_SUCCESS", "FAILURE"]
                    if parsed_status in valid_statuses:
                        status = parsed_status
                        if len(lines) >= 2:
                            message = lines[1].strip()
                        else:
                             message = "Status read successfully, but no message provided."
                        if status != "FAILURE" and len(lines) < 2:
                             message = f"Status '{status}' read successfully, no specific message provided."
                        elif status == "FAILURE" and len(lines) < 2:
                             message = f"Status 'FAILURE' read, but no specific error message provided."

                    else:
                        message = f"Invalid status found in result file: {lines[0].strip()}"
                else:
                    message = "Result file is empty."
        except Exception as e:
            message = f"Error reading result file {file_path}: {e}"
            print(message)
        return {"status": status, "message": message}

    # Load external assets if they exist
    if os.path.exists(external_path):
        results["icon_base64Data"] = read_and_encode(os.path.join(external_path, "icon.png"))
        results["splash_base64Data"] = read_and_encode(os.path.join(external_path, "splash.png"))
        
        # Parse the result file
        parsed_result = parse_result_file(result_file_path)
        results["status"] = parsed_result["status"]
        results["message"] = parsed_result["message"]
        
        # Remove the external folder before zipping the main content
        shutil.rmtree(external_path)
        print(f"Processed and removed external assets directory: {external_path}")
    else:
        results["message"] = "External assets directory not found after processing."

    # Zip the remaining contents of the tempdir
    output_zip_path = os.path.join(tempfile.gettempdir(), f"{os.path.basename(tempdir)}_bundle.zip")
    try:
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(tempdir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Arcname determines the path inside the zip file
                    arcname = os.path.relpath(file_path, tempdir)
                    zipf.write(file_path, arcname)
        print(f"Zipped workspace contents to: {output_zip_path}")
        
        # Encode the generated zip file
        results["bundle_base64Data"] = read_and_encode(output_zip_path)
    except Exception as e:
        print(f"Error zipping workspace {tempdir}: {e}")
    finally:
        if os.path.exists(output_zip_path):
            os.remove(output_zip_path) # Clean up the final zip file

    # Clean up the entire temporary workspace directory
    try:
        shutil.rmtree(tempdir)
        print(f"Cleaned up workspace: {tempdir}")
    except Exception as e:
        print(f"Error cleaning up workspace {tempdir}: {e}")

    return results 