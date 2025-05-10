# Game Generator Flask Server

The Game Generator is an innovative AI-powered platform that enables the automated creation and customization of HTML5 games through natural language prompts. Built with a Flask-based REST API architecture, the system leverages specialized AI agent crews to transform text descriptions into playable games.

## Overview

This platform allows developers and non-technical users to:

- Generate complete HTML5 games from descriptive text prompts
- Customize existing games through natural language instructions
- Modify game assets including icons and splash screens
- Obtain game bundles ready for deployment

The system uses a modular architecture with specialized crews of AI agents that handle different aspects of game generation, from creating the game hierarchy to implementing the playable HTML5 experience. The workspace management system ensures secure and isolated processing of game assets.

## Table of Contents

- [API Endpoints](#api-endpoints)
- [System Architecture](#system-architecture)
  - [High-Level System Overview](#high-level-system-overview)
  - [Game Processing Pipeline](#game-processing-pipeline)
  - [Core Components](#core-components)
    - [Workspace Manager](#workspace-manager)
    - [Crew System](#crew-system)
    - [Core Services](#core-services)
    - [API Structure](#api-structure)
  - [Data Flow](#data-flow)
  - [Integration Points](#integration-points)
  - [Summary](#summary)
- [Development Guide](#development-guide)
  - [Setup](#setup)
  - [Running the Server](#running-the-server)
  - [Development with VS Code and Devcontainers](#development-with-vs-code-and-devcontainers)
  - [Docker Container Setup](#docker-container-setup)

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

## System Architecture

This document describes the high-level architecture of the game-generator system, showing how various components interact to generate and customize HTML5 games. It focuses on the overall structure, core components, and the flow of data through the system during game generation and customization processes.

For detailed information about individual components, see Component Structure. For in-depth information about the crew system that orchestrates game generation, see Crew System.

### High-Level System Overview

The architecture follows a layered approach:

- **Client Interface**: Flask-based REST API providing endpoints for client applications
- **Core Services**: Business logic for game generation and customization
- **Execution Layer**: Workspace management and crew orchestration
- **Agent Framework**: AI agent system organized into specialized crews for different game creation tasks

**Sources**:
- `app/__init__.py` (lines 1-10)
- `app/api/v1/__init__.py` (lines 1-8)
- `lib/techiecrews.py` (lines 1-17)
- `lib/workspaces.py` (lines 56-114)

### Game Processing Pipeline

The game processing pipeline consists of these stages:

1. **Initialization**: Create a temporary workspace directory using `initialize_workspace()`
2. **Preparation**: Extract and prepare game content and assets using `prepare_workspace()`
3. **Processing**:
   - Generate game hierarchy structure using the hierarchy crew
   - Implement the playable game using the HTML5 crew
4. **Finalization**: Package and encode game artifacts using `finalize_workspace()`
5. **Response**: Return the processed game to the client

**Sources**:
- `lib/workspaces.py` (lines 56-218)
- `app/usecases/generate_game.py` (lines 1-15)
- `app/usecases/customize_game.py` (lines 1-18)
- `lib/techiecrews.py` (lines 8-17)

### Core Components

#### Workspace Manager

The Workspace Manager provides:

- Creation of isolated temporary directories for game processing
- Extraction of game bundles and preparation of assets
- Collection and encoding of processed artifacts
- Cleanup of temporary resources

**Sources**:
- `lib/workspaces.py` (lines 56-65) - `initialize_workspace`
- `lib/workspaces.py` (lines 66-113) - `prepare_workspace`
- `lib/workspaces.py` (lines 115-218) - `finalize_workspace`
- `lib/workspaces.py` (lines 9-54) - `_extract_and_prepare_game_content`

#### Crew System

The Crew System functions as follows:

- `get_crew()` initializes specialized crews with agent and task pools
- Agents use tools to perform specific operations
- Tasks are assigned to appropriate agents
- Specialized crews (`hierarchy_crew_v2`, `html5_crew`) execute specific game generation tasks

**Sources**:
- `lib/techiecrews.py` (lines 1-17)
- `app/usecases/generate_game.py` (lines 1-15)
- `app/usecases/customize_game.py` (lines 1-18)

#### Core Services

The core services implement two primary functions:

- **Game Generation**: Creates new games based on a text description
- **Game Customization**: Modifies existing games based on customization requests

Both services follow a similar workflow:
1. Initialize specialized crews using `get_crew()`
2. Invoke each crew's `kickoff()` method with the request input

**Sources**:
- `app/usecases/generate_game.py` (lines 1-15)
- `app/usecases/customize_game.py` (lines 1-18)

#### API Structure

The API provides:

- A versioned API structure (currently v1)
- Endpoints for game generation and customization
- Integration with the core service use cases

**Sources**:
- `app/__init__.py` (lines 1-10)
- `app/api/v1/__init__.py` (lines 1-8)

### Data Flow

The data flow illustrates:

1. Client request processing through the API
2. Workspace creation and preparation
3. Crew initialization and execution
4. Result finalization and response delivery

**Sources**:
- `lib/workspaces.py` (lines 56-218)
- `app/usecases/generate_game.py` (lines 1-15)
- `app/usecases/customize_game.py` (lines 1-18)

### Integration Points

The system provides these integration points:

- **External Interface**: REST API for client applications
- **Internal Interfaces**: Between core services, crew system, and workspace manager

This architecture enables:
- Separation of concerns
- Modular development and testing
- Extensibility for new game generation capabilities

**Sources**:
- `app/__init__.py` (lines 1-10)
- `app/api/v1/__init__.py` (lines 1-8)
- `lib/techiecrews.py` (lines 1-17)
- `lib/workspaces.py` (lines 56-218)

### Summary

The game-generator system architecture provides a structured approach to automated game generation and customization through these key components:

| Component | Responsibility | Key Elements |
|-----------|---------------|--------------|
| Client Interface | External API access | Flask API, Blueprint |
| Core Services | Business logic | `generate_game()`, `customize_game()` |
| Execution Layer | Processing coordination | Techie Crews, Workspace Manager |
| Agent Framework | Game creation implementation | `hierarchy_crew_v2`, `html5_crew` |

For more detailed information on specific aspects of the system, refer to:
- Component Structure for detailed component descriptions
- Data Flow for in-depth data flow analysis
- Crew System for details on the crew orchestration mechanism
- Workspace Management for workspace handling specifics

## Development Guide

### Setup

This project uses `uv` for dependency and environment management.

1.  **Install uv:**
    If you don't have uv installed, follow the instructions here: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

2.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    uv pip sync requirements.in
    ```

### Running the Server

1.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate 
    ```

2.  **Run the Flask development server:**
    ```bash
    python run.py
    ```

The server will start on `http://0.0.0.0:5000`.

### Development with VS Code and Devcontainers

This project supports development using VS Code with devcontainers, which provides a consistent development environment for all contributors.

#### Prerequisites

1. **Install Docker:**
   - [Docker Desktop](https://www.docker.com/products/docker-desktop) for Windows and macOS
   - [Docker Engine](https://docs.docker.com/engine/install/) for Linux

2. **Install VS Code:**
   - Download and install [Visual Studio Code](https://code.visualstudio.com/)

3. **Install the Dev Containers extension:**
   - Open VS Code and install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

#### Opening the Project in a Devcontainer

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/game-generator.git
   cd game-generator
   ```

2. **Open the project in VS Code:**
   ```bash
   code .
   ```

3. **Reopen in Container:**
   - When prompted, click "Reopen in Container"
   - Alternatively, press `F1`, type "Dev Containers: Reopen in Container" and press Enter

VS Code will build the devcontainer based on the configuration in `.devcontainer/devcontainer.json` and `.devcontainer/Dockerfile`. This process may take a few minutes the first time.

#### Benefits of Using Devcontainers

- Consistent development environment across all team members
- All dependencies are pre-installed in the container
- Isolated environment that won't conflict with your local system
- Easy to onboard new developers

### Docker Container Setup

If you prefer to run the application as a standalone Docker container without VS Code:

1. **Build the Docker image:**
   ```bash
   docker build -t game-generator .
   ```

2. **Run the container:**
   ```bash
   docker run -p 5000:5000 game-generator
   ```

The server will be accessible at `http://localhost:5000`.

#### Docker Compose (Optional)

For a more comprehensive setup, you can use Docker Compose:

1. **Create a `docker-compose.yml` file:**
   ```yaml
   version: '3'
   services:
     app:
       build: .
       ports:
         - "5000:5000"
       volumes:
         - .:/app
       environment:
         - FLASK_ENV=development
   ```

2. **Start the services:**
   ```bash
   docker-compose up
   ```

3. **Stop the services:**
   ```bash
   docker-compose down
   ```
