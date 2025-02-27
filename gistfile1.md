
### **Coding Assessment Documentation**

---

### **Problem Statement**

Design and implement two API endpoints using FastAPI or Flask that automate the process of ranking resumes based on job descriptions. The assessment evaluates candidates on their ability to handle text extraction, data processing, and structured outputs through REST APIs.  
**Note:** Candidates must use FastAPI or Flask, implement a well-documented Swagger UI, and provide a loom video explaining their process and how they built the solution and a working demo.

---

### **Task 1: Extract Ranking Criteria from Job Description**

**Description:**  
Develop an API endpoint that accepts a job description file (PDF or DOCX), extracts key ranking criteria, and returns a structured JSON response. You may use any publicly available job description for testing. Feel free to use any LLM of your choice, including OpenAI, Gemini, Claude, Grok, or locally run models.

**API Endpoint:**  
```
POST /extract-criteria
```

**Input Payload Example (Multipart Form-Data):**  
```json
{
  "file": "<uploaded_job_description.pdf>"
}
```

**Output Payload Example:**  
```json
{
  "criteria": [
    "Must have certification XYZ",
    "5+ years of experience in Python development",
    "Strong background in Machine Learning"
  ]
}
```

**Requirements for Task 1:**  
- Use FastAPI or Flask.
- Avoid using LangChain, prefer OpenAI SDK, LiteLLM or Google google-genai SDK.
- Extract text from the provided file.
- Identify key ranking criteria such as skills, certifications, experience, and qualifications.
- Ensure the system works with different ranking criteria provided by the user.
- Return structured JSON output as a list of strings for each extracted criterion.
- Implement Swagger UI with clear documentation for this endpoint.

---

### **Task 2: Score Resumes Against Extracted Criteria**

**Description:**  
Develop an API endpoint that accepts ranking criteria and multiple resumes (PDF or DOCX), processes the resumes, scores them based on the given criteria, and returns an Excel or CSV sheet containing each candidate's score. You may use any publicly available resumes for testing. Feel free to use any LLM of your choice, including OpenAI, Gemini, Claude, Grok, or locally run models.

**API Endpoint:**  
```
POST /score-resumes
```

**Input Payload Example (Multipart Form-Data):**  
```json
{
  "criteria": [
    "Must have certification XYZ",
    "5+ years of experience in Python development",
    "Strong background in Machine Learning"
  ],
  "files": [
    "<uploaded_resume_1.pdf>",
    "<uploaded_resume_2.docx>",
    "<uploaded_resume_3.pdf>"
  ]
}
```

**Output Payload Example (Excel or CSV Sheet):**

| Candidate Name | Certification XYZ | Python Experience | Machine Learning | Total Score |
|----------------|--------------------|--------------------|------------------|-------------|
| John Doe       | 5                  | 4                  | 4                | 13          |
| Jane Smith     | 4                  | 3                  | 5                | 12          |
| Alan Brown     | 3                  | 5                  | 4                | 12          |

**Requirements for Task 2:**  
- Use FastAPI or Flask.
- Accept extracted criteria as a list of strings.
- Support bulk upload of multiple resumes in PDF or DOCX formats.
- Extract text from each resume file.
- Match text against the provided ranking criteria.
- Assign scores based on the presence and relevance of each criterion (0-5 scale).
- Generate and return an Excel or CSV sheet with the candidate's name, individual scores for each criterion, and total scores.
- Implement Swagger UI with clear documentation for this endpoint.

---

### **Additional Deliverables:**
- **Swagger UI Documentation:** Each endpoint must be clearly documented using Swagger UI, including example inputs and expected outputs.
- **Video Demo:** Provide a short loop or unpublish youtube video (5-10 minutes) explaining your process, the architecture, key code sections, and how you built the solution, and a working demo in 5 mins
- **Public GitHub Repository:**  The solution must be submitted as a public GitHub project, including a well-structured README with setup instructions, usage details, and contribution guidelines.
---