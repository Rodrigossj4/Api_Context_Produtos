from pydantic import BaseModel
from src.models.Secao.Secao import Secao

class Secoes(BaseModel):    
    Secoes:list[Secao] 