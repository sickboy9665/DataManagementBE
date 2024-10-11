import csv
import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import openpyxl
from sqlalchemy.orm import Session
from jwtauth import create_access_token
from schemas import UserCreate, UserInDB, UserResponse
from usermodel import  Contact, User
from dbconnection import SessionLocal
from passlib.context import CryptContext
import pandas as pd
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new user
@router.post("/register", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    
    # Create a new user instance
    new_user = User(email=user.email, hashed_password=hashed_password)
    
    # Add and commit to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# Login user
@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create a JWT token
    access_token = create_access_token(data={"sub": db_user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/upload-contacts/")
async def upload_contacts(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contacts = await process_csv(file)
    # Insert contacts into the database
    for contact in contacts:
        contact_obj = Contact(
            client_name=contact['client_name'],
            first_name=contact['first_name'],
            last_name=contact['last_name'],
            email=contact['email'],
            company_name=contact['company_name'],
            designation=contact['designation'],
            dup_group_id=contact['dup_group_id']
        )
        db.add(contact_obj)

    db.commit()
    return {"message": "Contacts uploaded successfully"}

# Helper to process CSV file
async def process_csv(file: UploadFile):
    contents = await file.read()
    contacts = []
    reader = csv.DictReader(io.StringIO(contents.decode('utf-8')))
    i=0
    for row in reader:
        i += 1
        contact = {
            "client_name": "CLIENT 1",
            "first_name": row["FirstName"],
            "last_name": row["LastName"],
            "email": row["Email"],
            "company_name": row["CompanyName"],
            "designation": row["Designation"],
            "dup_group_id": row["dup_group_id"]
        }
        contacts.append(contact)
    return contacts


## make a get call to fetch contacts from the db
@router.get("/contacts/")
def get_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return [{"id": contact.id, 
             "client_name": contact.client_name, 
             "first_name": contact.first_name, 
             "last_name": contact.last_name, 
             "email": contact.email, 
             "company_name": contact.company_name, 
             "designation": contact.designation, 
             "dup_group_id": contact.dup_group_id} 
            for contact in contacts]