from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas, security, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = security.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    user_id: int = payload.get("id")
    if username is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return schemas.TokenData(username=username, user_id=user_id)

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    ## 注册接口
    - **username**: 用户名
    - **password**: 密码
    - **返回**: 注册成功的用户信息
    """
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """
    ## 登录接口
    - **username**: 用户名
    - **password**: 密码
    - **返回**: 登录成功后的 鉴权token和刷新token
    """ 

    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Include id in payload for standard JWT
    access_token = security.create_access_token(
        data={"sub": user.username, "id": user.id}, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/refresh", response_model=schemas.Token)
async def refresh_token(request: schemas.TokenRefreshRequest, db: Session = Depends(database.get_db)):
    payload = security.verify_token(request.refresh_token, is_refresh=True)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    username: str = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Re-include id during refresh
    access_token = security.create_access_token(
        data={"sub": user.username, "id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "refresh_token": request.refresh_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: schemas.TokenData = Depends(get_current_user)):
    return {"id": current_user.user_id, "username": current_user.username}
