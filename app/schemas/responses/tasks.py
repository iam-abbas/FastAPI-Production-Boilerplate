from pydantic import UUID4, BaseModel, Field


class TaskResponse(BaseModel):
    title: str = Field(..., description="Task name", example="Task 1")
    description: str = Field(
        ..., description="Task description", example="Task 1 description"
    )
    completed: bool = Field(alias="is_completed", description="Task completed status")
    uuid: UUID4 = Field(
        ..., description="Task UUID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    )

    class Config:
        orm_mode = True
