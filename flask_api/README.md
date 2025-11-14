# Flask API

## Setup

### Prerequisites

Before setting up the project, make sure you have the following installed:

- Python 3.x
- pip (Python package installer)

### Installation

1. Create a virtual environment:

    ```
    python -m venv venv
    ```


2. Activate the virtual environment:

    On macOS/Linux:

        source venv/bin/activate
        

    On Windows:

        venv\Scripts\activate


3. Install the required dependencies:

    pip install -r requirements.txt


4. Create the .env file, with this structure:
    DB_HOST=localhost
    DB_PORT=5432 # for postgresql
    DB_NAME=hattrick-database # replace it with your database name
    DB_USER=postgres # replace it with your db username
    DB_PASSWORD=postgres # replace it with your db password
