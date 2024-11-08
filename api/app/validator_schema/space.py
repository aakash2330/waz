from pydantic import model_validator
from pydantic.main import BaseModel


class TCreateSpace(BaseModel):
    name: str
    width: int | None = None
    height: int | None = None
    spaceId: str | None = None

    @model_validator(mode="before")
    def check_name_and_dimentions(cls, values: dict[str, str]) -> dict[str, str]:
        space_id = values.get("spaceId")
        width = values.get("width")
        height = values.get("height")

        if space_id is None:
            if not width or not height:
                raise ValueError("Space id is null , dimentions must be provided")
        else:
            if height or width:
                raise ValueError("Both Space Id and dimentions can't be present")

        return values


class TAddElementToSpace(BaseModel):
    name: str
    elementId: str
    spaceId: str
    x: int
    y: int
