from fastapi import FastAPI, HTTPException, Request, Form, Body, Depends
from typing import Annotated, List

from fastapi.middleware.cors import CORSMiddleware # starlette.middleware가 fastapi.middleware 에 포함됨
from fastapi.templating import Jinja2Templates

from mongo_db import user_collection # sql database 에서의 session 기능과 동일함
from model import User
from model_login import Login


import uvicorn
from bson import ObjectId
import json
import os


app = FastAPI()

# 동일한 host address 에서 server기능과 client 기능이 일어남을 허용하는 middleware 임
# 실제경우는 일어나지 않으며 개발 기간동안 동일 서버 에서 개발을 허용함
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

templates = Jinja2Templates(directory="templates")

headings = ("Name","Age", "_id", "Actions")
data = () 

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request} )


@app.get("/users")
async def read_users(request: Request):
    users = []
    cursor = user_collection.find({})
    async for doc in cursor:
        temp = {}
        temp['id'] = str(doc['_id']) #abstract _id from ObjectID and add id into doc
        doc.update(temp) 
        print(doc)# inser _id value into the doc dictionary
        user = User(**doc)
        print(user)
        users.append(user)
    print(users)
    if not users: return{"msg":"no records found"}
    #return (users)
    return templates.TemplateResponse("user_list.html", {"request": request, "headings": headings, "data": users}) 

    return users
    
@app.get("/user/{name}") # mongodb 에서는 _id 값이 objectID 로 자동 생성 되어 복잡하여 _id 값을 name 으로 대치하였음
async def read_user(name: str):
    data = {"name": name}
    # make dictionary type data for name (mongodb 에서 data 를 dict 형태로 받음)
    print(data)
    user = await user_collection.find_one(data)
    if not user:
        return f"{name} does not exist"
    print(user)

    user = {"name": user['name'], "age": user['age']}
    # abstract name and user from dictionary to make a json file to response
    # dict 형태에서 json type 으로 바꾸어 return 함
    return (user)

@app.get("/upload")
def root(request: Request):
    print("request received")
    return templates.TemplateResponse("upload.html", {"request": request} )

@app.post("/user")
async def create_user(
    name: str = Form(...),
    age: int = Form(...)
    ):
    data = {
        "name": name,
        "age": age
    }
    print(data)
    # mongodb 에서 data 를 dict 형태로 받음
    doc = dict(data)
    result = await user_collection.insert_one(doc)
    if not result:
        return f"{name} addition failed"
    print(result)
    return f"{name} created..."

@app.delete("/user/{id}")  # mongodb 에서는 _id 값이 objectID 로 자동 생성 되어 복잡하여 _id 값을 name 으로 대치하였음
async def delete_users(id: str):
    data = {"_id": ObjectId(id)}
    print(data)
    result = await user_collection.find_one(data)
    if not result:
        return f"{id} does not exist"
    result = await user_collection.delete_one(data)
    print(result)
    return f"{id} deleted..."

@app.get('/login')
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request} )
  
@app.post('/login', response_model=Login)
async def login_process(id: Annotated[str, Form()], pw: Annotated[str, Form()]):
    print(id, pw)
    #result = await find_user(id)
    result = await user_collection.find_one({"id": id})
    if not result: raise HTTPException(400)
    if not result['pw'] == pw: return {"msg": 'wrong password'}
    return (result)

@app.post('/register', response_model=Login)
async def user_register(id: Annotated[str, Form()], pw: Annotated[str, Form()]):
    user = {"id": id, "pw": pw}
    #result = await create_user(user)
    result = await user_collection.insert_one(user)
    if not result: return {"msg": 'register failed'}
    return (user)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)