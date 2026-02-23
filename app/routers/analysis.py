from fastapi import APIRouter, Depends, status, HTTPException
from ..schemas.analysis import  AnalysisResponse, TickerMetricResponse, OptimizedAllocationResponse
from ..oauth2 import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
from ..crud import analysis
from ..crud import portfolio
from ..crud import holding
from ..services.analysis_service import run_portfolio_analysis
import logging


# Get a logger instance
logger = logging.getLogger("app.routers.analysis")


router = APIRouter(tags=['Analysis'])

# Run analysis on a portfolio
@router.post("/{portfolio_id}/analyze", status_code=status.HTTP_201_CREATED, response_model=AnalysisResponse)
def run_analysis(portfolio_id:int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    
    # Fetch portfolio to check for ownership
    portfolio_check = portfolio.get_portfolio_by_id(db, portfolio_id)

    
    # Check portfolio ownership
    if not portfolio_check:
        logger.info(f"Portfolio with id {portfolio_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {portfolio_id} not found.")
    
     
    # Check if user matches portfokio id
    if portfolio_check.user_id != current_user.id:
        logger.warning(f"Access to portfolio with portfolio id: {portfolio_id} not authorized.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Acess to portfolio with  id: {portfolio_id} not authorized")
    
    # Fetch holdings data for calculatios
    holdings_check = holding.get_holdings( db, portfolio_id)
    
    if not holdings_check:
        logger.info(f"Holdings with portfolio id {portfolio_id} not found.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No holdings to analyze")
   

    # Save the analysis result (this comes from analysis_service.py)
    analysis_data, ticker_metrics, allocations = run_portfolio_analysis(holdings_check)

    new_analysis = analysis.create_analysis_result(db, portfolio_id, analysis_data, ticker_metrics, allocations)
    logger.info(f"Analysis with id {new_analysis.id} successfully performed.")
    return new_analysis


# Get latest analysis
@router.get("/{portfolio_id}/analysis", response_model=AnalysisResponse)
def get_latest_analysis(portfolio_id:int, db:Session = Depends(get_db), current_user=Depends(get_current_user)):
    portfolio_check = portfolio.get_portfolio_by_id(db,portfolio_id)

    if not portfolio_check:
        logger.info(f"Portfolio with id {portfolio_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {portfolio_id} not found.")
    
    if portfolio_check.user_id != current_user.id:
        logger.warning(f"Access to portfolio with portfolio id: {portfolio_id} not authorized.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Acess to portfolio with  id: {portfolio_id} not authorized")
    

    latest_analysis = analysis.get_latest_analysis(db, portfolio_id)

    if latest_analysis is None:
        # here we use portfolio_id since no analysis was found to get an id
        logger.info(f"Analysis with id {portfolio_id} not found.") 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Analysis with id: {portfolio_id} not found.")
    
    logger.info(f"Analysis with id {latest_analysis.id} successfully retrieved")
    
    return latest_analysis


# Get all analyses
@router.get("/{portfolio_id}/analysis/history", response_model=list[AnalysisResponse])
def get_historical_analysis(portfolio_id:int, db:Session = Depends(get_db), current_user=Depends(get_current_user)):
    portfolio_check = portfolio.get_portfolio_by_id(db,portfolio_id)

    if not portfolio_check:
        logger.info(f"Portfolio with id {portfolio_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"portfolio with id: {portfolio_id} not found.")
    
    if portfolio_check.user_id != current_user.id:
        logger.warning(f"Access to portfolio with portfolio id: {portfolio_id} not authorized.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Acess to portfolio with  id: {portfolio_id} not authorized")
    
    historical_analysis = analysis.get_analysis_history(db, portfolio_id)

    # Check if the historical analysis list is empty
    if not historical_analysis :
        # here we use portfolio_id since no analysis was found to get an id
        logger.info(f"Analysis with id {portfolio_id} not found.") 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Analysis with id: {portfolio_id} not found.")
    
    logger.info(f"Retrieved {len(historical_analysis)} analyses for portfolio id {portfolio_id}.")
    return historical_analysis
    

