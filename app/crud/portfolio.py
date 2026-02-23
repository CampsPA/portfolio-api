from ..models.portfolio import Portfolio
from ..schemas.portfolio import PortfolioCreate, PortfolioUpdate
from sqlalchemy.orm import Session
import logging


# Get a logger instance
logger = logging.getLogger("app.crud.portfolio")

# Create portfolio
def create_portfolio(db : Session, portfolio : PortfolioCreate, user_id : int):
    new_portfolio = Portfolio(name=portfolio.name, description=portfolio.description, user_id=user_id)
    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)
    logger.info(f"Portfolio with id {new_portfolio.id} successfully created.")
    return new_portfolio


# Get all portfolios
def get_portfolios(db : Session, user_id : int):
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    logger.info(f"Retrieved {len(portfolios)} portfolios for user id {user_id}.")
    return portfolios


# Get portfolio by id
def get_portfolio_by_id(db : Session, portfolio_id : int):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    if portfolio is None:
        logger.info(f"Portfolio with id {portfolio_id} not found.")
        return None
    else:
        logger.info(f"Portfolio with id {portfolio.id} successfully retrieved.")
    return portfolio


# Update portfolio
def update_portfolio(db: Session, portfolio_id : int, portfolio_update : PortfolioUpdate):
    portfolio = get_portfolio_by_id(db, portfolio_id)

    if portfolio_update.name is not None:
        portfolio.name = portfolio_update.name

    if portfolio_update.description is not None:
        portfolio.description  =portfolio_update.description

    db.commit()
    db.refresh(portfolio)
    logger.info(f"Portfolio with id {portfolio.id} successfully updated.")
    return portfolio


# Delete portfolio
def delete_portfolio(db : Session, portfolio_id : int):
    portfolio = get_portfolio_by_id(db, portfolio_id)
    db.delete(portfolio)
    logger.info(f"Portfolio with id {portfolio.id} successfully deleted.")
    db.commit()


    