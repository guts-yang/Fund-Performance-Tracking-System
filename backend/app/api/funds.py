from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import crud, schemas
from ..services.fund_fetcher import FundDataFetcher

router = APIRouter(prefix="/api/funds", tags=["funds"])


@router.post("/", response_model=schemas.FundResponse, status_code=status.HTTP_201_CREATED)
def create_fund(fund: schemas.FundCreate, db: Session = Depends(get_db)):
    """添加基金"""
    # Check if fund code already exists
    existing = crud.get_fund_by_code(db, fund.fund_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"基金代码 {fund.fund_code} 已存在"
        )

    # Try to fetch fund info from API
    fetcher = FundDataFetcher()
    nav_data = fetcher.get_fund_nav(fund.fund_code)

    if nav_data and not fund.fund_name:
        fund.fund_name = f"基金{fund.fund_code}"

    return crud.create_fund(db=db, fund=fund)


@router.get("/", response_model=List[schemas.FundResponse])
def get_funds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有基金列表"""
    return crud.get_funds(db, skip=skip, limit=limit)


@router.get("/{fund_id}", response_model=schemas.FundResponse)
def get_fund(fund_id: int, db: Session = Depends(get_db)):
    """获取基金详情"""
    fund = crud.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )
    return fund


@router.put("/{fund_id}", response_model=schemas.FundResponse)
def update_fund(fund_id: int, fund: schemas.FundUpdate, db: Session = Depends(get_db)):
    """更新基金信息"""
    updated_fund = crud.update_fund(db, fund_id, fund)
    if not updated_fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )
    return updated_fund


@router.delete("/{fund_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fund(fund_id: int, db: Session = Depends(get_db)):
    """删除基金"""
    success = crud.delete_fund(db, fund_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )
    return None


@router.post("/{fund_id}/sync", response_model=schemas.NavHistoryResponse)
def sync_fund(fund_id: int, db: Session = Depends(get_db)):
    """手动同步基金数据"""
    fund = crud.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"基金 ID {fund_id} 不存在"
        )

    result = crud.sync_fund_data(db, fund_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步基金 {fund.fund_code} 数据失败"
        )

    return result


@router.post("/search")
def search_fund(keyword: str, db: Session = Depends(get_db)):
    """搜索基金"""
    fetcher = FundDataFetcher()
    results = fetcher.search_fund(keyword)
    return {"results": results}


@router.get("/info/{fund_code}", response_model=schemas.FundInfoResponse)
def get_fund_info_by_code(fund_code: str):
    """根据基金代码获取基金信息（用于前端自动填充）"""
    fetcher = FundDataFetcher()
    fund_info = fetcher.get_fund_info(fund_code)
    return fund_info
