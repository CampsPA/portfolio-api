from ..models.holding import Holding
from ..schemas.holding import HoldingCreate, HoldingUpdate
from sqlalchemy.orm import Session
import logging


# Get a logger instance
logger = logging.getLogger("app.crud.holding")

def create_holding(db: Session, holding : HoldingCreate, portfolio_id : int):
    new_holding = Holding(ticker=holding.ticker, num_shares=holding.num_shares,average_cost = holding.average_cost, portfolio_id=portfolio_id)
    db.add(new_holding)
    db.commit()
    db.refresh(new_holding)
    logger.info(f"Holding with id {new_holding.id} succesfully created for portfolio id {portfolio_id}.")
    return new_holding

def get_holdings(db : Session, portfolio_id : int):
    # here i'm filtering the holding model to get all the holding in a given portfolio
    # so I need to call the Holdig and pass the portfolio_id that is in the holding model
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    logger.info(f"Holdings successfully retrieved for portfolio id {portfolio_id}.")
    return holdings


def get_holding_by_id(db : Session, holding_id : int):
    holding = db.query(Holding).filter(Holding.id == holding_id).first()

    if holding is None:
        logger.info(f"Holding with id {holding_id} not found.") 
        return None
    else:
        logger.info(f"Holding with id {holding.id} successfully retrieved.")
    return holding

# Update optional attributes
def update_holding(db: Session, holding_id : int, holding_update : HoldingUpdate):
    holding= get_holding_by_id(db, holding_id)

    if holding_update.num_shares is not None:
        holding.num_shares = holding_update.num_shares

    if holding_update.average_cost is not None:
        holding.average_cost = holding_update.average_cost

    db.commit()
    db.refresh(holding)
    logger.info(f"Holding with id {holding.id} successfully updated.")
    return holding


def delete_holding(db : Session, holding_id : int):
    holding= get_holding_by_id(db, holding_id)
    db.delete(holding)
    logger.info(f"Holding with id {holding.id} successfully deleted.")
    db.commit()



