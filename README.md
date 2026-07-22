# My Meal Tracker Docker Service

This project tracks meals and calculates nutritional content based on analysed food portions and online nutrition databases

This is a personal project and is not open to contributions. Feedback is unnecessary.

## Features

- Tracks and stores consumed meals
- Identifies food portions using local Ollama VLM
- Calculates nutrition data using local database and online nutrition sources

## Getting Started

### Prerequisites

- Python 3.10

### Installation

1. Clone the repository
2. Navigate to the project directory
3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

### Usage

1. Start the server:
    ```sh
    fastapi dev
    ```
2. Access the endpoints at `http://localhost:8000`.

## Endpoints

Swagger documentation is available at `http://localhost:8000/docs`

## License and Contributing

This project is licensed under the MIT license. Contributions are not open.
