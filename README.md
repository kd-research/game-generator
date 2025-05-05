# Game Generator Flask Server

This is a Flask server scaffold for generating and customizing game assets based on API schemas.

## Setup

This project uses `uv` for dependency and environment management.

1.  **Install uv:**
    If you don't have uv installed, follow the instructions here: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

2.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    uv pip sync requirements.in
    ```

## Running the Server

1.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate 
    ```

2.  **Run the Flask development server:**
    ```bash
    python run.py
    ```

The server will start on `http://0.0.0.0:5000`.

## API Endpoints

*   `POST /v1/generate_game`
    *   Expects `application/json` content type.
    *   Payload: `{"request": "Description of the game"}`
    *   Returns JSON with generated asset placeholders.
*   `POST /v1/customize_game`
    *   Expects `multipart/form-data` content type.
    *   Fields:
        *   `game_bundle` (file, required): The game bundle ZIP file.
        *   `request` (text, required): Description of modifications.
        *   `game_icon` (file, optional): The game icon PNG file.
        *   `game_splash` (file, optional): The game splash PNG file.
    *   Returns JSON with modified asset placeholders.
