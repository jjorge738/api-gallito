from doctest import Example
from xxlimited import Str
from fastapi import Body,Path,FastAPI,status,Form,File, UploadFile,Request,Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse

from pydantic import BaseModel,Field,HttpUrl,EmailStr
from typing import List, Optional,Union

#Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

##Handlin Errors
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


#clase para recibir una data de images
class Images(BaseModel):
    url:str
    name:str
        
#Clase para recibir imagenes
class Image(BaseModel):
    url:HttpUrl
    #url:str Parametro String
    name:str

class Item(BaseModel):
    name: str = Field(...,Example="Ropa",description="Nombre del producto")
    price: float = Field(...,Example="10.25",description="Valor unitario del producto")
    is_offer: Optional[bool] = Field(...,Example="False",title="Oferta del producto",description="Validacion si esta en oferta.")
    tags: List[str] = []
    image: Optional[Image] = None
    images: Optional[List[Images]] #Parametro Opcional

    class Config:
        schema_extra = {
            "example": {
                "name": "Vehiculo Electrico",
                "price": 84.58,
                "is_offer":True,
                "image":{},
                "images":[],
                "description": "Carro electrico de 12 volts.",
                "tax": 65.89
            }
        }

class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item]

class BaseItem(BaseModel):
    description: str
    type: str

class CarItem(BaseItem):
    type = "car"


class PlaneItem(BaseItem):
    type = "planet"
    size: int


### Usuarios
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserIn(UserBase):
    password: str

class UserOut(UserBase):
    pass

class UserInDB(UserBase):
    hashed_password: str

def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    print(hashed_password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db

def get_user(name:str):
    print(name)

    return {
        "name":"Test",
        "email":"jj@email.com"
    }

@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved

@app.get("/user", response_model=UserOut)
async def create_user(name:str):
    
    return get_user(name)

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item = Body(
    ...,
    examples={
        ##Lista de ejemplos para el API
        "normal": {
            "summary": "A normal example",
            "description": "A **normal** item works correctly.",
            "value": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            },
        },
        "converted": {
            "summary": "An example with converted data",
            "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
            "value": {
                "name": "Bar",
                "price": "35.4",
            },
        },
        "invalid": {
            "summary": "Invalid data is rejected with an error",
            "value": {
                "name": "Baz",
                "price": "thirty five point four",
            },
        },
    }
)):
    return {"item_id": item_id,"item":item}

#Api con un Ejemplo
@app.put("/items_data/{item_id}")
def update_data(
        item_id: int = Path(..., title="The ID of the item to get"), 
        item: Item = Body(
            ...,
            example={
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            },
    )):
    
    results = {"item_id": item_id, "item": item}
    return results

@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

items = {
        "item1": {"description": "All my friends drive a low rider", "type": "car"},
        "item2": {
            "description": "Music is my aeroplane, it's my aeroplane",
            "type": "plane",
            "size": 5,
        },
    }
@app.get("/productos/{item_id}", response_model=Union[PlaneItem, CarItem],status_code=status.HTTP_200_OK)
async def read_item(item_id: str):
    print(items)
    return items[item_id]

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}

@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}

@app.get("/auth/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}

@app.get("/print_template/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})