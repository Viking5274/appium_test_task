# appium_test_task

# Steps to run app

1) pip install -r requirements.txt
2) cd app
3) uvicorn main:app --host 0.0.0.0 --port 8000
4) rqworker --url redis://localhost:6379 order_queue

api have 2 endpoints:

1) http://127.0.0.1:8000/order
2) http://127.0.0.1:8000/order/<order_id>