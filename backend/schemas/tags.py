from pydantic import BaseModel, ConfigDict, Field


class CreateTagsRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class TagsResponse(BaseModel):
    id:int
    name:str

    model_config = ConfigDict(from_attributes=True)


class TagsListResponse(BaseModel):
    tags: list[TagsResponse]