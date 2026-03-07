from fastapi import FastAPI
from pydantic import BaseModel
from proxy.proxy import process_request

app = FastAPI()


class Query(BaseModel):
    text: str


@app.post("/query")
def query_agent(q: Query):
    result = process_request(q.text)

    return {"response": result}
