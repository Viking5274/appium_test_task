from fastapi import FastAPI, Request
import redis
from redis import Redis
from rq import Queue

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
q = Queue(connection=Redis())


@app.post("/hotel_prices")
async def hotel_prices(req: Request):
    from working import MyTest

    my_class = MyTest()
    json_dict = await req.json()

    final_data = my_class.get_prices(json_dict)
    print(final_data)
    return final_data
