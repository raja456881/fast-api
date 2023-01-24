# from fastapi import BackgroundTasks, HTTPException, UploadFile, File, Form, Depends, status
# from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
# from dotenv import dotenv_values
# from pydantic import BaseModel, EmailStr
# from typing import List
# from models import User
# import jwt

# config_credentials=dotenv_values(".env")

# conf = ConnectionConfig(
#     MAIL_USERNAME =config_credentials("MAIL_USERNAME"),
#     MAIL_PASSWORD=config_credentials("MAIL_PASSWORD"),
#     MAIL_FROM = config_credentials("MAIL_FROM"),
#     MAIL_PORT = 587,
#     MAIL_SERVER = "smtp.gmail.com",
#     MAIL_TLS = True,
#     MAIL_SSL = False,
#     USE_CREDENTIALS = True,
# )
# class EmailSchema(BaseModel):
#     email: List[EmailStr]


# async def email_send(email: EmailSchema, instance:User):
#     token_data={
#         "id":instance.id,
#         "name":instance.name
#     }
#     token=jwt.encode(token_data, config_credentials['SECRET'], algorithm="HS256")
#     print(token)
#     template=f"""<!DOCTYPE html><html lang="en">
#     <head>
#     <meta charset="UTF-8">
#     <meta http-equiv="X-UA-Compatible" content="IE=edge">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Document</title>
# </head>
# <body>
# <h1>hello world</h1>
# </body>
# </html>"""
#     message=MessageSchema(
#     subject="Easyshopas Account verification email",
#     recipients=email,
#     body=template,
#     subtype="html"
#     )
#     fm=FastMail(conf)
#     await fm.send_message(message=message)





