from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
import os

from app.api.routes import router

# 创建FastAPI应用
app = FastAPI(
    title="Resume Ranking API",
    description="API for ranking resumes against job descriptions",
    version="1.0.0"
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，在生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加根路径重定向
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# 包含API路由
app.include_router(router, prefix="/api")

# 确保必要的目录存在
os.makedirs("testdata/jd", exist_ok=True)
os.makedirs("testdata/resume", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("reports", exist_ok=True)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
