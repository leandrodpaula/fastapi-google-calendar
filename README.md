# Event Manager API

This project is a Python application for managing events, following a clean architecture pattern. It provides a FastAPI-based API and includes capabilities for interacting with Google Calendar.

## Directory Structure

- `src/`: Contains the source code for the application.
  - `domain/`: Core business logic and entities.
    - `entities/`: Pydantic models for domain entities (e.g., `Event`, `Participant`).
    - `repositories/`: Abstract repository interfaces for data persistence.
  - `application/`: Application-specific logic, orchestrating domain actions.
    - `use_cases/`: Business workflows (e.g., `CreateEventUseCase`).
    - `services/`: Interfaces for application-level services (e.g., `GoogleCalendarService`).
  - `infrastructure/`: Implementation details for frameworks, tools, and external services.
    - `api/`: FastAPI application, including routers, request/response models, and dependency injection.
    - `persistence/`: Concrete implementations of repositories (e.g., `MongoEventRepository`).
    - `external/`: Adapters for external services (e.g., `GoogleCalendarAdapter`).
    - `config/`: Application configuration management (not extensively used in this version).
- `tests/`: Contains unit and integration tests.
  - `unit/`: Tests for individual components in isolation.
  - `integration/`: Tests for interactions between components or with external services (mocked).
- `terraform/`: Terraform configuration for deploying the application to Google Cloud Run.
- `Dockerfile`: For containerizing the application.

## Getting Started

### Prerequisites

- Python 3.9+
- Pip (Python package installer)
- Docker (for containerization, optional for local development if not using containers)
- Access to a MongoDB instance (for data persistence if using `MongoEventRepository`)

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    # (Note: A requirements.txt file would need to be generated and maintained)
    # For now, assuming dependencies like fastapi, uvicorn, pydantic, motor are installed manually or via poetry/pipenv.
    # Example: pip install fastapi uvicorn pydantic motor pymongo python-dotenv
    ```

4.  **Environment Variables:**
    *   **MongoDB**: If using `MongoEventRepository`, ensure your MongoDB server is running and accessible. You'll need to configure the connection string. This application currently defaults to:
        *   `DATABASE_URL="mongodb://localhost:27017"`
        *   `DATABASE_NAME="eventsdb"`
        (These would typically be set via environment variables or a `.env` file loaded by `python-dotenv` in `main.py` or config module).
    *   **Google Calendar**: The current `GoogleCalendarAdapter` is a mock. For a real integration, you would need to:
        *   Set up Google Cloud credentials (e.g., a service account JSON key file).
        *   Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your key file.
        *   The adapter might also require an `API_KEY` or other specific configurations.

5.  **Run the application (using Uvicorn):**
    ```bash
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The API will typically be available at `http://localhost:8000`.

## API Endpoints

### Event Creation

*   **Endpoint:** `POST /api/v1/events/`
*   **Description:** Creates a new event.
*   **Request Body:**
    ```json
    {
        "title": "My Awesome Event",
        "description": "Details about this fantastic event.",
        "start_datetime": "2024-09-15T10:00:00Z",
        "end_datetime": "2024-09-15T12:00:00Z",
        "participants": [
            {
                "email": "alice@example.com",
                "cell_phone": "1234567890"
            },
            {
                "cell_phone": "0987654321"
            }
        ]
    }
    ```
*   **Participants Field:**
    *   The `participants` field in the request body is optional.
    *   If provided, it must be an array of participant objects.
    *   For each participant object:
        *   `email` (string, optional): The participant's email address.
        *   `cell_phone` (string, **mandatory**): The participant's cell phone number.

## Deployment to Google Cloud Run with Terraform

Terraform configuration is provided in the `terraform/` directory to deploy the application as a Google Cloud Run service.

### Prerequisites for Terraform Deployment

1.  **Google Cloud SDK (gcloud):** Installed and configured. Authenticate with your Google Cloud account:
    ```bash
    gcloud auth login
    gcloud auth application-default login
    gcloud config set project YOUR_PROJECT_ID
    ```
2.  **Terraform:** Installed (version ~>1.0 recommended).
3.  **Docker Image:** You need to have built the Docker image for the application and pushed it to Google Container Registry (GCR) or Artifact Registry. The Terraform configuration assumes the image is available.
    *   Example (GCR): `gcr.io/YOUR_PROJECT_ID/event-manager-api-image:latest`
    *   Update `var.image_name` or `var.project_id` in Terraform if your image path differs.

### Deployment Steps

1.  **Navigate to the Terraform directory:**
    ```bash
    cd terraform
    ```

2.  **Create `terraform.tfvars` file:**
    Create a file named `terraform.tfvars` in this directory to provide values for variables, especially your `project_id`.
    ```terraform
    // terraform.tfvars
    project_id = "your-gcp-project-id"
    // Optional: Override other variables like image_name, region, service_name if needed
    // image_name = "my-custom-image-name"
    // region     = "europe-west1"
    ```
    Alternatively, variables can be set via command-line arguments (`-var="project_id=your-gcp-project-id"`) or environment variables (`TF_VAR_project_id=your-gcp-project-id`).

3.  **Initialize Terraform:**
    Downloads the necessary provider plugins.
    ```bash
    terraform init
    ```

4.  **Plan the deployment:**
    Shows what resources Terraform will create/modify.
    ```bash
    terraform plan
    ```

5.  **Apply the configuration:**
    Creates the resources in Google Cloud.
    ```bash
    terraform apply
    ```
    Confirm the action by typing `yes` when prompted.

### Outputs

After a successful deployment, Terraform will output:
- `cloud_run_service_url`: The URL of your deployed service.
- `cloud_run_service_name`: The name of the Cloud Run service.
- `cloud_run_service_location`: The region where the service is deployed.

You can also retrieve these outputs anytime using `terraform output`.

## Running Tests

(Instructions for running unit and integration tests will be added here. Typically using `pytest`.)
```bash
# Example:
# pytest tests/unit
# pytest tests/integration
```

## Contributing

(Information on how to contribute to the project will be added here.)

## License

(License information will be added here. Consider MIT License if unsure.)
This project is licensed under the MIT License. See the LICENSE file for details.
(Assuming a LICENSE file will be added - if not, remove this line or state license directly).
