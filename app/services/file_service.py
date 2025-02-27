import os
from typing import Literal, Tuple
import pandas as pd
from datetime import datetime
import PyPDF2
from docx import Document
import re

class FileService:
    def __init__(self):
        # 使用CSV文件替代Excel
        self.raw_jd_path = "data/raw_jd.csv"
        self.raw_resume_path = "data/raw_resume.csv"
        self.jd_analysis_path = "data/jd_analysis.csv"
        self.resume_analysis_path = "data/resume_analysis.csv"
        self.scores_path = "data/scores.csv"
        self._init_csv_files()

    def _init_csv_files(self):
        """Initialize CSV files if they don't exist"""
        os.makedirs("data", exist_ok=True)
        
        # 创建所需的CSV文件
        files_and_columns = {
            self.raw_jd_path: ['file_name', 'content', 'extracted_at'],
            self.raw_resume_path: ['file_name', 'content', 'extracted_at'],
            self.jd_analysis_path: ['file_name', 'criteria', 'analyzed_at'],
            self.resume_analysis_path: ['file_name', 'candidate_name', 'skills', 'analyzed_at'],
            self.scores_path: ['resume_name', 'jd_name', 'scores', 'total_score', 'scored_at']
        }
        
        for file_path, columns in files_and_columns.items():
            if not os.path.exists(file_path):
                pd.DataFrame(columns=columns).to_csv(file_path, index=False)

    def clean_text(self, text: str) -> str:
        """清理文本，去除乱码和特殊字符"""
        # 1. 替换常见的Unicode控制字符和不可打印字符
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # 2. 替换特殊的Unicode字符（如特殊符号、表情符号等）
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        
        # 3. 替换多个空格为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 4. 替换多个换行为单个换行
        text = re.sub(r'\n+', '\n', text)
        
        # 5. 去除行首和行尾的空白字符
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
        
        return text.strip()

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from PDF or DOCX file"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return self.clean_text(text.strip())
                
        elif file_extension == '.docx':
            doc = Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return self.clean_text(text.strip())
            
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def save_raw_content(self, 
                        file_path: str, 
                        doc_type: Literal['JD', 'Resume']) -> None:
        """Save extracted content to CSV"""
        content = self.extract_text_from_file(file_path)
        file_name = os.path.basename(file_path)
        
        new_row = pd.DataFrame([{
            'file_name': file_name,
            'content': content,
            'extracted_at': datetime.now()
        }])
        
        # 选择正确的CSV文件
        csv_path = self.raw_jd_path if doc_type == 'JD' else self.raw_resume_path
        
        # 读取现有数据
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row
            
        # 保存回CSV
        df.to_csv(csv_path, index=False)

    def get_raw_content(self, 
                       file_name: str, 
                       doc_type: Literal['JD', 'Resume']) -> Tuple[str, datetime]:
        """Get content and extraction time from CSV"""
        csv_path = self.raw_jd_path if doc_type == 'JD' else self.raw_resume_path
        df = pd.read_csv(csv_path)
        result = df[df['file_name'] == file_name]
        
        if result.empty:
            raise ValueError(f"No content found for file: {file_name}")
            
        return result.iloc[0]['content'], pd.to_datetime(result.iloc[0]['extracted_at']) 