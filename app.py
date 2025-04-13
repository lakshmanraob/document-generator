import streamlit as st
import requests
import io
import datetime
import os                     # Import os module
# from dotenv import load_dotenv # Import load_dotenv

# --- Load Environment Variables ---
# load_dotenv() # Load variables from .env file

# --- Configuration ---
# Read base URL from environment variable, provide default if not found
# API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000") # Default if .env is missing
API_BASE_URL = os.getenv("API_BASE_URL")

# Construct full API endpoints using the base URL
USER_STORIES_API_ENDPOINT = f"{API_BASE_URL}/upload/userstories"
SCHEMA_API_ENDPOINT = f"{API_BASE_URL}/upload/databaseschema"
GENERATE_API_ENDPOINT = f"{API_BASE_URL}/generate"

# --- Session State Initialization ---
if 'user_stories_uploaded' not in st.session_state:
    st.session_state.user_stories_uploaded = False
if 'schema_uploaded' not in st.session_state:
    st.session_state.schema_uploaded = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'uploaded_user_stories_files' not in st.session_state:
    st.session_state.uploaded_user_stories_files = []
if 'uploaded_schema_file' not in st.session_state:
    st.session_state.uploaded_schema_file = None
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None # To store the generated text
if 'generated_filename' not in st.session_state:
    st.session_state.generated_filename = "generated_output.txt" # Default filename

# --- Helper Function for API Upload ---
def upload_file_to_api(endpoint, file_bytes, filename):
    """Sends a file to a specified API endpoint."""
    try:
        # Use file.getvalue() if it's an UploadedFile object, otherwise assume it's bytes
        file_data = file_bytes.getvalue() if hasattr(file_bytes, 'getvalue') else file_bytes
        files = {'file': (filename, file_data, getattr(file_bytes, 'type', 'application/octet-stream'))}
        response = requests.post(endpoint, files=files)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        st.success(f"Successfully uploaded {filename}!")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading {filename}: {e}")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred during upload: {e}")
        return False

# --- Sidebar ---
with st.sidebar:
    st.header("Uploads")

    # --- User Stories Upload ---
    uploaded_user_stories = st.file_uploader(
        "Upload User Stories (Multiple)",
        accept_multiple_files=True,
        key="user_stories_uploader", # Use a key to manage state
        type=['txt', 'md', 'json', 'csv'] # Add relevant file types
    )

    if uploaded_user_stories and uploaded_user_stories != st.session_state.uploaded_user_stories_files :
        st.session_state.uploaded_user_stories_files = uploaded_user_stories # Update cache
        st.session_state.user_stories_uploaded = False # Reset status until all uploads succeed
        all_successful = True
        st.write("Uploading user stories...")
        progress_bar_stories = st.progress(0)
        num_files = len(uploaded_user_stories)
        for i, file in enumerate(uploaded_user_stories):
            # --- API Call for User Stories ---
            success = upload_file_to_api(USER_STORIES_API_ENDPOINT, file, file.name)
            # ----------------------------------
            if not success:
                all_successful = False
                st.error(f"Failed to upload {file.name}. Aborting remaining uploads.")
                break # Stop if one fails
            progress_bar_stories.progress((i + 1) / num_files)

        if all_successful and uploaded_user_stories:
            st.session_state.user_stories_uploaded = True
            st.success("All user stories processed.")
            st.rerun()
        elif not all_successful:
             st.error("One or more user story uploads failed.")
             # Keep state as False


    # --- Database Schema Upload ---
    uploaded_schema = st.file_uploader(
        "Upload Database Schema (Single)",
        accept_multiple_files=False,
        key="schema_uploader", # Use a key
        type=['sql', 'json', 'yaml', 'txt'] # Add relevant file types
    )

    if uploaded_schema and uploaded_schema != st.session_state.uploaded_schema_file:
        st.session_state.uploaded_schema_file = uploaded_schema # Update cache
        st.session_state.schema_uploaded = False # Reset status
        st.write("Uploading database schema...")
        # --- API Call for Schema ---
        success = upload_file_to_api(SCHEMA_API_ENDPOINT, uploaded_schema, uploaded_schema.name)
        # --------------------------
        if success:
            st.session_state.schema_uploaded = True
            st.success("Database schema processed.")
            st.rerun()
        else:
            st.error("Failed to process database schema.")
            # Keep state as False


# --- Main Area ---
st.title("Welcome!")

user_name = st.text_input("Please enter your name:", value=st.session_state.user_name)
st.session_state.user_name = user_name # Store name in session state if needed elsewhere

st.write(f"Hello, {user_name if user_name else 'Guest'}!")

# --- Generate Button ---
# Enable button only if both uploads are successful
generate_button_disabled = not (st.session_state.user_stories_uploaded and st.session_state.schema_uploaded)

if st.button("Generate", disabled=generate_button_disabled):
    st.session_state.generated_content = None # Clear previous results
    with st.spinner("Generating document... Please wait."):
        try:
            # --- Call the /generate API ---
            # Add any necessary data payload (e.g., user identifier, session id)
            # if your backend needs it to find the uploaded files.
            payload = {"user_name": st.session_state.user_name} # Example payload
            response = requests.get(GENERATE_API_ENDPOINT, json=payload) # Send as JSON
            # Or send form data: requests.post(GENERATE_API_ENDPOINT, data=payload)

            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # --- Process Successful Response (Status Code 200) ---
            if response.status_code == 200:
                # Assume the response body is the text file content
                st.session_state.generated_content = response.text
                # Try to get filename from headers, otherwise create one
                content_disposition = response.headers.get('content-disposition')
                if content_disposition:
                    parts = content_disposition.split('filename=')
                    if len(parts) > 1:
                        st.session_state.generated_filename = parts[1].strip('"')
                    else: # Fallback if header format is unexpected
                         st.session_state.generated_filename = f"generated_output_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
                else: # Fallback if header is missing
                    st.session_state.generated_filename = f"generated_output_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"

                st.success("Document generated successfully!")

            # This part might not be reached if raise_for_status() handles non-200 codes
            # else:
            #     st.error(f"Issue in generating the document. API returned status: {response.status_code}")
            #     st.error(f"Response: {response.text[:500]}") # Show part of the error response

        except requests.exceptions.RequestException as e:
            st.error(f"Issue in generating the document. Could not connect to the API: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred during generation: {e}")

# --- Display Generated Content and Download Button ---
if st.session_state.generated_content:
    st.markdown("---") # Separator
    st.subheader("Generated Document Preview")
    # Use a text area for potentially long content, set height
    st.text_area("Content", st.session_state.generated_content, height=300)

    st.download_button(
        label="Download Generated File",
        data=st.session_state.generated_content,
        file_name=st.session_state.generated_filename,
        mime="text/plain" # Adjust mime type if it's not plain text
    )


# --- Display Upload Status (Optional) ---
st.sidebar.markdown("---")
st.sidebar.write("Upload Status:")
st.sidebar.write(f"User Stories: {'✔️ Processed' if st.session_state.user_stories_uploaded else '❌ Pending'}")
st.sidebar.write(f"Database Schema: {'✔️ Processed' if st.session_state.schema_uploaded else '❌ Pending'}")
