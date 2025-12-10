Below is a **clean, structured, production-ready Markdown (.md) file** for your *BankGPT: Conversation-Driven Loan Processor* documentation.
You can **copy–paste directly into a `.md` file** (e.g., `README.md`).

---

# **BankGPT: Conversation-Driven Loan Processor**

**Version 2.0 | Developed by BankGPT Team**

BankGPT is a next-generation AI-powered personal loan processor that replaces static forms with a dynamic, conversational, multi-agent system. Instead of overwhelming users with long forms, BankGPT guides applicants through an intuitive chat workflow, performing verification, underwriting, fraud checks, and sanctioning in real time.

---

# **✨ Key Features**

### **1. Conversational Interface**

* Users interact naturally through chat instead of forms.
* Dynamic prompts appear only when needed (e.g., salary slip upload for high amounts).

### **2. Multi-Agent Orchestration**

A Master Agent coordinates the workflow across:

* **Verification Agent**
* **Underwriting Agent**
* **Fraud Agent**
* **Sanction Agent**

### **3. Smart Eligibility Routing**

Automatically decides the journey:

* **FAST_TRACK** → Instant approval
* **CONDITIONAL_REVIEW** → Requires additional documents
* **HARD_REJECTION** → Stops with clear explanation

### **4. Real-Time XAI Panel**

A transparency sidebar displays:

* Credit score insights
* Underwriting reasoning
* Fraud check explanations
* Agent-level status updates

### **5. Auto-Sanctioning**

At approval, BankGPT generates:

* **PDF Sanction Letter** (auto-download)

### **6. State Machine Architecture**

Conversation-driven workflow instead of linear forms.

---

# **🏗 Architecture Overview**

```
User <--> Streamlit UI <--> Master Agent

Orchestration Layer:
    Phase 1: Sales
    Phase 2: Underwriting
    Phase 3: Conditional Review
    Phase 4: Sanction

Worker Agents:
    Verification Agent
    Underwriting Agent
    Fraud Agent
    Sanction Agent

Verification Agent <--> Mock CRM (JSON)
Sanction Agent --> PDF Generator
```

---

# **🔄 4-Phase Workflow**

### **Phase 1: Sales**

* Friendly onboarding
* Product pitch + fixed interest rate (11%)

### **Phase 2: Underwriting**

**Two-step verification:**

1. **Identity** → Lookup via mock CRM
2. **Eligibility** → Compare request vs. pre-approved limit

### **Phase 3: Conditional Review**

Triggered if:

* Requested amount > pre-approved limit
* Score is decent (≥700)

Prompts:

* Salary slip upload
* Fraud scan

### **Phase 4: Sanction**

* Approval
* Auto-generated PDF sanction letter

---

# **🚀 Quick Start**

### **1. Clone & Setup**

```bash
git clone <repo_url>
cd loan_rag_streamlit
python -m venv venv
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

**Note:** For Voice & OCR
Install **FFmpeg** and **Tesseract** on system path.

### **3. Run the Application**

```bash
streamlit run app.py
```

### **4. Run Tests**

```bash
python test_conversation_flow.py
```

---

# **📂 Project Structure**

```
loan_rag_streamlit/
├── app.py                     # Streamlit UI
├── master_agent.py            # Phase orchestration
├── session_manager.py         # Chat state persistence
├── agents.py                  # Verification, Fraud, Underwriting, Sanction agents
├── eligibility.py             # Fast-track / Hard-reject logic
├── test_conversation_flow.py  # Unit tests
├── data/
│   └── mock_db.json           # CRM mock database
├── outputs/                   # Generated sanction letters
└── requirements.txt
```

---

# **🧪 Demo Test Cases**

Mock CRM (excerpt from `data/mock_db.json`):

```json
{
  "9876543210": {
    "name": "Amit Kumar",
    "credit_score": 780,
    "income": 65000,
    "blacklisted": false,
    "approved_amount": 1200000
  },
  "9998887776": {
    "name": "Neha Singh",
    "credit_score": 710,
    "income": 48000,
    "blacklisted": false,
    "approved_amount": 800000
  },
  "8887776665": {
    "name": "Ravi Sharma",
    "credit_score": 640,
    "income": 40000,
    "blacklisted": true,
    "approved_amount": 0
  }
}
```

---

# **📘 Test Case Summaries**

## **Test Case 1 — Fast Track Approval ✅**

**Applicant:** Amit Kumar
**Loan Request:** ₹500,000 (<= ₹1.2M)
**Score:** 780

* Verification: Pass
* Underwriting: Pass @ 10.5%
* Fraud: Clear
* Route: **FAST_TRACK**
* **Approved**
* Sanction PDF generated

---

## **Test Case 2 — Conditional Review ⚠️**

**Applicant:** Neha Singh
**Loan Request:** ₹1,200,000 (> ₹800k limit but < 2×)
**Score:** 710

Flow:

* Conditional Review → Salary slip upload
* Fraud scan → Pass
* Approved → PDF generated

---

## **Test Case 3 — Hard Rejection (Blacklisted) ❌**

**Applicant:** Ravi Sharma
**Score:** 640
**Blacklisted:** Yes

* Underwriting: Fail
* Fraud: Fail
* Route: **HARD_REJECTION**
* **Rejected** with XAI explanation

---

## **Test Case 4 — Hard Rejection (Low Credit Score) ❌**

**Score:** 590 (<650)

* Immediate rejection
* Clear XAI reasoning

---

## **Test Case 5 — Not Found in CRM → Manual Review 🔍**

Unknown applicant

* Verification: Not found
* Route: Rejected → **Manual Review**

---

## **Test Case 6 — EMI & FOIR Calculator**

Input:

* Loan: ₹1,000,000
* Tenure: 10 yrs
* Rate: 11%
* Income: ₹100,000
* Existing EMI: ₹10,000

Output:

* **EMI:** ~₹13,218
* **FOIR:** 23.2%
* Band: **Likely Eligible**

---

## **Test Case 7 — Voice Input (Optional)**

Process:

1. Click microphone
2. Speak query
3. Auto-transcribed
4. Answered with RAG/Gemini

---

## **Test Case 8 — OCR from Document (Optional)**

* Upload PNG/JPG
* OCR extracts text
* Auto-filled into conversation

---

# **📊 Eligibility Routing Summary**

| Amount | Limit | Score | Route          | Result                |
| ------ | ----- | ----- | -------------- | --------------------- |
| 500k   | 1M    | 780   | FAST_TRACK     | Approved              |
| 900k   | 500k  | 680   | CONDITIONAL    | Conditional           |
| 1.2M   | 500k  | 750   | CONDITIONAL    | Conditional           |
| 1.5M   | 500k  | 680   | HARD_REJECTION | Rejected              |
| 500k   | 500k  | 600   | HARD_REJECTION | Rejected              |
| 500k   | 0     | 680   | HARD_REJECTION | Rejected (Not in CRM) |

---

# **🖥 Expected UI Flow**

```
Enter Applicant Info
      ↓
Click "Process Loan Application"
      ↓
Multi-Agent Pipeline:
    - Verification
    - Underwriting
    - Fraud Detection
    - Eligibility Routing
      ↓
FAST_TRACK  → Instant Approval → PDF
CONDITIONAL → Salary Slip Upload → Approval/Rejection
```

---

# **✔ Success Criteria**

* Correct sales pitch
* Accurate routing (Fast/Conditional/Reject)
* Document upload appears only when needed
* XAI panel shows detailed reasoning
* Sanction PDFs generate properly

---


