from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
load_dotenv()
from fastapi import FastAPI
import uvicorn
from router import router 
from dbconnection import engine, Base
from fastapi.middleware.cors import CORSMiddleware
# Create the database tables
Base.metadata.create_all(bind=engine)
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Allows your Angular app to access the API
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(router)

# @app.get("/")
# def read_root():
#     return {"message": "Contact Management API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
