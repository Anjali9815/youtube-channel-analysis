import uvicorn

if __name__ == "__main__":
    # Start FastAPI server with uvicorn if the script is run directly
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
