from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from datetime import date
from fastapi.responses import FileResponse
import os
import hashlib


UPLOAD_FOLDER = "evidence_files"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)



app = FastAPI(
    title="Digital Evidence Management  API",
    description="API for managing digital evidence and checking evidence integrity",
    version="1.0.0"
)


incidents = []

evidence_list = []

custody_records = []



class Incident(BaseModel):
    title: str
    description: str
    incident_type: str
    reported_by: str



class Evidence(BaseModel):
    incident_id: str
    evidence_type: str
    description: str
    collected_by: str

class CustodyRecord(BaseModel):
    action: str
    performed_by: str
    transferred_to: str | None = None
    remarks: str | None = None

@app.get("/")
def home():

    return {
        "message": "Digital Evidence API is running"
    }



@app.post("/incidents")
def create_incident(incident: Incident):

    incident_id = f"INC{len(incidents) + 1:03d}"

    new_incident = {
        "incident_id": incident_id,
        "title": incident.title,
        "description": incident.description,
        "incident_type": incident.incident_type,
        "reported_by": incident.reported_by,
        "date_reported": str(date.today()),
        "status": "Open"
    }

    incidents.append(new_incident)

    return new_incident




@app.get("/incidents")
def get_incidents():

    return {
        "total_incidents": len(incidents),
        "incidents": incidents
    }



@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):

    for incident in incidents:

        if incident["incident_id"] == incident_id:

            return incident

    raise HTTPException(
        status_code=404,
        detail="Incident not found"
    )


@app.put("/incidents/{incident_id}")
def update_incident(
    incident_id: str,
    incident: Incident
):

    for existing_incident in incidents:

        if existing_incident["incident_id"] == incident_id:

            existing_incident["title"] = incident.title
            existing_incident["description"] = incident.description
            existing_incident["incident_type"] = incident.incident_type
            existing_incident["reported_by"] = incident.reported_by

            return {
                "message": "Incident updated successfully",
                "incident": existing_incident
            }

    raise HTTPException(
        status_code=404,
        detail="Incident not found"
    )



@app.post("/evidence")
async def create_evidence(
    incident_id: str = Form(...),
    evidence_type: str = Form(...),
    description: str = Form(...),
    collected_by: str = Form(...),
    file: UploadFile = File(...)
):


    incident_exists = False

    for incident in incidents:

        if incident["incident_id"] == incident_id:

            incident_exists = True
            break

    if not incident_exists:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )


    

    evidence_id = f"E{len(evidence_list) + 1:03d}"


    

    original_filename = file.filename

    stored_filename = f"{evidence_id}_{original_filename}"

    file_path = os.path.join(
        UPLOAD_FOLDER,
        stored_filename
    )



    file_data = await file.read()



    with open(file_path, "wb") as buffer:

        buffer.write(file_data)




    file_hash = hashlib.sha256(
        file_data
    ).hexdigest()


   

    new_evidence = {

        "evidence_id": evidence_id,

        "incident_id": incident_id,

        "evidence_type": evidence_type,

        "description": description,

        "collected_by": collected_by,

        "original_filename": original_filename,

        "stored_filename": stored_filename,

        "content_type": file.content_type,

        "file_size": len(file_data),

        "file_hash": file_hash,

        "date_collected": str(date.today()),

        "status": "Registered"
    }


    

    evidence_list.append(new_evidence)


    

    return {

        "message": "Evidence uploaded successfully",

        "evidence": new_evidence
    }




@app.get("/evidence")
def get_all_evidence():

    return {

        "total_evidence": len(evidence_list),

        "evidence": evidence_list
    }



@app.get("/evidence/{evidence_id}")
def get_evidence(evidence_id: str):

    for evidence in evidence_list:

        if evidence["evidence_id"] == evidence_id:

            return evidence

    raise HTTPException(
        status_code=404,
        detail="Evidence not found"
    )

@app.get("/evidence/{evidence_id}/file")
def get_evidence_file(evidence_id: str):

    for evidence in evidence_list:

        if evidence["evidence_id"] == evidence_id:

            file_path = os.path.join(
                UPLOAD_FOLDER,
                evidence["stored_filename"]
            )

            if not os.path.exists(file_path):

                raise HTTPException(
                    status_code=404,
                    detail="Evidence file not found"
                )

            return FileResponse(
                path=file_path,
                media_type=evidence["content_type"],
                filename=evidence["original_filename"]
            )

    raise HTTPException(
        status_code=404,
        detail="Evidence not found"
    )




@app.post("/evidence/{evidence_id}/verify")
def verify_evidence(evidence_id: str):

    

    for evidence in evidence_list:

        if evidence["evidence_id"] == evidence_id:

            stored_filename = evidence["stored_filename"]

            file_path = os.path.join(
                UPLOAD_FOLDER,
                stored_filename
            )


            

            if not os.path.exists(file_path):

                evidence["status"] = "File Missing"

                return {

                    "evidence_id": evidence_id,

                    "result": "Evidence file is missing",

                    "status": "File Missing"
                }


           

            with open(file_path, "rb") as file:

                file_data = file.read()


            

            current_hash = hashlib.sha256(
                file_data
            ).hexdigest()


            original_hash = evidence["file_hash"]


           
            if current_hash == original_hash:

                evidence["status"] = "Verified"

                return {

                    "evidence_id": evidence_id,

                    "original_hash": original_hash,

                    "current_hash": current_hash,

                    "result": "Evidence integrity verified",

                    "status": "Verified"
                }


            else:

                evidence["status"] = "Integrity Check Failed"

                return {

                    "evidence_id": evidence_id,

                    "original_hash": original_hash,

                    "current_hash": current_hash,

                    "result": "Evidence may have been modified",

                    "status": "Integrity Check Failed"
                }


    

    raise HTTPException(
        status_code=404,
        detail="Evidence not found"
    )

@app.post("/evidence/{evidence_id}/custody")
def add_custody_record(
    evidence_id: str,
    custody: CustodyRecord
):

    for evidence in evidence_list:

        if evidence["evidence_id"] == evidence_id:

            custody_id = f"C{len(custody_records) + 1:03d}"

            new_record = {
                "custody_id": custody_id,
                "evidence_id": evidence_id,
                "action": custody.action,
                "performed_by": custody.performed_by,
                "transferred_to": custody.transferred_to,
                "remarks": custody.remarks,
                "date_time": str(date.today())
            }

            custody_records.append(new_record)

            return new_record

    raise HTTPException(
        status_code=404,
        detail="Evidence not found"
    )

@app.get("/evidence/{evidence_id}/custody")
def get_custody_history(evidence_id: str):

    # Check whether evidence exists
    for evidence in evidence_list:

        if evidence["evidence_id"] == evidence_id:

            history = []

            for record in custody_records:

                if record["evidence_id"] == evidence_id:

                    history.append(record)

            return {
                "evidence_id": evidence_id,
                "total_records": len(history),
                "chain_of_custody": history
            }

    raise HTTPException(
        status_code=404,
        detail="Evidence not found"
    )

@app.get("/evidence/search")
def search_evidence(
    incident_id: str | None = None,
    evidence_type: str | None = None,
    status: str | None = None
):

    results = []

    for evidence in evidence_list:

        if incident_id is not None:
            if evidence["incident_id"] != incident_id:
                continue

        if evidence_type is not None:
            if evidence["evidence_type"].lower() != evidence_type.lower():
                continue

        if status is not None:
            if evidence["status"].lower() != status.lower():
                continue

        results.append(evidence)

    return {
        "total_results": len(results),
        "evidence": results
    }
class IncidentStatus(BaseModel):
    status: str


@app.patch("/incidents/{incident_id}/status")
def update_incident_status(
    incident_id: str,
    status_data: IncidentStatus
):

    if status_data.status not in ["Open", "Closed"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be Open or Closed"
        )

    for incident in incidents:

        if incident["incident_id"] == incident_id:

            incident["status"] = status_data.status

            return {
                "message": "Incident status updated successfully",
                "incident": incident
            }

    raise HTTPException(
        status_code=404,
        detail="Incident not found"
    )