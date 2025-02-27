import sys
import os
import json

# 获取项目根目录的路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python的模块搜索路径中
sys.path.insert(0, project_root)

from app.services.jd_service import JDService
from app import config

def test_extract_criteria():
    print("Starting test_extract_criteria test...")
    
    # 确保当前工作目录是项目根目录
    os.chdir(project_root)
    
    # 使用配置文件中的API密钥
    api_key = config.GEMINI_API_KEY
    
    service = JDService(api_key)
    
    # 获取testdata/jd目录中的所有文件
    jd_dir = os.path.join(project_root, "testdata", "jd")
    files = os.listdir(jd_dir)
    
    # 遍历所有文件
    for file in files:
        file_name = os.path.basename(file)
        print(f"Processing JD: {file_name}")
        
        # 提取criteria
        criteria_json = service.extract_criteria(file_name)
        
        # 打印结果
        print(f"Extracted criteria for {file_name}:")
        print(json.dumps(criteria_json, indent=2))
        
        # 验证结果
        assert 'criteria' in criteria_json, f"No criteria found in the response for {file_name}"
        assert isinstance(criteria_json['criteria'], list), f"Criteria is not a list for {file_name}"
        assert len(criteria_json['criteria']) > 0, f"No criteria items found for {file_name}"
        
        print(f"Successfully extracted criteria for {file_name}")
        print("=" * 50)

if __name__ == "__main__":
    test_extract_criteria() 