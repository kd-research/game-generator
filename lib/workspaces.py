import tempfile
import os
import shutil
import zipfile
import base64
import json
from typing import Dict, Optional
from werkzeug.datastructures import FileStorage

def _extract_and_prepare_game_content(bundle_zip_path: str, target_workspace_dir: str) -> None:
    """
    Extracts game content from a zip bundle, finds the root based on index.html,
    and moves the content to the target workspace directory.
    """
    extraction_tempdir = tempfile.mkdtemp()
    print(f"Created temporary directory for bundle extraction: {extraction_tempdir}")
    try:
        try:
            with zipfile.ZipFile(bundle_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extraction_tempdir)
            print(f"Bundle temporarily extracted from {bundle_zip_path} to: {extraction_tempdir}")
        except zipfile.BadZipFile:
            # This error will be caught by the caller (prepare_workspace)
            print(f"Error: Bundle at {bundle_zip_path} is not a valid zip file.")
            raise ValueError("Invalid game bundle format: Not a valid zip file.")

        index_html_path = None
        for root, _, files in os.walk(extraction_tempdir):
            if "index.html" in files:
                index_html_path = os.path.join(root, "index.html")
                break

        if not index_html_path:
            # This error will be caught by the caller (prepare_workspace)
            raise ValueError("Game bundle does not contain an 'index.html' file.")

        content_root_dir = os.path.dirname(index_html_path)
        print(f"Identified game content root: {content_root_dir}")

        # Move items from content_root_dir to target_workspace_dir
        for item_name in os.listdir(content_root_dir):
            source_item_path = os.path.join(content_root_dir, item_name)
            # shutil.move(src, dst_dir) moves src into dst_dir.
            # If an item with the same name exists in dst_dir,
            # behavior depends on whether it's a file or directory.
            # Files will be overwritten. Directories will have src moved inside them if names clash.
            # Given target_workspace_dir might contain 'external', this behavior is acceptable.
            shutil.move(source_item_path, target_workspace_dir)
        
        print(f"Moved game content from {content_root_dir} to {target_workspace_dir}")

    finally:
        if os.path.exists(extraction_tempdir):
            shutil.rmtree(extraction_tempdir)
            print(f"Cleaned up temporary extraction directory: {extraction_tempdir}")

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
        _extract_and_prepare_game_content(bundle_zip_path, tempdir)
        print(f"Successfully processed and placed game content into: {tempdir}")
    except ValueError as e: # Catches ValueErrors from _extract_and_prepare_game_content
        print(f"Error processing game bundle: {e}")
        # Re-raise the exception for the calling route to handle and return a proper response
        raise
    finally:
        if os.path.exists(bundle_zip_path): # Ensure it exists before removing
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
        "suggested_name": None, # Default suggested name
    }
    external_path = os.path.join(tempdir, "external")
    result_file_path = os.path.join(external_path, "result")
    metadata_file_path = os.path.join(external_path, "metadata.json")

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
    
    def parse_metadata_file(file_path: str) -> Dict[str, Optional[str]]:
        metadata = {}
        if not os.path.exists(file_path):
            print(f"Metadata file not found: {file_path}")
            return metadata
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                metadata = json.load(f)
                print(f"Loaded metadata from {file_path}")
        except Exception as e:
            print(f"Error reading metadata file {file_path}: {e}")
        return metadata

    # Load external assets if they exist
    if os.path.exists(external_path):
        results["icon_base64Data"] = read_and_encode(os.path.join(external_path, "icon.png"))
        results["splash_base64Data"] = read_and_encode(os.path.join(external_path, "splash.png"))
        
        # Parse the result file
        parsed_result = parse_result_file(result_file_path)
        results["status"] = parsed_result["status"]
        results["message"] = parsed_result["message"]
        
        # Parse the metadata file and merge with results
        metadata = parse_metadata_file(metadata_file_path)
        results.update(metadata)
        
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