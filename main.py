from app.core.auth import auth_config
from app.main import create_app

app = create_app()

@app.get("/")
@auth_config(required=False)
async def root():
    """Basic index route to confirm app availability."""
    return {"message": "Spa Manager API is running"}
