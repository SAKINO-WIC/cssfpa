from app import db, create_app
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_update_columns():
    """检查列是否存在并更新数据"""
    app = create_app()
    with app.app_context():
        try:
            # 检查comprehensive_test_score列是否存在
            result = db.session.execute(text("PRAGMA table_info(students)")).fetchall()
            columns = [row[1] for row in result]
            
            logger.info(f"当前students表的列: {columns}")
            
            has_comprehensive_score = 'comprehensive_score' in columns
            has_comprehensive_test_score = 'comprehensive_test_score' in columns
            
            logger.info(f"comprehensive_score列是否存在: {has_comprehensive_score}")
            logger.info(f"comprehensive_test_score列是否存在: {has_comprehensive_test_score}")
            
            # 如果comprehensive_test_score列不存在，添加它
            if not has_comprehensive_test_score:
                logger.info("添加comprehensive_test_score列")
                db.session.execute(text("ALTER TABLE students ADD COLUMN comprehensive_test_score INTEGER"))
            
            # 如果两列都存在，确保数据正确
            if has_comprehensive_score and has_comprehensive_test_score:
                logger.info("复制数据从comprehensive_score到comprehensive_test_score")
                db.session.execute(text("UPDATE students SET comprehensive_test_score = comprehensive_score WHERE comprehensive_test_score IS NULL"))
            
            db.session.commit()
            logger.info("列检查和数据更新完成")
            
        except Exception as e:
            logger.error(f"发生错误: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    check_and_update_columns() 