from server import mcp
import uvicorn

if __name__ == "__main__":
    # Configure the server to run on localhost:3001
    # Port 3001 is the default port VS Code looks for MCPs
    uvicorn.run(
        mcp.app,
        host="127.0.0.1",
        port=3001,
        log_level="info"
    )