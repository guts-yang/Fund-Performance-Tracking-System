from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api/nav", tags=["nav"])


@router.get("/{fund_code}", response_model=schemas.NavHistoryResponse)
def get_latest_nav(fund_code: str, db: Session = Depends(get_db)):
    """获取基金最新净值"""
    fund = crud.get_fund_by_code(db, fund_code)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金代码 {fund_code} 不存在"
        )

    nav = crud.get_latest_nav(db, fund.id)
    if not nav:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 {fund_code} 没有净值数据"
        )
    return nav


@router.get("/{fund_code}/history", response_model=List[schemas.NavHistoryResponse])
def get_nav_history(
    fund_code: str,
    start_date: date = None,
    end_date: date = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取基金历史净值"""
    fund = crud.get_fund_by_code(db, fund_code)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金代码 {fund_code} 不存在"
        )

    return crud.get_nav_history(db, fund.id, start_date, end_date, limit)


@router.post("/sync-all", response_model=schemas.SyncResponse)
def sync_all_nav(db: Session = Depends(get_db)):
    """同步所有基金最新净值"""
    result = crud.sync_all_funds(db)

    return schemas.SyncResponse(
        success=True,
        message=f"成功同步 {result['updated_count']}/{result['total_count']} 只基金",
        funds_updated=result['updated_count'],
        errors=result['errors']
    )
