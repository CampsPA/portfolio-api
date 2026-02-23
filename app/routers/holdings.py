from fastapi import APIRouter, Depends, status, HTTPException
from ..schemas.holding import HoldingCreate, HoldingUpdate, HoldingResponse
from ..crud import portfolio
from ..oauth2 import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
from ..crud import holding
import yfinance as yf
import logging


# Get a logger instance
logger = logging.getLogger("app.routers.holdings")

router = APIRouter(tags=['Holdings'])

# Get current price
def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice") or stock.info.get("regularMarketPrice")

    if not price:
        logger.info("Current price data not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"current_price no found.")
    
    logger.info("Current prices successfully found.")
    
    return price

# Add a holding to a portfolio
@router.post("/{portfolio_id}/holdings", status_code=status.HTTP_201_CREATED, response_model=HoldingResponse)
def create_holding(portfolio_id:int, holding_data: HoldingCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    
    # Fetch portfolio by id
    portfolio_check = portfolio.get_portfolio_by_id(db,portfolio_id)

     # Check if the portfolio exists
    if not portfolio_check:
        logger.info(f"portfolio with id: {portfolio_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {portfolio_id} not found.")
    
    # Check if the portfolio id matches the user id
    if portfolio_check.user_id != current_user.id:
        logger.warning(f"Acess to portfolio with  id: {portfolio_id} not authorized")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Acess to portfolio with  id: {portfolio_id} not authorized")


    # Check if average price is provided, if not fetch current price
    if holding_data.average_cost is None:
        logger.info(f"Average cost not provided for {holding_data.ticker}, fetching current market price.")
        price = get_current_price(holding_data.ticker)
        holding_data.average_cost = price

    # Create a new holding in the portfolio
    new_holding = holding.create_holding(db,holding_data, portfolio_id)
    logger.info(f"New holding with id {new_holding.id} successfully created at portfolio with id {portfolio_id}")
    return new_holding



# List all holdings in a portfolio
@router.get("/{portfolio_id}/holdings", status_code= status.HTTP_200_OK, response_model=list[HoldingResponse])
def get_holdings(portfolio_id:int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Fetch portfolio by id
    portfolio_check = portfolio.get_portfolio_by_id(db,portfolio_id)

     # Check if the portfolio exists
    if not portfolio_check:
        logger.info(f"portfolio with id: {portfolio_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {portfolio_id} not found.")
    
    # Check if the portfolio id matches the user id
    if portfolio_check.user_id != current_user.id:
        logger.warning(f"Acess to portfolio with  id: {portfolio_id} not authorized")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Acess to portfolio with  id: {portfolio_id} not authorized")
    
    holdings = holding.get_holdings(db, portfolio_id)
    logger.info(f"Retrieved {len(holdings)} holdings for portfolio id {portfolio_id}.")

    return holdings

# Update a specific holding in a portfolio
# Sice we are acting on an specific holding with need its id along with the portfolio_id
@router.put("/{portfolio_id}/holdings/{holding_id}", response_model=HoldingResponse)
def update_holding(portfolio_id:int, holding_id:int, holding_data : HoldingUpdate, db:Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Fetch the portfolio by its id, then check ownership
    portfolio_check = portfolio.get_portfolio_by_id(db, portfolio_id)
    # Fetch holdings by its id, then check ownership
    holding_check = holding.get_holding_by_id(db, holding_id)


    if not portfolio_check:
        logger.info(f"portfolio with id: {portfolio_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {portfolio_id} not found.")
    
    if not holding_check:
        logger.info(f"holding with id: {holding_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"holding with id: {holding_id} not found.")
    
    if portfolio_check.user_id != current_user.id:
        logger.warning(f"Acess to portfolio with  id: {portfolio_id} not authorized")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Acess to portfolio with  id: {portfolio_id} not authorized")
    
    # Update the portfolio using its id and the data received
    holding_update = holding.update_holding(db, holding_id, holding_data)
    logger.info(f"Holding with {holding_id} sucessfully updated.")

    return holding_update


# Delete holding
@router.delete("/{portfolio_id}/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(portfolio_id:int, holding_id:int, db:Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Fetch the portfolio by its id, then check ownership
    portfolio_check = portfolio.get_portfolio_by_id(db, portfolio_id)
    # Fetch holdings by its id, then check ownership
    holding_check = holding.get_holding_by_id(db, holding_id)

    if not portfolio_check:
        logger.info(f"portfolio with id: {portfolio_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {portfolio_id} not found.")
    
    if not holding_check:
        logger.info(f"holding with id: {holding_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"holding with id: {holding_id} not found.")
    
    if portfolio_check.user_id != current_user.id:
        logger.warning(f"Acess to portfolio with  id: {portfolio_id} not authorized")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Acess to portfolio with  id: {portfolio_id} not authorized")
    
    # Delete the portfolio
    holding.delete_holding(db, holding_id)
    logger.info(f"Holding with id {holding_id} successfully deleted")