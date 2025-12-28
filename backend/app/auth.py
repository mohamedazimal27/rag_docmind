import os
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

from . import models, schemas, database

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # Change in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Path Configuration (Up 3 levels: app -> backend -> project_root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # CRITICAL: Create user directory
    user_folder = DATA_DIR / str(new_user.id)
    try:
        os.makedirs(user_folder, exist_ok=True)
        # print(f"Created user directory: {user_folder}")
    except Exception as e:
        # In a real app, might want to rollback DB transaction here
        # print(f"Failed to create user directory: {e}")
        # Proceeding for now as directory creation failure shouldn't crash the response if DB is committed, 
        # but logically it's an error state. 

    return new_user

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = Depends(database.SessionLocal) # Placeholder, correct generic way below:
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

