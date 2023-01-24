from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from .user_router import get_current_user
from models import *
import secrets
from PIL import Image


router=APIRouter(
    prefix="/api/product",
    tags=['product']
)

@router.post("/products")
async def add_product(product:product_pydantic_in, user:user_pydantic=Depends(get_current_user)):
    product=product.dict(exclude_unset=True)
    if product['original_price']>0:
        product['percentage_discount']=(product['original_price']-product['new_price'])/product['original_price'] *100
        product_obj=await Product.create(**product, business=user)
        product_obj=await product_pydantic.from_tortoise_orm(product_obj)
        return {"status":"ok", "data":product_obj}
    return {"status":"error"}

@router.get("/products")
async def get_product():
    response=await product_pydantic.from_tortoise_orm(Product.all())
    return {"status":"ok", "data":response}

@round.get("/product/{id}")
async def get_product(id:str):
    product=await Product.get(id=id) 
    business=product.business
    owner=business.owner
    response=await product_pydantic.from_queryset_single(Product.get(id=id))
    return {
        "status":"ok",
        "data":{
            "product":response,
            "business_details":{
                "business_name":business.business_name,
                "city":business.city,
                "region":business.region,
                "business_description":business.business_description,
                "logo":business.logo,
                "owner_id":owner.id,
                "email":owner.email,
                "join_date":owner.join_data.strftime("%b %d %Y")
            }
        }
    }
@router.delete("/product/{id}")
async def delete_product(id :str, user:user_pydantic=Depends(get_current_user)):
    product=await Product.get(id=id)
    business=await product.business
    owner=await business.owner
    if owner==user:
        await product.delete()
    else:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated to perform the action",
            headers={"WWw-Authenticate", "Bearer"}
        )
    return {"status":"ok"}
























@router.post("/uploadfile/product/{id}")
async def create_upload_file(id:str, file:UploadFile=File(...), user:user_pydantic=Depends(get_current_user)):
    filename=file.filename
    filepath="static\image"
    extension=filename.split(".")[1]
    if extension not in ['jpg', "png"]:
        return {"status":"error", "details":"File extension is not allowed"}
    token_name=f"{secrets.token_hex(10)}.{extension}"

    generated_name=f"{filepath}{token_name}"
    file_context=await file.read()
    with open(generated_name, "wb") as file:
        await file.write(file_context)
    img=Image.open(generated_name)
    img=img.resize(size=(200, 200))
    img.save(generated_name)
    file.close()
    product=await Product.get(id=id)
    business=await product.business
    owmer=await business.owner
    if owmer==user:
        product.product_image=token_name
        await product.save()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invaild token or expried token",
            headers={"WWW-Authenticate":"Bearer"}
        )  
    file_url=f"localhost:9000{generated_name[1:]}"  
    return {"status":"ok", "filename":file_url}



    
