import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..model import models, schemas
from ..services.auth import hash_password, verify_password, create_access_token
from ..services.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.email == user_in.email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado.")
    user = models.User(
        first_name=user_in.first_name.strip(),
        last_name=user_in.last_name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=hash_password(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}

@router.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email.lower().strip()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}

from datetime import datetime, timedelta
from ..services.auth import hash_password
from ..services.config import SECRET_KEY
from jose import jwt
from ..services.email_service import send_reset_email
from pydantic import EmailStr

@router.post("/reset-password")
def reset_password(req: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email.lower().strip()).first()
    if user:
        exp = datetime.utcnow() + timedelta(minutes=30)
        token = jwt.encode({"sub": user.email, "exp": exp, "typ":"reset"}, SECRET_KEY, algorithm="HS256")
        user.reset_token = token
        user.reset_token_expires = exp
        db.commit()
        frontend_base = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:8000/frontend")
        link = f"{frontend_base}/html/reset_confirm.html?token={token}"
        try:
            send_reset_email(user.email, link)
        except Exception as e:
            print("Falha ao enviar e-mail:", e)
    return {"message": "Se o e-mail existir, enviaremos instruções."}

@router.post("/reset-password-confirm")
def reset_password_confirm(data: schemas.ResetPasswordConfirm, db: Session = Depends(get_db)):
    email = None
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("typ") != "reset":
            raise Exception("tipo inválido")
        email = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or user.reset_token != data.token or (user.reset_token_expires and user.reset_token_expires < datetime.utcnow()):
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    user.password_hash = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    return {"message": "Senha redefinida com sucesso"}
