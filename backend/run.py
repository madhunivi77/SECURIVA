
import uvicorn

if __name__ == "__main__":
    # We use uvicorn's built-in env_file loading to ensure the environment is correctly
    # loaded in the reloader subprocess.
    uvicorn.run(
        "my_app.server.main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True, 
        env_file=".env"
    )
