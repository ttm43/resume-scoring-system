import os
import json
import pandas as pd
from datetime import datetime
import google.generativeai as genai
from app.services.file_service import FileService
from app.services.jd_service import JDService
from app.utils.constants import DocType
from app import config

class ResumeService:
    def __init__(self, api_key=None):
        self.file_service = FileService()
        self.jd_service = JDService(api_key)
        
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
    
    def score_resume(self, resume_file_name, jd_file_name):
        """根据JD中的criteria对简历进行评分"""
        # 获取简历内容
        resume_content, _ = self.file_service.get_raw_content(resume_file_name, DocType.RESUME)
        
        # 获取JD的criteria
        criteria_json = self.jd_service.get_criteria(jd_file_name)
        criteria_list = criteria_json.get('criteria', [])
        
        if not criteria_list:
            return {"error": "No criteria found for the job description"}
        
        # 使用Gemini评分
        prompt = f"""
        Score the following resume against the job criteria. 
        For each criterion, assign a score from 0 to 5, where:
        0 = Not mentioned or not relevant
        1 = Barely mentioned
        2 = Somewhat relevant
        3 = Relevant
        4 = Very relevant
        5 = Perfectly matches
        
        Also extract the candidate's name from the resume.
        
        Resume:
        {resume_content}
        
        Criteria:
        {json.dumps(criteria_list, indent=2)}
        
        Return the result as a JSON object with the following format:
        {{
          "candidate_name": "Full Name",
          "scores": {{
            "criteria1": score1,
            "criteria2": score2,
            ...
          }},
          "total_score": sum_of_all_scores
        }}
        
        Make sure to include a score for each criterion listed above.
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
                score_json = json.loads(json_str)
                
                # 验证所有criteria都有评分
                scores = score_json.get('scores', {})
                for criterion in criteria_list:
                    if criterion not in scores:
                        scores[criterion] = 0
                
                # 重新计算总分
                total_score = sum(scores.values())
                score_json['scores'] = scores
                score_json['total_score'] = total_score
                
                # 保存到CSV
                self._save_score(resume_file_name, jd_file_name, score_json)
                
                return score_json
            else:
                raise ValueError("Could not find valid JSON in the response")
        except Exception as e:
            print(f"Error parsing score: {str(e)}")
            # 返回一个空的评分
            return {"candidate_name": "Unknown", "scores": {}, "total_score": 0}
    
    def _save_score(self, resume_file_name, jd_file_name, score_json):
        """将评分保存到CSV"""
        scores_str = json.dumps(score_json.get('scores', {}))
        
        new_row = pd.DataFrame([{
            'resume_name': resume_file_name,
            'jd_name': jd_file_name,
            'scores': scores_str,
            'total_score': score_json.get('total_score', 0),
            'scored_at': datetime.now()
        }])
        
        # 读取现有数据
        if os.path.exists(self.file_service.scores_path):
            df = pd.read_csv(self.file_service.scores_path)
            # 检查是否已存在该简历和JD的评分
            df = df[(df['resume_name'] != resume_file_name) | (df['jd_name'] != jd_file_name)]
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row
            
        # 保存回CSV
        df.to_csv(self.file_service.scores_path, index=False)
        
        # 保存候选人信息到resume_analysis
        self._save_candidate_info(resume_file_name, score_json)
    
    def _save_candidate_info(self, resume_file_name, score_json):
        """将候选人信息保存到CSV"""
        candidate_name = score_json.get('candidate_name', 'Unknown')
        skills = json.dumps(score_json.get('scores', {}))
        
        new_row = pd.DataFrame([{
            'file_name': resume_file_name,
            'candidate_name': candidate_name,
            'skills': skills,
            'analyzed_at': datetime.now()
        }])
        
        # 读取现有数据
        if os.path.exists(self.file_service.resume_analysis_path):
            df = pd.read_csv(self.file_service.resume_analysis_path)
            # 检查是否已存在该简历的分析
            df = df[df['file_name'] != resume_file_name]
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = new_row
            
        # 保存回CSV
        df.to_csv(self.file_service.resume_analysis_path, index=False)
    
    def get_scores(self, resume_file_name=None, jd_file_name=None):
        """获取评分结果"""
        if not os.path.exists(self.file_service.scores_path):
            return []
        
        df = pd.read_csv(self.file_service.scores_path)
        
        if resume_file_name and jd_file_name:
            # 获取特定简历和JD的评分
            result = df[(df['resume_name'] == resume_file_name) & (df['jd_name'] == jd_file_name)]
        elif resume_file_name:
            # 获取特定简历的所有评分
            result = df[df['resume_name'] == resume_file_name]
        elif jd_file_name:
            # 获取特定JD的所有评分
            result = df[df['jd_name'] == jd_file_name]
        else:
            # 获取所有评分
            result = df
        
        # 转换为字典列表
        scores = []
        for _, row in result.iterrows():
            score_dict = {
                'resume_name': row['resume_name'],
                'jd_name': row['jd_name'],
                'scores': json.loads(row['scores']) if isinstance(row['scores'], str) else {},
                'total_score': row['total_score'],
                'scored_at': row['scored_at']
            }
            scores.append(score_dict)
        
        return scores
    
    def get_detailed_scores(self, jd_file_name=None):
        """获取详细的评分结果，包括每个criteria的评分"""
        scores = self.get_scores(jd_file_name=jd_file_name)
        
        if not scores:
            return pd.DataFrame()
        
        # 获取所有criteria
        all_criteria = set()
        for score in scores:
            all_criteria.update(score['scores'].keys())
        
        # 创建DataFrame
        data = []
        for score in scores:
            row = {
                'Resume': score['resume_name'],
                'Candidate': 'Unknown',
                'Total Score': score['total_score']
            }
            
            # 获取候选人姓名
            if os.path.exists(self.file_service.resume_analysis_path):
                resume_df = pd.read_csv(self.file_service.resume_analysis_path)
                candidate_info = resume_df[resume_df['file_name'] == score['resume_name']]
                if not candidate_info.empty:
                    row['Candidate'] = candidate_info.iloc[0]['candidate_name']
            
            # 添加每个criteria的评分
            for criterion in all_criteria:
                row[criterion] = score['scores'].get(criterion, 0)
            
            data.append(row)
        
        # 创建DataFrame并按总分排序
        df = pd.DataFrame(data)
        df = df.sort_values('Total Score', ascending=False)
        
        # 重新排列列，使Resume、Candidate和Total Score在前面
        columns = ['Resume', 'Candidate', 'Total Score'] + sorted(list(all_criteria))
        df = df[columns]
        
        return df 
    
    def export_scores_to_excel(self, jd_files=None, resume_files=None, output_path=None):
        """
        将评分结果导出为Excel文件，每个JD一个工作表
        
        Args:
            jd_files: 要导出的JD文件列表，如果为None，则导出所有JD
            resume_files: 要导出的简历文件列表，如果为None，则导出所有简历
            output_path: 输出Excel文件的路径，如果为None，则使用默认路径
        
        Returns:
            导出的Excel文件路径
        """
        # 获取所有评分
        all_scores = self.get_scores()
        
        if not all_scores:
            print("No scores to export")
            return None
        
        # 如果指定了JD文件，则只导出这些JD的评分
        if jd_files:
            all_scores = [s for s in all_scores if s['jd_name'] in jd_files]
        
        # 如果指定了简历文件，则只导出这些简历的评分
        if resume_files:
            all_scores = [s for s in all_scores if s['resume_name'] in resume_files]
        
        if not all_scores:
            print("No scores match the specified filters")
            return None
        
        # 按JD分组
        jd_groups = {}
        for score in all_scores:
            jd_name = score['jd_name']
            if jd_name not in jd_groups:
                jd_groups[jd_name] = []
            jd_groups[jd_name].append(score)
        
        # 如果未指定输出路径，则使用默认路径
        if output_path is None:
            # 创建输出目录
            output_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"resume_scores_{timestamp}.xlsx")
        
        # 创建Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 为每个JD创建一个工作表
            for jd_name, scores in jd_groups.items():
                # 获取该JD的criteria
                all_criteria = set()
                for score in scores:
                    all_criteria.update(score['scores'].keys())
                
                # 创建DataFrame
                data = []
                for score in scores:
                    row = {
                        'Resume': score['resume_name'],
                        'Candidate': 'Unknown',
                        'Total Score': score['total_score']
                    }
                    
                    # 获取候选人姓名
                    if os.path.exists(self.file_service.resume_analysis_path):
                        resume_df = pd.read_csv(self.file_service.resume_analysis_path)
                        candidate_info = resume_df[resume_df['file_name'] == score['resume_name']]
                        if not candidate_info.empty:
                            row['Candidate'] = candidate_info.iloc[0]['candidate_name']
                    
                    # 添加每个criteria的评分
                    for criterion in all_criteria:
                        row[criterion] = score['scores'].get(criterion, 0)
                    
                    data.append(row)
                
                # 创建DataFrame并按总分排序
                df = pd.DataFrame(data)
                if not df.empty:
                    df = df.sort_values('Total Score', ascending=False)
                    
                    # 重新排列列，使Resume、Candidate和Total Score在前面
                    columns = ['Resume', 'Candidate', 'Total Score'] + sorted(list(all_criteria))
                    df = df[columns]
                    
                    # 创建工作表名称（去除不允许的字符）
                    sheet_name = os.path.splitext(jd_name)[0]
                    # Excel工作表名称不能超过31个字符
                    if len(sheet_name) > 31:
                        sheet_name = sheet_name[:28] + "..."
                    # 替换不允许的字符
                    sheet_name = sheet_name.replace(':', '_').replace('\\', '_').replace('/', '_').replace('?', '_').replace('*', '_').replace('[', '_').replace(']', '_')
                    
                    # 将DataFrame写入Excel工作表
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 创建一个汇总工作表
            summary_data = []
            for jd_name, scores in jd_groups.items():
                for score in scores:
                    summary_data.append({
                        'JD': jd_name,
                        'Resume': score['resume_name'],
                        'Candidate': 'Unknown',
                        'Total Score': score['total_score']
                    })
            
            # 获取候选人姓名
            if os.path.exists(self.file_service.resume_analysis_path):
                resume_df = pd.read_csv(self.file_service.resume_analysis_path)
                for i, row in enumerate(summary_data):
                    candidate_info = resume_df[resume_df['file_name'] == row['Resume']]
                    if not candidate_info.empty:
                        summary_data[i]['Candidate'] = candidate_info.iloc[0]['candidate_name']
            
            # 创建汇总DataFrame并按JD和总分排序
            summary_df = pd.DataFrame(summary_data)
            if not summary_df.empty:
                summary_df = summary_df.sort_values(['JD', 'Total Score'], ascending=[True, False])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Scores exported to {output_path}")
        return output_path 