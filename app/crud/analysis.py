from ..models.analysis import AnalysisResult, TickerMetric, OptimizedAllocation
from sqlalchemy.orm import Session
import logging


# Get a logger instance
logger = logging.getLogger("app.crud.analysis")

'''
Here I'm getting all the calculations and metrics and saving them to the database,
the actual calculations will be done in the routes
This file: 
- Receives data
- Saves to the database
- Retrieve data from database
- Return the data
 '''


# Function signature
def create_analysis_result(
    db : Session,
    portfolio_id : int,
    analysis_data : dict,
    ticker_metrics : list[dict],
    allocations : list[dict]
):
    new_analysis = AnalysisResult(portfolio_id=portfolio_id, **analysis_data)
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)
    logger.info(f"Analysis result with id {new_analysis.id} sucessfully created for portfolio id {portfolio_id}")
    
    # now we have new_analysis.id , use in the loop to create new_analysis

    for metric in ticker_metrics:
        new_ticker_metric = TickerMetric(analysis_id=new_analysis.id, **metric)
        db.add(new_ticker_metric)

        
       # now we have new_analysis.id , use in the loop to create new_allocations

    for allocation in allocations:
        new_allocation = OptimizedAllocation(analysis_id=new_analysis.id, **allocation)
        db.add(new_allocation)

    db.commit()
    return new_analysis
        

def get_latest_analysis(db : Session, portfolio_id : int):
    latest_analysis = db.query(AnalysisResult).filter(AnalysisResult.portfolio_id == portfolio_id).order_by(AnalysisResult.calculated_at.desc()).first()
    if latest_analysis is None:
        logger.info(f"No analysis found for portfolio with id {portfolio_id}.")
        return None
    else:
        logger.info(f"Latest analysis with id {latest_analysis.id} for portfolio id {portfolio_id} succesfully retrieved.")
    return latest_analysis


def get_analysis_history(db : Session, portfolio_id : int):
    analysis_history = db.query(AnalysisResult).filter(AnalysisResult.portfolio_id == portfolio_id).order_by(AnalysisResult.calculated_at.desc()).all()
    logger.info(f"Analysis history succesfully for portfolio id {portfolio_id} successfully retrieved.")
    return analysis_history

    