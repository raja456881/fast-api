from passlib.context import CryptContext
import jwt
from dotenv import dotenv_values
from models import User
from fastapi import HTTPException, status
config_credentials=dotenv_values(".env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def get_password_hash(password):
    return pwd_context.hash(password)


async def verify_token(token :str):
    try:
        payload=jwt.decode(token, config_credentials['SECRET'], algorithm="HS256")
        user=await User.get(id=payload["id"])
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invaild token",
            headers={"www-Authenticate":"Bearer"}
        )
    return user


async def verify_password(plainpassword, hashed_password):
    return pwd_context.verify(plainpassword, hashed_password)


async def authenticate_user(username, password):
    user=await User.get(username=username)
    if user and verify_password(password, user.password):
        return user
    return False



async def token_generator(username:str , password:str):
    user=await authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invaild username or password",
            headers={"WWW-Authenticate":"Bearer"}
        )
    token_data={
        "id":user.id,
        "username":user.name
    }
    token=jwt.encode(token_data, config_credentials['SECRET'],algorithm="HS256")
    return token