# 模型包的初始化文件
from . import user, student, score_config, file

# 导出常用模型
from app.models.user import User
from app.models.student import Student, StudentFile
from app.models.score_config import ScoreConfig, StudentScore
from app.models.file import File
