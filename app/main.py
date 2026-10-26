
import os
from datetime import date
import psycopg2
from fastapi import FastAPI, HTTPException ,Response
from dotenv import load_dotenv
from pydantic import BaseModel,Field

load_dotenv()
app = FastAPI(title="User Managemnet API")

class User(BaseModel):
    name: str = Field(max_length=100)
    gender: str = Field(max_length=20)
    age: int
    dob: date
    address: str
    blood_group: str = Field(max_length=5)
    time_zone: str = Field(max_length=64)

def run_query(sql,params=(),fetch=None):
    conn=psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur=conn.cursor()
    cur.execute(sql,params)
    conn.commit()
    result=None
    if fetch is not None:
        columns=[]
        for col in cur.description:
            columns.append(col[0])
        if fetch=="one":
            row = cur.fetchone()
            if row:
                result=dict(zip(columns,row))
            else:
                result=None
        else:
            result=[]
            rows=cur.fetchall()
            for row in rows:
                result.append(dict(zip(columns,row)))
    cur.close()
    conn.close()
    return result

#create user
@app.post("/users",status_code=201)
def create_user(user:User):
    sql="""INSERT INTO users(name,gender, age, dob, address, blood_group, time_zone)
           VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING *"""
    return run_query(sql,tuple(user.model_dump().values()),"one")

#list user
@app.get("/users")
def list_users():
    return run_query("SELECT * FROM users ORDER BY id",fetch="all")

#get_one user
@app.get("/users/{user_id}")
def get_user(user_id:int):
    row=run_query("SELECT * FROM users WHERE id =%s",(user_id,), "one")
    if row is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return row

#update user
@app.put("/users/{user_id}")
def update_user(user_id:int, user:User):
    sql="UPDATE users SET name=%s,gender=%s,age=%s,dob=%s,address=%s,blood_group=%s,time_zone=%s WHERE id=%s RETURNING*"
    row=run_query(sql,(*user.model_dump().values(),user_id),"one")
    if row is None:
        raise HTTPException(status_code=404,detail=f"User {user_id} not found")
    return row

#delete user
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    row = run_query("DELETE FROM users WHERE id=%s RETURNING id", (user_id,), "one")
    if row is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return Response(status_code=204)