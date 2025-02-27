import os

# Gemini API配置
GEMINI_API_KEY = "xxxxxxxxxxxxxxxxxxx" # replace with your own key
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_TEMPERATURE = 0.2  # 较低的温度使输出更确定性
GEMINI_MAX_OUTPUT_TOKENS = 1024  # 最大输出长度
GEMINI_TOP_P = 0.95  # 控制输出的多样性
GEMINI_TOP_K = 40  # 控制输出的多样性

# 文件路径配置
DATA_DIR = "data"
RAW_JD_PATH = os.path.join(DATA_DIR, "raw_jd.csv")
RAW_RESUME_PATH = os.path.join(DATA_DIR, "raw_resume.csv")
JD_ANALYSIS_PATH = os.path.join(DATA_DIR, "jd_analysis.csv")
RESUME_ANALYSIS_PATH = os.path.join(DATA_DIR, "resume_analysis.csv")
SCORES_PATH = os.path.join(DATA_DIR, "scores.csv") 