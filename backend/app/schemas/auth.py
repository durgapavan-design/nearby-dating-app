from pydantic import BaseModel, Field


class OtpRequest(BaseModel):
    phone_number: str = Field(min_length=6, max_length=20)


class OtpRequestResponse(BaseModel):
    message: str
    debug_code: str | None = None


class OtpVerify(BaseModel):
    phone_number: str = Field(min_length=6, max_length=20)
    code: str = Field(min_length=4, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool
    profile_completed: bool
