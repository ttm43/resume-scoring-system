import sys
import os
import pandas as pd

# 获取项目根目录的路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python的模块搜索路径中
sys.path.insert(0, project_root)

from app.services.resume_service import ResumeService
from app import config

def test_export_scores():
    print("Starting test_export_scores test...")
    
    # 确保当前工作目录是项目根目录
    os.chdir(project_root)
    
    # 使用配置文件中的API密钥
    api_key = config.GEMINI_API_KEY
    
    service = ResumeService(api_key)
    
    # 获取testdata/jd目录中的所有文件
    jd_dir = os.path.join(project_root, "testdata", "jd")
    jd_files = [os.path.basename(f) for f in os.listdir(jd_dir)]
    
    if not jd_files:
        print("No JD files found")
        return
    
    # 为每个JD导出评分结果
    for jd_file in jd_files:
        print(f"Exporting scores for JD: {jd_file}")
        
        # 导出评分结果
        csv_path = service.export_scores_to_csv(jd_file_name=jd_file)
        
        if csv_path:
            print(f"Scores exported to: {csv_path}")
            
            # 验证导出的CSV文件
            df = pd.read_csv(csv_path)
            print(f"Exported CSV contains {len(df)} rows and {len(df.columns)} columns")
            print("Columns:", df.columns.tolist())
            
            # 打印前几行
            print("\nFirst few rows:")
            print(df.head())
        else:
            print(f"No scores to export for JD: {jd_file}")
        
        print("=" * 50)
    
    # 导出所有JD的评分结果
    print("Exporting scores for all JDs")
    csv_path = service.export_scores_to_csv()
    
    if csv_path:
        print(f"All scores exported to: {csv_path}")
        
        # 验证导出的CSV文件
        df = pd.read_csv(csv_path)
        print(f"Exported CSV contains {len(df)} rows and {len(df.columns)} columns")
        print("Columns:", df.columns.tolist())
        
        # 打印前几行
        print("\nFirst few rows:")
        print(df.head())
    else:
        print("No scores to export")

if __name__ == "__main__":
    test_export_scores() 