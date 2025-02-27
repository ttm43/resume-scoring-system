import sys
import os
import pandas as pd

# 获取项目根目录的路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python的模块搜索路径中
sys.path.insert(0, project_root)

import pytest
from app.services.file_service import FileService

def test_extract_and_save_to_csv():
    print("Starting test_extract_and_save_to_csv test...")
    
    # 确保当前工作目录是项目根目录
    os.chdir(project_root)
    
    service = FileService()
    
    # 获取testdata/jd目录中的所有文件
    jd_dir = os.path.join(project_root, "testdata", "jd")
    files = os.listdir(jd_dir)
    
    # 创建一个列表来存储提取的内容
    extracted_data = []
    
    # 遍历所有文件
    for file in files:
        file_path = os.path.join(jd_dir, file)
        print(f"Processing file: {file_path}")
        
        # 确定文件类型
        file_type = "JD"
        
        # 保存并提取内容
        try:
            service.save_raw_content(file_path, file_type)
            # 使用文件名（不包括路径）来获取内容
            file_name = os.path.basename(file_path)
            content, time = service.get_raw_content(file_name, file_type)
            print(f"Successfully extracted content from {file_name}. Content length: {len(content)}")
            
            # 将提取的内容添加到列表中
            extracted_data.append({
                "File Name": file_name,
                "File Type": file_type,
                "Content": content,  # 保存完整内容
                "Extraction Time": time
            })
        except Exception as e:
            print(f"Error extracting content from {file}: {str(e)}")
    
    # 将提取的内容保存到CSV文件中
    if extracted_data:
        df = pd.DataFrame(extracted_data)
        csv_path = os.path.join(project_root, "extracted_content_full.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved extracted content to {csv_path}")
        
        # 验证CSV文件是否已创建
        assert os.path.exists(csv_path), f"CSV file {csv_path} was not created"
        
        # 读取CSV文件以验证内容
        df_read = pd.read_csv(csv_path)
        assert len(df_read) == len(extracted_data), f"CSV file contains {len(df_read)} rows, expected {len(extracted_data)}"
        print("CSV file validation passed")
        
        # 验证原始数据CSV文件是否包含提取的内容
        raw_jd_path = os.path.join(project_root, "data", "raw_jd.csv")
        assert os.path.exists(raw_jd_path), f"Raw JD CSV file {raw_jd_path} was not created"
        raw_df = pd.read_csv(raw_jd_path)
        assert len(raw_df) >= len(extracted_data), f"Raw JD CSV file contains {len(raw_df)} rows, expected at least {len(extracted_data)}"
        print("Raw JD CSV file validation passed")
    else:
        print("No content was extracted")
        assert False, "No content was extracted from any file"

if __name__ == "__main__":
    test_extract_and_save_to_csv() 