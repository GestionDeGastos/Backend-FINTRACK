from pydantic import BaseModel, EmailStr

class RecoverRequest(BaseModel):
    correo: EmailStr

class ResetRequest(BaseModel):
    token: str
    nueva_password: str
    confirmar_password: str

class ChangePasswordRequest(BaseModel):
    actual: str
    nueva: str
    confirmar: str
