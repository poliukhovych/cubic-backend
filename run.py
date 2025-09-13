
import uvicorn
import logging

if __name__ == "__main__":
    print(" Starting Cubic Backend API Server...")
    print(" Server will be available at: http://localhost:8000")
    print(" API Documentation at: http://localhost:8000/docs")
    print(" ReDoc Documentation at: http://localhost:8000/redoc")
    print(" Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
