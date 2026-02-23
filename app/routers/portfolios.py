from fastapi import APIRouter, Depends, status, HTTPException
from ..schemas.portfolio import  PortfolioCreate, PortfolioUpdate, PortfolioResponse
from ..oauth2 import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
from ..crud import portfolio
import logging


# Get a logger instance
logger = logging.getLogger("app.routers.portfolios")

router = APIRouter(tags=['Portfolios'])

# Create portfolio
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PortfolioResponse)
def create_portfolio(portfolio_data: PortfolioCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_portfolio = portfolio.create_portfolio(db,portfolio_data, current_user.id)
    logger.info(f"Portfolio with id {new_portfolio.id} successfully created for user with id {current_user.id}.")
    return new_portfolio

# List all the portfolios for the user
@router.get("/", status_code= status.HTTP_200_OK, response_model=list[PortfolioResponse]) # return a list of portfolios
def get_portfolios(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    all_portfolios = portfolio.get_portfolios(db, current_user.id)
    logger.info(f"Retrieved {len(all_portfolios)} portfolios with user id {current_user.id}.")
    return all_portfolios


# List a single portfolio by user id
@router.get("/{id}", response_model=PortfolioResponse)
def get_portfolio_id(id:int, db:Session = Depends(get_db), current_user=Depends(get_current_user)):
    portfolio_id = portfolio.get_portfolio_by_id(db,id)

    if not portfolio_id:
        logger.info(f"portfolio with id: {id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {id} not found.")
    
    if portfolio_id.user_id != current_user.id:
        logger.warning(f"Acess to portfolio with  id: {id} not authorized")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Acess to portfolio with  id: {id} not authorized")
    
    logger.info(f"Portfolio with id {id} sucessfully retieved.")
    
    return portfolio_id


# Update portfolio
@router.put("/{id}", response_model=PortfolioResponse)
def update_portfolio(id:int, portfolio_data : PortfolioUpdate, db:Session = Depends(get_db), current_user=Depends(get_current_user)):
    
    # Fetch the portfolio by its id, then check ownership
    portfolio_check = portfolio.get_portfolio_by_id(db, id)

    if not portfolio_check:
        logger.info(f"portfolio with id: {id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {id} not found.")
    
    if portfolio_check.user_id != current_user.id:
        logger.warning(f"Acess to portfolio with  id: {id} not authorized")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Acess to portfolio with  id: {id} not authorized")
    
    # Update the portfolio using its id and the data received
    portfolio_update = portfolio.update_portfolio(db, id, portfolio_data)
    logger.info(f"Portfolio with id {id} successfully updated. ")

    return portfolio_update


# Delete portfolio
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(id:int, db:Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Fetch the portfolio by its id, then check ownership
    portfolio_check = portfolio.get_portfolio_by_id(db, id)

    # Check if the portfolio exists
    if portfolio_check is None:
        logger.info(f"portfolio with id: {id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {id} not found.")
    
    # Make sure only the owner can delete this portfolio
    if portfolio_check.user_id != current_user.id:
        logger.warning(f"Acess to portfolio with  id: {id} not authorized")
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    # Delete the portfolio
    portfolio.delete_portfolio(db, id)
    logger.info(f"Portfolio with id {id} successfully deleted")


