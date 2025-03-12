gh codespace ports visibility 8000:public -c $(echo $CODESPACE_NAME)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
