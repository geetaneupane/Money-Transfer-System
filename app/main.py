from fastapi import FastAPI


from app.api.accounts import router as accounts_router

app=FastAPI(
    title="Money Transfer System",
    version="0.1.0",
)

app.include_router(accounts_router)

@app.get("/health")
def health_check()->dict[str, str]:
    return{"status":"ok"}