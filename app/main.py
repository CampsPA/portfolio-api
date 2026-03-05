# activate venv -> venv\Scripts\activate
# run: uvicorn app.main:app --reload
# Run this to generate a new secret key then paste into .env if the existing key is ever compromised
# run: openssl rand -hex 32
# add columns migrations - alembic revision --autogenerate -m "add first_name to users"

from fastapi import FastAPI
from .routers import analysis, auth, holdings, portfolios, users
from fastapi.middleware.cors import CORSMiddleware
import logging
from .logger import setup_logging


# Call the logging setup function *before* initializing the FastAPI app or getting other loggers
setup_logging()

# Get logger instance 
# app.main is a child of app so it inherits everything automatically
logger = logging.getLogger("app.main")


# Create database tables 
# Base.metadata.create_all(bind=engine) no longer needed since the database in now under Alembic's control

# Initialize the App
app = FastAPI(
    title="Portfolio Analyzer API",
    description="Analyze and optimize stock portfolios",
    version="0.1.0"
)
# Log app start up after initialization
logger.info("Portfolio Analyzer API starting up.")


# Initialize CORS, provide the path to React - where frontend runs: http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message" : "Portfolio Analyzer API"}

# link routes
# The analysis and holdings require to be prefixed under portfolios since they are nested uder portfolios
app.include_router(analysis.router, prefix="/portfolios" )
logger.info("Analysis router successfully registered.")

app.include_router(holdings.router, prefix="/portfolios" )
logger.info("Holdings router successfully registered.")

app.include_router(auth.router, prefix="/auth" )
logger.info("Authentication router successfully registered.")

app.include_router(users.router, prefix="/users" )
logger.info("Users router successfully registered.")

app.include_router(portfolios.router, prefix="/portfolios" )
logger.info("Portfolios router successfully registered.")