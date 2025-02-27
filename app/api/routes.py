from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks

from fastapi.responses import FileResponse

from typing import List, Optional

import os

import shutil

import uuid

import tempfile

from datetime import datetime

import pandas as pd

from app.services.file_service import FileService

from app.services.jd_service import JDService

from app.services.resume_service import ResumeService

from app.utils.constants import DocType

from app import config

import json

from typing_extensions import Annotated
from pydantic import BaseModel



router = APIRouter()

file_service = FileService()

jd_service = JDService()

resume_service = ResumeService()

# 全局变量，用于存储上传的JD文件和它们的评分标准
uploaded_jd_files = {}



class UploadResponse(BaseModel):
    """Response model for file upload endpoints"""
    status: str
    message: str
    data: dict

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Successfully uploaded 2 files",
                "data": {
                    "uploaded_files": ["jd1.pdf", "jd2.docx"],
                    "errors": [],
                    "criteria": {
                        "jd1.pdf": {
                            "criteria": ["Python", "Machine Learning", "SQL"]
                        }
                    }
                }
            }
        }



@router.post(
    "/upload-jds",
    response_model=UploadResponse,
    summary="Upload multiple JD files",
    description="Upload multiple Job Description files (PDF/DOCX format) and extract scoring criteria.",
    response_description="Returns a list of uploaded file names and extracted criteria"
)
async def upload_jds(
    files: Annotated[
        List[UploadFile],
        File(
            description="Multiple JD files to upload (PDF/DOCX format)",
            example=["senior_ml_engineer.pdf", "data_scientist.docx"]
        )
    ]
):
    """
    Upload multiple Job Description (JD) files and extract scoring criteria.
    
    The endpoint will:
    - Accept multiple PDF/DOCX files
    - Save files to the JD directory
    - Extract text content from files
    - Analyze JDs to identify key requirements
    - Return extracted criteria for each JD
    
    Parameters:
    - files: List of files to upload (PDF/DOCX format)
    
    Returns:
    - status: Success/error status
    - message: Operation result message
    - data: Dictionary containing:
        - uploaded_files: List of successfully uploaded files
        - errors: List of any errors encountered
        - criteria: Dictionary of extracted criteria for each JD
    
    Raises:
    - 400: No files provided or invalid file format
    - 500: Server error during processing
    """
    global uploaded_jd_files
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    errors = []
    criteria_results = {}
    
    # 确保目录存在
    os.makedirs("testdata/jd", exist_ok=True)
    
    for file in files:
        # 检查文件类型
        if not file.filename.endswith(('.pdf', '.PDF', '.docx', '.DOCX')):
            errors.append({
                "file": file.filename,
                "error": "Unsupported file format. Only PDF and DOCX are supported."
            })
            continue
        
        # 保存文件到目标位置
        file_path = os.path.join("testdata/jd", file.filename)
        try:
            # 读取上传文件的内容
            content = await file.read()
            
            # 写入到目标文件
            with open(file_path, "wb") as f:
                f.write(content)
            
            uploaded_files.append(file.filename)
        except Exception as e:
            errors.append({
                "file": file.filename,
                "error": str(e)
            })
            print(f"Error saving file {file.filename}: {str(e)}")
            continue
    
    # 提取所有上传文件的文本并分析JD
    for filename in uploaded_files:
        try:
            # 构建完整的文件路径
            file_path = os.path.join("testdata/jd", filename)
            
            # 保存原始内容
            file_service.save_raw_content(file_path, 'JD')
            
            # 分析JD并提取评分标准
            print(f"Calling get_criteria for {filename}")
            criteria = jd_service.get_criteria(filename)
            print(f"Criteria for {filename}: {criteria}")
            criteria_results[filename] = criteria
            
            # 将JD文件和评分标准存储到全局变量中
            uploaded_jd_files[filename] = criteria
        except Exception as e:
            print(f"Error getting criteria for {filename}: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    return {
        "status": "success" if uploaded_files else "error",
        "message": f"Successfully uploaded {len(uploaded_files)} files" if uploaded_files else "Failed to upload any files",
        "data": {
            "uploaded_files": uploaded_files,
            "errors": errors,
            "criteria": criteria_results
        }
    }



@router.post(
    "/upload-resumes",
    response_model=UploadResponse,
    summary="Upload and score multiple resume files",
    description="Upload multiple resume files and score them against previously uploaded JDs.",
    response_description="Returns upload status, scoring results and Excel report path"
)
async def upload_resumes(
    files: Annotated[
        List[UploadFile],
        File(
            description="Multiple resume files to upload (PDF/DOCX format)",
            example=["john_doe_resume.pdf", "jane_smith_resume.docx"]
        )
    ]
):
    """
    Upload multiple resume files and score them against previously uploaded JDs.
    
    The endpoint will:
    - Accept multiple PDF/DOCX files
    - Save files to the resume directory
    - Extract text content from files
    - Score each resume against all uploaded JDs
    - Generate an Excel report with detailed scores
    
    Parameters:
    - files: List of files to upload (PDF/DOCX format)
    
    Returns:
    - status: Success/error status
    - message: Operation result message
    - data: Dictionary containing:
        - uploaded_files: List of successfully uploaded files
        - errors: List of any errors encountered
        - scoring_results: Dictionary of scoring results
        - export: Excel report details
    
    Raises:
    - 400: No files provided or invalid file format
    - 404: No JDs found for scoring
    - 500: Server error during processing
    """
    global uploaded_jd_files
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    errors = []
    
    # 确保目录存在
    os.makedirs("testdata/resume", exist_ok=True)
    os.makedirs("scores", exist_ok=True)
    
    for file in files:
        # 检查文件类型
        if not file.filename.endswith(('.pdf', '.PDF', '.docx', '.DOCX')):
            errors.append({
                "file": file.filename,
                "error": "Unsupported file format. Only PDF and DOCX are supported."
            })
            continue
        
        # 保存文件到目标位置
        file_path = os.path.join("testdata/resume", file.filename)
        try:
            # 读取上传文件的内容
            content = await file.read()
            
            # 写入到目标文件
            with open(file_path, "wb") as f:
                f.write(content)
            
            uploaded_files.append(file.filename)
        except Exception as e:
            errors.append({
                "file": file.filename,
                "error": str(e)
            })
            print(f"Error saving file {file.filename}: {str(e)}")
            continue
    
    # 提取所有上传文件的文本
    for filename in uploaded_files:
        try:
            # 构建完整的文件路径
            file_path = os.path.join("testdata/resume", filename)
            
            # 保存原始内容
            file_service.save_raw_content(file_path, 'Resume')
        except Exception as e:
            print(f"Error extracting text from {filename}: {str(e)}")
    
    # 获取之前上传的JD文件
    jd_files = list(uploaded_jd_files.keys())
    
    if not jd_files:
        return {
            "status": "success",
            "message": f"Successfully uploaded {len(uploaded_files)} files, but no JD files found for scoring",
            "data": {
                "uploaded_files": uploaded_files,
                "errors": errors
            }
        }
    
    # 对所有组合进行评分
    scoring_results = {}
    
    # 清除之前的评分结果，确保只保留新的评分
    if os.path.exists(file_service.scores_path):
        try:
            df = pd.read_csv(file_service.scores_path)
            # 只保留不涉及当前上传简历的评分
            df = df[~df['resume_name'].isin(uploaded_files)]
            df.to_csv(file_service.scores_path, index=False)
        except Exception as e:
            print(f"Error clearing previous scores: {str(e)}")
    
    for jd_file in jd_files:
        print(f"Processing JD: {jd_file}")
        jd_scores = {}
        
        for resume_file in uploaded_files:
            print(f"  Scoring resume: {resume_file}")
            try:
                # 评分
                score = resume_service.score_resume(resume_file, jd_file)
                
                # 获取JD的评分标准
                jd_criteria = uploaded_jd_files.get(jd_file, {})
                
                jd_scores[resume_file] = {
                    "total_score": score.get("total_score", 0),
                    "detailed_scores": score.get("detailed_scores", {})
                }
            except Exception as e:
                jd_scores[resume_file] = {
                    "error": str(e)
                }
                print(f"  Error scoring resume {resume_file} against JD {jd_file}: {str(e)}")
        
        scoring_results[jd_file] = {
            "criteria": uploaded_jd_files.get(jd_file, {}),
            "scores": jd_scores
        }
    
    # 导出评分结果为Excel
    try:
        # 生成Excel文件名
        candidates = "_".join([os.path.splitext(f)[0] for f in uploaded_files])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"scores_{candidates}_{timestamp}.xlsx"
        excel_path = os.path.join("scores", excel_filename)
        
        # 导出评分结果，只导出当前上传的简历文件的评分
        excel_file = resume_service.export_scores_to_excel(
            jd_files=jd_files,
            resume_files=uploaded_files,
            output_path=excel_path
        )
        export_success = True
        export_path = excel_file
    except Exception as e:
        export_success = False
        export_path = None
        print(f"Error exporting scores to Excel: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    return {
        "status": "success" if uploaded_files else "error",
        "message": f"Successfully uploaded {len(uploaded_files)} files and scored against {len(jd_files)} JDs" if uploaded_files else "Failed to upload any files",
        "data": {
            "uploaded_files": uploaded_files,
            "errors": errors,
            "scoring_results": scoring_results,
            "export": {
                "success": export_success,
                "path": export_path
            }
        }
    }


