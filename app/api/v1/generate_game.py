from flask import request, jsonify, make_response
import uuid
import traceback
import shutil

from . import api_v1 # Import the blueprint
from lib.workspaces import initialize_workspace, finalize_workspace
from app.usecases.generate_game import generate_game as generate_game_use_case

@api_v1.route('/generate_game', methods=['POST'])
def generate_game():
    if not request.is_json:
        return make_response(jsonify({"error": "Request must be JSON"}), 400)

    data = request.get_json()
    game_request = data.get('request')

    if not game_request:
        return make_response(jsonify({"error": "Missing 'request' field"}), 400)

    workspace_path = None
    try:
        # 1. Initialize workspace
        workspace_path = initialize_workspace()

        # 2. Call the use case (placeholder for actual generation)
        generate_game_use_case(workspace_path, game_request)

        # 3. Finalize workspace (collect results, zip, cleanup)
        final_results = finalize_workspace(workspace_path)
        workspace_path = None # Mark as cleaned up
        
        # 4. Construct the response based on schema
        response_data = {
            "generated_icon": {
                "name": "generated_icon.png",
                "type": "image/png",
                "base64Data": final_results["icon_base64Data"]
            },
            "generated_splash": {
                "name": "generated_splash.png",
                "type": "image/png",
                "base64Data": final_results["splash_base64Data"]
            },
            "generated_bundle": {
                "name": "generated_bundle.zip",
                "type": "application/zip",
                "base64Data": final_results["bundle_base64Data"]
            },
            "status": final_results["status"].lower() if final_results["status"] else "failed",
            "message": final_results["message"],
            "generation_id": str(uuid.uuid4()),
            "suggested_name": final_results["suggested_name"]
        }

        # Ensure required fields have data, even if empty, to match schema
        if not response_data["generated_icon"]["base64Data"]:
             response_data["generated_icon"]["base64Data"] = ""
        if not response_data["generated_splash"]["base64Data"]:
             response_data["generated_splash"]["base64Data"] = ""
        if not response_data["generated_bundle"]["base64Data"]:
             response_data["generated_bundle"]["base64Data"] = "" # Or handle as error depending on logic
             if response_data["status"] == "success": # Bundle is required for success
                 response_data["status"] = "failed"
                 response_data["message"] = "Failed to generate game bundle zip."
        if "suggested_name" not in final_results or not final_results["suggested_name"]:
             response_data["suggested_name"] = ""

        return jsonify(response_data)

    except Exception as e:
        print(f"Error during game generation: {e}")
        traceback.print_exc() # Log the full traceback
        return make_response(jsonify({"error": "Server error during game generation."}), 500)

    finally:
        # Ensure cleanup even if errors occurred before finalization
        if workspace_path and shutil.os.path.exists(workspace_path):
            try:
                shutil.rmtree(workspace_path)
                print(f"Cleaned up workspace due to error or incomplete finalization: {workspace_path}")
            except Exception as cleanup_e:
                print(f"Error during final workspace cleanup: {cleanup_e}") 