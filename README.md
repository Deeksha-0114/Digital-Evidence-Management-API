# Digital Evidence Management API

A REST API built using Python and FastAPI to manage digital evidence, track incidents, verify evidence integrity, and maintain chain-of-custody records.

## Features

- **Incident Management:** Create, view, update, and track incidents.
- **Evidence Management:** Upload and retrieve digital evidence files.
- **Integrity Verification:** Use SHA-256 hashing to verify whether evidence files have been modified.
- **Chain of Custody:** Record evidence handling and transfer details.
- **Evidence Search:** Filter evidence by incident ID, evidence type, and status.
- **REST API Documentation:** Explore and test endpoints through Swagger UI.

## Technologies Used

- Python
- FastAPI
- Pydantic
- Uvicorn
- SHA-256 hashing

## Installation and Setup

1. Clone the repository:

   `git clone https://github.com/Deeksha-0114/Digital-Evidence-Management-API.git`

2. Navigate to the project directory:

   `cd Digital-Evidence-Management-API`

3. Install the dependencies:

   `pip install -r requirements.txt`

4. Start the FastAPI server:

   `uvicorn main:app --reload`

5. Open the interactive API documentation:

   `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/incidents` | Create an incident |
| GET | `/incidents` | Retrieve incidents |
| POST | `/evidence` | Upload evidence |
| GET | `/evidence` | Retrieve evidence records |
| POST | `/evidence/{evidence_id}/verify` | Verify evidence integrity |
| POST | `/evidence/{evidence_id}/custody` | Add a custody record |
| GET | `/evidence/search` | Search evidence |

## Note

This project currently uses in-memory storage for incident, evidence, and custody records. Data is not persisted across application restarts.

## Author

Deeksha Kollu

GitHub: https://github.com/Deeksha-0114
