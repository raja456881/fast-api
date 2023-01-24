from fastapi import APIRouter, status, responses, Depends, HTTPException, File, UploadFile
from models import *
import secrets
from starlette.requests import Request
from authentication import *
from fastapi.templating import Jinja2Templates
from dotenv import dotenv_values
from PIL import Image


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")
config_credentials=dotenv_values(".env")
# from .main import get_current_user
router=APIRouter(
    prefix="/api/user",
    tags=['User']
)
async def get_current_user(token:str=Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(token, config_credentials['SECRET'], algorithms=['HS256'])
        user=await User.get(id=payload.get("id"))
        return user
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invaild username or password",
            headers={"WWW-Authenticate":"Bearer"}
        ) 

@router.post("/token")
async def generate_token(request_form:OAuth2PasswordRequestForm = Depends()):
    token=await token_generator(request_form.username, request_form.password)
    return {"access_token": token, "token_type":"bearer"}


@router.post("/registration")
async def user_registrations(user:user_pydantic_in):
    user_info=user.dict(exclude_unset=True)
    user_info['password']=get_password_hash(user_info['password'])
    user_obj=await User.create(**user_info)
    new_user=await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "status":status.HTTP_201_CREATED,
        "data":f"Hello {new_user.name}.thanks user this services. Please check your email indox and click on the link to confirm your registration."
    }

@router.post("/user/me")
async def user_login(user: user_pydantic_in=Depends(get_current_user)):
    business=Business.get(owner=user)
    log =await business.logo
    log_path=f"localhost:9000/static/images/{log}"
    return {
        "status":"ok",
        "data":{
            "username":user.username,
            "email":user.email,
            "verified":user.is_verified,
            "joined_data":user.join_data.strftime("%b %d %Y"),
            "log":log_path
        }
    }

template=Jinja2Templates(directory="templates")
@router.get("/verification", response_class=responses.HTMLResponse)
async def email_verification(request:Request, token:str):
    user=await verify_token(token)
    if user and not user.is_verified:
        user.is_verified=True
        await user.save()
        return template.TemplateResponse("verification.html", {"request":request, "username":user.name})


@router.post("/uploadfile/profile")
async def create_upload_file(file: UploadFile=File(...), user:user_pydantic=Depends(get_current_user)):
    Filepath="./static/images"
    filename=file.filename
    extension=filename.split(".")[1]
    if extension not in ["jpg", "png"]:
        return {"status":"error", "details":"File extension is not allowed"}
    token_name=f"{secrets.token_hex(10)}.{extension}"

    generated_name=f"{Filepath}{token_name}"
    file_context = await file.read()
    with open(generated_name, "wb") as file:
        await file.write(file_context)

    img=Image.open(generated_name)
    img=img.resize(size=(200, 200))
    img.save(generated_name)
    file.close()
    business=await Business.get(owner=user)
    if user==await business.owner:
        business.logo=token_name
        await business.save()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invaild token or expried token",
            headers={"WWW-Authenticate":"Bearer"}
        )  
    file_url=f"localhost:9000{generated_name[1:]}"  
    return {"status":"ok", "filename":file_url}