import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import crud
from .config import settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def update_daily_nav():
    """每日净值更新任务"""
    db = SessionLocal()
    try:
        logger.info("开始执行每日净值更新任务")

        # Check if today is a trading day
        from .services.fund_fetcher import FundDataFetcher
        fetcher = FundDataFetcher()

        if not fetcher.is_trading_day():
            logger.info("今天不是交易日，跳过更新")
            return

        # Sync all funds
        result = crud.sync_all_funds(db)

        logger.info(
            f"净值更新完成: {result['updated_count']}/{result['total_count']} 只基金成功"
        )

        if result['errors']:
            logger.error(f"更新过程中的错误: {result['errors']}")

    except Exception as e:
        logger.error(f"每日净值更新任务失败: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """启动定时任务调度器"""
    if not settings.SCHEDULER_ENABLED:
        logger.info("定时任务调度器已禁用")
        return

    # Schedule daily task
    scheduler.add_job(
        update_daily_nav,
        'cron',
        hour=settings.SCHEDULER_HOUR,
        minute=settings.SCHEDULER_MINUTE,
        id='daily_nav_update',
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"定时任务调度器已启动，每日 {settings.SCHEDULER_HOUR:02d}:{settings.SCHEDULER_MINUTE:02d} 执行净值更新")


def stop_scheduler():
    """停止定时任务调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已停止")
