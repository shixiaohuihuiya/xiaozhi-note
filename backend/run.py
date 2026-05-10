"""
启动脚本 - 从backend目录运行
"""
import sys
from pathlib import Path

# 添加app目录到Python路径
app_dir = Path(__file__).resolve().parent / "app"
sys.path.insert(0, str(app_dir))

import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
