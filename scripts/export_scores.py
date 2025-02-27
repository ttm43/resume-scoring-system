import sys
import os
import argparse

# 获取项目根目录的路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python的模块搜索路径中
sys.path.insert(0, project_root)

from app.services.resume_service import ResumeService
from app import config

def main():
    parser = argparse.ArgumentParser(description='Export resume scores to Excel')
    parser.add_argument('--resume', help='Resume file name (optional)')
    parser.add_argument('--jd', help='JD file name (optional)')
    parser.add_argument('--output', help='Output Excel file path (optional)')
    parser.add_argument('--all', action='store_true', help='Score all resumes against all JDs')
    args = parser.parse_args()
    
    # 确保当前工作目录是项目根目录
    os.chdir(project_root)
    
    # 使用配置文件中的API密钥
    api_key = config.GEMINI_API_KEY
    
    service = ResumeService(api_key)
    
    if args.all:
        # 获取所有JD和简历文件
        jd_dir = os.path.join(project_root, "testdata", "jd")
        resume_dir = os.path.join(project_root, "testdata", "resume")
        
        jd_files = [os.path.basename(f) for f in os.listdir(jd_dir)]
        resume_files = [os.path.basename(f) for f in os.listdir(resume_dir)]
        
        # 对所有组合进行评分
        for jd_file in jd_files:
            print(f"Processing JD: {jd_file}")
            for resume_file in resume_files:
                print(f"  Scoring resume: {resume_file}")
                try:
                    service.score_resume(resume_file, jd_file)
                except Exception as e:
                    print(f"  Error scoring resume {resume_file} against JD {jd_file}: {str(e)}")
        
        # 导出所有评分结果
        excel_path = service.export_scores_to_excel(output_path=args.output)
        if excel_path:
            print(f"All scores exported to: {excel_path}")
        else:
            print("No scores to export")
    elif args.jd and args.resume:
        # 评分特定的JD和简历组合
        print(f"Scoring resume {args.resume} against JD {args.jd}")
        try:
            service.score_resume(args.resume, args.jd)
            # 导出评分结果
            excel_path = service.export_scores_to_excel(output_path=args.output)
            if excel_path:
                print(f"Scores exported to: {excel_path}")
            else:
                print("No scores to export")
        except Exception as e:
            print(f"Error scoring resume {args.resume} against JD {args.jd}: {str(e)}")
    else:
        # 导出已有的评分结果
        excel_path = service.export_scores_to_excel(output_path=args.output)
        if excel_path:
            print(f"Scores exported to: {excel_path}")
        else:
            print("No scores to export")

if __name__ == "__main__":
    main() 