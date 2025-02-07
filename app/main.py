from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from celery.result import AsyncResult
import uuid
import base64
from .tasks import process_image_task

app = FastAPI()

class ProcessingRequest(BaseModel):
    image_b64: str
    categories: list[str]

@app.post("/process", status_code=status.HTTP_202_ACCEPTED)
async def process_image(request: ProcessingRequest):
    try:
        # Validate base64
        base64.b64decode(request.image_b64, validate=True)
    except:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")
    
    task = process_image_task.apply_async(
        args=(request.image_b64, request.categories),  # Add your actual categories here
        task_id=str(uuid.uuid4())
    )
    return {"task_id": task.id}

@app.get("/results/{task_id}")
def get_results(task_id: str):
    task_result = AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        return {"status": "processing"}
    elif task_result.state == 'SUCCESS':
        return {"status": "completed", "result": task_result.result}
    elif task_result.state == 'RETRY':
        return {"status": "retrying"}
    elif task_result.state == 'FAILURE':
        return {"status": "failed", "error": str(task_result.result)}
    
    return {"status": "unknown"}