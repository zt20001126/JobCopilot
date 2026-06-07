from pydantic import BaseModel, Field, HttpUrl


class GreetingRequest(BaseModel):
    position_title: str = Field(min_length=1, max_length=200)
    job_description: str = Field(min_length=10, max_length=20_000)
    job_url: HttpUrl | None = None


class GreetingResponse(BaseModel):
    simple_version: str
    professional_version: str
    high_reply_version: str
