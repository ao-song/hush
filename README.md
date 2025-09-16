# Hush: Share Secrets Securely 🤫

## Overview

Hush is a simple, secure web application designed for sharing sensitive text-based secrets like passwords, private notes, or confidential information. It ensures that your secrets are viewed only once and expire automatically after a short period, providing an ephemeral and secure way to transmit sensitive data.

## Features

-   **One-Time View:** Each secret link can only be viewed once. After being accessed, the secret is permanently deleted.
-   **Time-Based Expiration:** If a secret link is not viewed, it automatically expires after one minute, enhancing security.
-   **Unique Shareable Links:** Generate unique, random links for each secret, making them hard to guess.
-   **Simple Interface:** A clean and intuitive user interface built with plain HTML, CSS, and JavaScript.
-   **Robust Backend:** Powered by FastAPI for high performance and easy API development.
-   **Containerized Deployment:** Easily deployable using Docker and Docker Compose, with Nginx serving the frontend and proxying API requests.

## How to Run Locally

To get Hush up and running on your local machine, follow these steps:

### Prerequisites

-   Docker and Docker Compose installed on your system.

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ao-song/hush.git
    cd hush
    ```

2.  **Build and run the Docker containers:**
    ```bash
    docker-compose up --build -d
    ```
    This command will:
    -   Build the `hush-app` Docker image, which includes the FastAPI backend and Nginx for the frontend.
    -   Start the `hush-app` service in detached mode.

3.  **Access the application:**
    Open your web browser and navigate to:
    ```
    http://localhost:8100
    ```

## How to Use

1.  **Create a Secret Link to share:**
    -   On the homepage, enter your secret text into the input field.
    -   Click the "Generate Shareable Link" button.
    -   A unique link will be generated and displayed.

2.  **Share the Link:**
    -   Click the "Copy Link" button to copy the generated link to your clipboard.
    -   Share this link with the intended recipient.

3.  **View the Secret:**
    -   When the recipient opens the link, the secret will be displayed on their screen.
    -   **Important:** Once viewed, the secret is immediately deleted from the system and the link becomes invalid.

4.  **Expired Links:**
    -   If the link is not viewed within one minute of its creation, it will automatically expire and become inaccessible.
