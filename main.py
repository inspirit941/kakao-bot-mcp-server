# from fastapi import FastAPI
# from fastapi.security import OAuth2AuthorizationCodeBearer
# from starlette.middleware.sessions import SessionMiddleware
# import secrets
# from router.auth import auth
#
# app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))
#
# # Include auth router
# app.include_router(auth)
#
# # OAuth2 Configuration compliant with MCP Spec 2025-03-26
# oauth2_scheme = OAuth2AuthorizationCodeBearer(
#     authorizationUrl="/auth/authorize",
#     tokenUrl="/auth/token",
#     scopes={"openid": "OpenID Connect scope"},
# )
#
#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
