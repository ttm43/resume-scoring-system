import sys
import os
import json

# 获取项目根目录的路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python的模块搜索路径中
sys.path.insert(0, project_root)

from app.services.resume_service import ResumeService
from app import config

def test_score_resumes():
    print("Starting test_score_resumes test...")
    
    # 确保当前工作目录是项目根目录
    os.chdir(project_root)
    
    # 使用配置文件中的API密钥
    api_key = config.GEMINI_API_KEY
    
    service = ResumeService(api_key)
    
    # 获取testdata/resume目录中的所有文件
    resume_dir = os.path.join(project_root, "testdata", "resume")
    resume_files = [os.path.basename(f) for f in os.listdir(resume_dir)]
    
    # 获取testdata/jd目录中的所有文件
    jd_dir = os.path.join(project_root, "testdata", "jd")
    jd_files = [os.path.basename(f) for f in os.listdir(jd_dir)]
    
    if not jd_files:
        print("No JD files found")
        return
    
    # 遍历所有JD文件
    for jd_file in jd_files:
        print(f"\nProcessing JD: {jd_file}")
        
        # 遍历所有简历文件
        for resume_file in resume_files:
            print(f"Processing resume: {resume_file} against JD: {jd_file}")
            
            # 评分简历
            score_json = service.score_resume(resume_file, jd_file)
            
            # 打印结果
            print(f"Score for {resume_file} against {jd_file}:")
            print(json.dumps(score_json, indent=2))
            
            # 验证结果
            assert 'candidate_name' in score_json, f"No candidate name found in the response for {resume_file}"
            assert 'scores' in score_json, f"No scores found in the response for {resume_file}"
            assert 'total_score' in score_json, f"No total score found in the response for {resume_file}"
            
            print(f"Successfully scored resume {resume_file} against JD {jd_file}")
            print("-" * 50)
        
        # 获取该JD的所有评分
        jd_scores = service.get_scores(jd_file_name=jd_file)
        print(f"\nAll scores for JD {jd_file}:")
        for score in jd_scores:
            print(f"Resume: {score['resume_name']}, Total Score: {score['total_score']}")
        
        # 按总分排序
        sorted_scores = sorted(jd_scores, key=lambda x: x['total_score'], reverse=True)
        print("\nRanked resumes for JD {jd_file}:")
        for i, score in enumerate(sorted_scores, 1):
            print(f"{i}. Resume: {score['resume_name']}, Total Score: {score['total_score']}")
        
        # 导出评分结果到CSV
        csv_path = service.export_scores_to_csv(jd_file_name=jd_file)
        if csv_path:
            print(f"\nScores for JD {jd_file} exported to CSV: {csv_path}")
        
        print("=" * 50)
    
    # 获取所有评分
    all_scores = service.get_scores()
    print(f"\nAll scores for all JDs:")
    for score in all_scores:
        print(f"Resume: {score['resume_name']}, JD: {score['jd_name']}, Total Score: {score['total_score']}")
    
    # 导出所有评分结果到CSV
    csv_path = service.export_scores_to_csv()
    if csv_path:
        print(f"\nAll scores exported to CSV: {csv_path}")

if __name__ == "__main__":
    test_score_resumes() 