# GxP Document Generator App

A GxP Document Generator application that interacts with a backend API.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd your_streamlit_app
    ```

2.  **Create Environment File:**
    Create a file named `.env` in the root directory and add your backend API base URL:
    ```dotenv
    # .env
    API_BASE_URL=http://your-backend-api-url:port
    ```
    *(Note: This file is included in `.gitignore` and should not be committed to version control).*

3.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the App Locally

Ensure your backend API is running. Then, run the Streamlit app:

```bash
streamlit run app.py
```

Open your browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`). The app will read the `API_BASE_URL` from the `.env` file.

## Running with Docker

Ensure your backend API is running and accessible from where you run Docker.

1.  **Build the Docker image:**
    ```bash
    docker build -t gxp-frontend .
    ```

2.  **Run the Docker container:**
    You need to pass the environment variables from your `.env` file to the container. The easiest way is using the `--env-file` flag:
    ```bash
    # Make sure your .env file exists in the current directory
    docker run -p 8501:8501 --env-file .env my-streamlit-app
    ```
    Alternatively, you can pass variables individually using the `-e` flag:
    ```bash
    docker run -p 8501:8501 -e API_BASE_URL="http://your-backend-api-url:port" my-streamlit-app
    ```
    *Replace `http://your-backend-api-url:port` with your actual backend URL. If running the backend API locally and accessing it from the Docker container, you might need to use a specific Docker network address (like `host.docker.internal` or your machine's IP) instead of `localhost`.*

Open your browser and navigate to `http://localhost:8501`.

## Project Structure
 - app.py # Main Streamlit application script
 - requirements.txt # Python dependencies
 - .env # Environment variables (API URL) - Not committed
 - .gitignore # Specifies intentionally untracked files that Git should ignore
 - Dockerfile # Defines the Docker image
 - .dockerignore # Specifies files/directories to exclude from the Docker build context
 - README.md # This file


## API Endpoints Expected by the Frontend

The application expects the backend to provide the following endpoints (relative to `API_BASE_URL`):

*   `POST /upload/userstories`: Accepts multiple file uploads.
*   `POST /upload/databaseschema`: Accepts a single file upload.
*   `GET /generate`: Expects parameters (e.g., `user_name`) and returns the generated text file content in the response body.