import os
import json
import pandas as pd
from datetime import datetime
import google.generativeai as genai
from app.services.file_service import FileService
from app.utils.constants import DocType
from app import config

class JDService:
    def __init__(self, api_key=None):
        self.file_service = FileService()
        
        # 初始化Gemini API
        if api_key:
            genai.configure(api_key=api_key)
        elif os.environ.get("GOOGLE_API_KEY"):
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        else:
            genai.configure(api_key=config.GEMINI_API_KEY)
        
        # 设置模型和生成参数
        self.model = genai.GenerativeModel(
            config.GEMINI_MODEL,
            generation_config={
                "temperature": config.GEMINI_TEMPERATURE,
                "max_output_tokens": config.GEMINI_MAX_OUTPUT_TOKENS,
                "top_p": config.GEMINI_TOP_P,
                "top_k": config.GEMINI_TOP_K
            }
        )
    
    def extract_criteria(self, jd_file_name):
        """从JD文件中提取criteria"""
        # 获取JD内容
        content, _ = self.file_service.get_raw_content(jd_file_name, DocType.JD)
        
        # 使用Gemini提取criteria
        prompt = f"""
        Extract key criteria from the following job description. 
        These criteria should include required skills, qualifications, experience, and certifications.
        Return the result as a JSON object with a single key 'criteria' containing an array of strings.
        
        Job Description:
        {content}
        
        Expected format:
        {{
          "criteria": [
            "criteria1",
            "criteria2",
            "criteria3",
            ...
          ]
        }}
        """
        
        response = self.model.generate_content(prompt)
        
        # 解析响应
        try:
            # 尝试从响应中提取JSON
            response_text = response.text
            # 查找JSON开始和结束的位置
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                criteria_json = json.loads(json_str)
                
                # 保存到CSV
                self._save_criteria(jd_file_name, criteria_json)
                
                return criteria_json
            else:
                raise ValueError("Could not find valid JSON in the response")
        except Exception as e:
            print(f"Error parsing criteria: {str(e)}")
            # 返回一个空的criteria列表
            return {"criteria": []}
    
    def _save_criteria(self, jd_file_name, criteria_json):
        """将提取的criteria保存到CSV"""
        criteria_str = json.dumps(criteria_json)
        
        new_row = pd.DataFrame([{
            'file_name': jd_file_name,
            'criteria': criteria_str,
            'analyzed_at': datetime.now()
        }])
        
        # 读取现有数据
        if os.path.exists(self.file_service.jd_analysis_path):
            df = pd.read_csv(self.file_service.jd_analysis_path)
            # 检查是否已存在该JD的分析
            df = df[df['file_name'] != jd_file_name]
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row
            
        # 保存回CSV
        df.to_csv(self.file_service.jd_analysis_path, index=False)
    
    def get_criteria(self, jd_file_name):
        """获取已保存的criteria，如果不存在则提取"""
        if os.path.exists(self.file_service.jd_analysis_path):
            df = pd.read_csv(self.file_service.jd_analysis_path)
            result = df[df['file_name'] == jd_file_name]
            
            if not result.empty:
                criteria_str = result.iloc[0]['criteria']
                return json.loads(criteria_str)
        
        # 如果不存在，则提取并返回
        return self.extract_criteria(jd_file_name)

    def analyze_jd(self, jd_file_name: str) -> dict:
        """
        Analyze JD and extract criteria for scoring.
        
        Args:
            jd_file_name: Name of the JD file
            
        Returns:
            Dictionary containing extracted criteria
        """
        # 从CSV文件中获取JD内容
        content, _ = self.file_service.get_raw_content(jd_file_name, 'JD')
        
        # 这里应该实现JD分析逻辑，提取评分标准
        # 例如，使用NLP技术提取关键技能、要求等
        
        # 简单示例：提取一些关键词作为标准
        criteria = {
            "skills": self._extract_skills(content),
            "education": self._extract_education(content),
            "experience": self._extract_experience(content)
        }
        
        # 保存分析结果到CSV
        self._save_jd_analysis(jd_file_name, criteria)
        
        return criteria
