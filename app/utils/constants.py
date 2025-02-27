from enum import Enum

class DocType(str, Enum):
    JD = "JD"
    RESUME = "Resume"

# CSV文件的列名常量
RAW_DATA_COLUMNS = ['file_name', 'content', 'extracted_at']
JD_ANALYSIS_COLUMNS = ['file_name', 'criteria', 'analyzed_at']
RESUME_ANALYSIS_COLUMNS = ['file_name', 'candidate_name', 'skills', 'analyzed_at']
SCORES_COLUMNS = ['resume_name', 'jd_name', 'scores', 'total_score', 'scored_at'] 