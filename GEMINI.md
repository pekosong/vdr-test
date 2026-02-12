# GEMINI.md

This file provides a comprehensive overview of the project, its structure, and how to work with it. It's intended to be a living document that's updated as the project evolves.

## Project Overview

This project is an Azure Function written in Python that is triggered by an Azure Event Grid event. Specifically, it's designed to handle `Microsoft.Storage.BlobCreated` events. When a new blob is uploaded to a configured storage account, this function will be triggered and log information about the blob, including its URL, content type, and size.

### Key Technologies

*   **Azure Functions:** The serverless compute service used to run the application code.
*   **Azure Event Grid:** The event routing service that triggers the function.
*   **Python:** The programming language used to write the function.
*   **GitHub Actions:** Used for CI/CD to automatically build and deploy the function to Azure.

## Building and Running

### Prerequisites

*   Python 3.13
*   An Azure subscription and an Azure Function App resource.
*   Azure Functions Core Tools (for local development).

### Local Development

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the function locally:**
    ```bash
    func start
    ```

### Deployment

Deployment is handled automatically by the GitHub Actions workflow in `.github/workflows/main_uploadevent.yml`. The workflow is triggered on every push to the `main` branch.

The workflow performs the following steps:
1.  **Build:**
    *   Checks out the repository.
    *   Sets up the specified Python version.
    *   Installs dependencies from `requirements.txt`.
    *   Creates a `release.zip` file with the application code.
    *   Uploads the zip file as a build artifact.
2.  **Deploy:**
    *   Downloads the build artifact.
    *   Logs into Azure using credentials stored in GitHub secrets.
    *   Deploys the application to the `uploadevent` Azure Function App.

## Development Conventions

*   The main application logic is contained in `function_app.py`.
*   The function is triggered by Event Grid and is named `BlobCreatedHandler`.
*   The function filters for `Microsoft.Storage.BlobCreated` events and logs the details of the created blob.
*   Dependencies are managed in `requirements.txt`.
*   Configuration for the Azure Functions host is in `host.json`.
*   The CI/CD pipeline is defined in `.github/workflows/main_uploadevent.yml`.
