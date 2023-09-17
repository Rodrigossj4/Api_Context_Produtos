from pydantic import BaseModel
from typing import Optional

class Secao(BaseModel):
    id: Optional[int]
    nome: str
    
