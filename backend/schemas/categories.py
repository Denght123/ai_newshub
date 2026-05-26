from pydantic import BaseModel, ConfigDict, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    sort_order: int = 0


class UpdateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    sort_order: int = 0
    is_active: bool = True

class CreateCategoryResponse(BaseModel):
    id:int
    name:str
    description:str | None
    sort_order:int
    is_active:bool

    model_config = ConfigDict(from_attributes=True)