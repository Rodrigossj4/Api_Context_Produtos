from pydantic import BaseModel
from src.models.Produto.Produto import Produto

class Produtos(BaseModel): 
    Produtos:list[Produto] 