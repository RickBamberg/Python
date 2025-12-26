# main.py
# para rodar o nosso código, executar no terminal: uvicorn main:app --reload
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
import secrets

# ==================== CONFIGURAÇÕES ====================
SECRET_KEY = "sua-chave-secreta-muito-segura-aqui"
REFRESH_SECRET_KEY = "outra-chave-secreta-para-refresh"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ==================== ENUM ROLES ====================
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

# ==================== BANCO DE DADOS ====================
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo do Banco de Dados
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RefreshTokenDB(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Criar tabelas
Base.metadata.create_all(bind=engine)

# ==================== PYDANTIC MODELS ====================
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str

class RoleUpdate(BaseModel):
    user_id: int
    new_role: UserRole

# ==================== SETUP ====================
app = FastAPI(title="API com Autenticação e Roles")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

# ==================== FUNÇÕES AUXILIARES ====================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: int, db: Session) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_token = RefreshTokenDB(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return token

def get_user_by_username(db: Session, username: str) -> Optional[UserDB]:
    return db.query(UserDB).filter(UserDB.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserDB]:
    return db.query(UserDB).filter(UserDB.email == email).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[UserDB]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: UserDB = Depends(get_current_user)
) -> UserDB:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user

# Verificar se é admin
async def get_current_admin_user(
    current_user: UserDB = Depends(get_current_active_user)
) -> UserDB:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este recurso"
        )
    return current_user

# ==================== ENDPOINTS ====================

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registrar novo usuário"""
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já registrado"
        )
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    hashed_password = get_password_hash(user.password)
    
    # Primeiro usuário é admin
    user_count = db.query(UserDB).count()
    role = UserRole.ADMIN if user_count == 0 else UserRole.USER
    
    db_user = UserDB(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login e obtenção de tokens"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(user.id, db)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/token/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Renovar access token usando refresh token"""
    db_token = db.query(RefreshTokenDB).filter(
        RefreshTokenDB.token == token_data.refresh_token
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
    
    if db_token.expires_at < datetime.utcnow():
        db.delete(db_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expirado"
        )
    
    user = db.query(UserDB).filter(UserDB.id == db_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    db.delete(db_token)
    new_refresh_token = create_refresh_token(user.id, db)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@app.post("/logout")
async def logout(
    token_data: TokenRefresh,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout - invalidar refresh token"""
    db_token = db.query(RefreshTokenDB).filter(
        RefreshTokenDB.token == token_data.refresh_token,
        RefreshTokenDB.user_id == current_user.id
    ).first()
    
    if db_token:
        db.delete(db_token)
        db.commit()
    
    return {"message": "Logout realizado com sucesso"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserDB = Depends(get_current_active_user)):
    """Obter dados do usuário autenticado"""
    return current_user

@app.put("/users/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualizar dados do usuário autenticado"""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.email is not None:
        # Verificar se email já existe
        existing_user = get_user_by_email(db, user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    return current_user

# ==================== ROTAS ADMIN ====================

@app.get("/admin/users", response_model=List[UserResponse])
async def list_all_users(
    current_user: UserDB = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Listar todos os usuários (apenas admin)"""
    users = db.query(UserDB).all()
    return users

@app.put("/admin/users/role")
async def update_user_role(
    role_update: RoleUpdate,
    current_user: UserDB = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Atualizar role de um usuário (apenas admin)"""
    user = db.query(UserDB).filter(UserDB.id == role_update.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode alterar seu próprio role"
        )
    
    user.role = role_update.new_role
    db.commit()
    db.refresh(user)
    
    return {"message": f"Role do usuário {user.username} atualizado para {role_update.new_role}"}

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserDB = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Deletar um usuário (apenas admin)"""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode deletar sua própria conta"
        )
    
    # Deletar refresh tokens do usuário
    db.query(RefreshTokenDB).filter(RefreshTokenDB.user_id == user_id).delete()
    
    db.delete(user)
    db.commit()
    
    return {"message": f"Usuário {user.username} deletado com sucesso"}

# ==================== ROTAS PROTEGIDAS ====================

@app.get("/protected")
async def protected_route(current_user: UserDB = Depends(get_current_active_user)):
    """Exemplo de rota protegida (qualquer usuário autenticado)"""
    return {
        "message": f"Olá {current_user.username}, você está autenticado!",
        "user_id": current_user.id,
        "role": current_user.role
    }

@app.get("/admin/dashboard")
async def admin_dashboard(current_user: UserDB = Depends(get_current_admin_user)):
    """Dashboard admin (apenas admin)"""
    return {
        "message": "Bem-vindo ao painel administrativo!",
        "admin": current_user.username
    }

@app.get("/")
async def root():
    """Rota pública"""
    return {
        "message": "API de Autenticação com Roles",
        "endpoints": {
            "register": "/register",
            "login": "/token",
            "refresh": "/token/refresh",
            "logout": "/logout",
            "me": "/users/me",
            "update_me": "PUT /users/me",
            "admin_users": "/admin/users (admin only)",
            "admin_dashboard": "/admin/dashboard (admin only)",
            "docs": "/docs"
        }
    }

@app.delete("/admin/cleanup-tokens")
async def cleanup_expired_tokens(
    current_user: UserDB = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Remover refresh tokens expirados (apenas admin)"""
    deleted = db.query(RefreshTokenDB).filter(
        RefreshTokenDB.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    return {"deleted_tokens": deleted}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
