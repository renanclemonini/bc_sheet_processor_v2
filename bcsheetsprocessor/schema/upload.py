from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool
    job_id: str
    message: str
    status_url: str