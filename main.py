from fastapi import FastAPI,  Depends
from tortoise import Model, BaseDBAsyncClient
from tortoise.contrib.fastapi import register_tortoise
from router import user_router, product_router
from tortoise.signals import post_save
from typing import Type, List, Optional
from models import *
from authentication import *
from fastapi.staticfiles import StaticFiles 


# from send_email import *
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router.router)
app.include_router(product_router.router)
# app.include_router

@post_save(User)
async def create_business(sender:"Type[User]", instance:User, created:bool, using_db:"Optional[BaseDBAsyncClient]",update_field:List[str])->None:
    if created:
        business_obj=await Business.create(business_name=instance.name, owner=instance)
        await business_pydantic.from_tortoise_orm(business_obj)
        # email_send([instance.email], instance)
        
        #send the mail to business

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


