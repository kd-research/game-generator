from flask import request, jsonify, make_response
import traceback
import shutil

from . import api_v1 # Import the blueprint
from lib.workspaces import initialize_workspace, prepare_workspace, finalize_workspace
from app.usecases.customize_game import customize_game as customize_game_use_case

@api_v1.route('/customize_game', methods=['POST'])
def customize_game():
    if 'game_bundle' not in request.files or 'request' not in request.form:
         return make_response(jsonify({"error": "Missing required form fields: 'game_bundle', 'request'"}), 400)

    game_icon = request.files.get('game_icon')
    game_splash = request.files.get('game_splash')
    game_bundle = request.files['game_bundle']
    modification_request = request.form['request']

    workspace_path = None
    try:
        # 1. Initialize workspace
        workspace_path = initialize_workspace()

        # 2. Prepare workspace (unzip bundle, place assets)
        prepare_workspace(workspace_path, game_bundle, game_icon, game_splash)

        # 3. Call the use case (placeholder for actual customization)
        customize_game_use_case(workspace_path, modification_request)

        # 4. Finalize workspace (collect results, zip, cleanup)
        final_results = finalize_workspace(workspace_path)
        workspace_path = None # Mark as cleaned up

        # 5. Construct the response based on schema
        response_data = {
            "modified_icon": {
                "name": "modified_icon.png",
                "type": "image/png",
                "base64Data": final_results["icon_base64Data"]
            },
            "modified_splash": {
                "name": "modified_splash.png",
                "type": "image/png",
                "base64Data": final_results["splash_base64Data"]
            },
            "modified_bundle": {
                "name": "modified_bundle.zip",
                "type": "application/zip",
                "base64Data": final_results["bundle_base64Data"]
            },
            "status": final_results["status"].lower() if final_results["status"] else "failed",
            "message": final_results["message"]
        }

        # Ensure required fields have data, even if empty, to match schema
        if not response_data["modified_icon"]["base64Data"]:
             response_data["modified_icon"]["base64Data"] = "" # Icon is required
             if response_data["status"] == "success":
                 response_data["status"] = "failed"
                 response_data["message"] = "Failed to generate modified icon."
        if not response_data["modified_splash"]["base64Data"]:
             response_data["modified_splash"]["base64Data"] = "" # Splash is required
             if response_data["status"] == "success":
                 response_data["status"] = "failed"
                 response_data["message"] = "Failed to generate modified splash screen."
        if not response_data["modified_bundle"]["base64Data"]:
             response_data["modified_bundle"]["base64Data"] = "" # Bundle is required
             if response_data["status"] == "success":
                 response_data["status"] = "failed"
                 response_data["message"] = "Failed to generate modified game bundle zip."

        return jsonify(response_data)
    
    except ValueError as e:
        # Catch errors specifically from prepare_workspace (e.g., bad zip)
        print(f"Input error during game customization: {e}")
        traceback.print_exc()
        return make_response(jsonify({"error": str(e)}), 400)

    except Exception as e:
        print(f"Error during game customization: {e}")
        traceback.print_exc() # Log the full traceback
        return make_response(jsonify({"error": "Server error during game customization."}), 500)

    finally:
        # Ensure cleanup even if errors occurred before finalization
        if workspace_path and shutil.os.path.exists(workspace_path):
            try:
                shutil.rmtree(workspace_path)
                print(f"Cleaned up workspace due to error or incomplete finalization: {workspace_path}")
            except Exception as cleanup_e:
                print(f"Error during final workspace cleanup: {cleanup_e}") 