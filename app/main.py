from rq import Queue
from redis import Redis
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

redis_conn = Redis(host='localhost', port=6379)
order_queue = Queue("order_queue", connection=redis_conn)


@app.post("/order")
async def submit_order(req: Request):
    from working import MyTest
    a = MyTest()
    json_dict = await req.json()
    job = order_queue.enqueue(a.get_prices, json_dict)
    return {
        'order_id': job.id,
    }


@app.get("/order/{order_id}")
def get_order_status(order_id: str):
    job = order_queue.fetch_job(order_id)
    if not job:
        raise HTTPException(status_code=404, detail="Order not found")

    if job.get_status() == 'failed':
        raise HTTPException(status_code=500, detail="Job failed")

    if job.get_status() != 'finished':
        return {
            'status': job.get_status()
        }

    return {
        'status': job.get_status(),
        'result': job.return_value()
    }
