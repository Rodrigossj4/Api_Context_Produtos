from pydantic import BaseModel
    
class Erro(BaseModel):
    status:int
    msg:str 