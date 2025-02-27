# Resume Scoring System

An AI-powered resume scoring system that automatically evaluates resumes based on job descriptions (JDs) and generates scoring reports.
video link:https://youtu.be/CQJwSjg-lCc

## Features

- Upload multiple JD files (PDF/DOCX format)
- Automatically extract scoring criteria from JDs
- Upload multiple resume files (PDF/DOCX format)
- Automatically score resumes against JD criteria
- Generate detailed scoring reports (Excel format)
- Command-line tool for batch processing

## System Architecture

```
app/
├── api/
│   └── routes.py          # API routes
├── services/
│   ├── file_service.py    # File handling service
│   ├── jd_service.py      # JD analysis service
│   └── resume_service.py  # Resume scoring service
├── utils/
│   └── constants.py       # Constants
├── config.py              # Configuration
└── main.py               # Main entry point

scripts/
└── export_scores.py      # Score export script

tests/
├── test_jd_analysis.py
├── test_resume_extraction.py
├── test_resume_scoring.py
└── test_export_scores.py
```

## API Endpoints

### 1. Upload JD Files

```http
POST /api/upload-jds
Content-Type: multipart/form-data

files: [file1.pdf, file2.docx, ...]
```

Response example:

```json
{
    "status": "success",
    "message": "Successfully uploaded 2 files",
    "data": {
        "uploaded_files": ["jd1.pdf", "jd2.docx"],
        "errors": [],
        "criteria": {
            "jd1.pdf": {
                "criteria": ["skill1", "skill2", ...]
            },
            "jd2.docx": {
                "criteria": ["requirement1", "requirement2", ...]
            }
        }
    }
}
```

### 2. Upload Resume Files

```http
POST /api/upload-resumes
Content-Type: multipart/form-data

files: [resume1.pdf, resume2.docx, ...]
```

Response example:

```json
{
    "status": "success",
    "message": "Successfully uploaded 2 files and scored against 2 JDs",
    "data": {
        "uploaded_files": ["resume1.pdf", "resume2.docx"],
        "errors": [],
        "scoring_results": {
            "jd1.pdf": {
                "criteria": {...},
                "scores": {
                    "resume1.pdf": {
                        "total_score": 85,
                        "detailed_scores": {...}
                    },
                    "resume2.docx": {
                        "total_score": 92,
                        "detailed_scores": {...}
                    }
                }
            }
        },
        "export": {
            "success": true,
            "path": "scores/scores_resume1_resume2_20240227_123456.xlsx"
        }
    }
}
```

## Command Line Tool

The system provides a command-line tool for batch processing resume scoring:

```bash
python scripts/export_scores.py --resume <resume_file> --jd <jd_file> --output <output_path>
```

Parameters:

- `--resume`: Resume filename (optional)
- `--jd`: JD filename (optional)
- `--output`: Output Excel file path (optional)
- `--all`: Score all resumes against all JDs

## Installation and Deployment

1. Clone the repository:

```bash
git clone <repository_url>
cd resume-scoring-system
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

   Setting the gemini api in config.py
4. Run the service:

```bash
uvicorn app.main:app --reload
```

## Testing

Run unit tests:

```bash
pytest tests/
```

## Directory Structure

- `app/`: Main application code
  - `api/`: API endpoint definitions
  - `services/`: Business logic services
  - `utils/`: Utility functions and constants
- `scripts/`: Command-line tools
- `tests/`: Test code
- `testdata/`: Test data directory
  - `jd/`: JD file storage directory
  - `resume/`: Resume file storage directory
- `scores/`: Score report export directory

## Important Notes

1. Supported file formats:

   - PDF (.pdf)
   - Word document (.docx)
2. Scoring criteria:

   - Each criterion: 0-5 points
   - 0: Not mentioned or irrelevant
   - 5: Perfect match

## Contribution guideline

    Ximing Tao

    cursor
