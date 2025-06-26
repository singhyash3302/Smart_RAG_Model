# 🧠 Smart RAG PDF Question Answering System

**Smart_RAG_Model** is an intelligent PDF-based question-answering application that combines **AI**, **Vector Search**, **Wikipedia Search**, and **Web Search via SerpAPI** to provide accurate and contextually relevant answers.

Built with **Streamlit (frontend)** and **FastAPI (backend)**, this app lets you upload PDFs and query their content while also supporting real-time factual questions from the web.

---

## 🚀 Features

### 📄 PDF Upload + Vector Store
- Upload one or more PDFs.
- Text is automatically extracted, chunked, and stored in a **FAISS vector database**.
- Uses **HuggingFace embeddings** for similarity search.

### 🧠 Dual Modes of Answering

#### 1. **AI + RAG Mode**
- Combines Groq’s LLM (LLaMA 3.1) with context from the vector store.
- Designed for deep answers grounded in your uploaded PDFs.

#### 2. **Smart Routing Mode**
Your question is routed to the most appropriate response path:

| Route           | Description |
|----------------|-------------|
| `ai_response`   | Friendly or general-purpose answers. |
| `vectorstore`   | Questions about your uploaded documents. |
| `wiki_search`   | Looks up verified data from Wikipedia. |
| `web_search`    | Fetches fresh information using SerpAPI (e.g., breaking news). |

---

## 📦 Installation

### 1. Clone the Repo

```bash
git clone https://github.com/singhyash3302/Smart_RAG_Model.git
cd Smart_RAG_Model
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

Create a `.env` file in the root directory and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key
SERPAPI_API_KEY=your_serpapi_key
```

Or export them manually in the terminal:

```bash
export GROQ_API_KEY=your_groq_api_key
export SERPAPI_API_KEY=your_serpapi_key
```


## Running the Application

### 1. Start the FastAPI Backend

The backend handles AI and RAG-based responses, and Wikipedia queries.

```bash
uvicorn fastapi_app:app --reload
```

This will start the FastAPI server locally at `http://127.0.0.1:8000/`.

### 2. Start the Streamlit Frontend

The frontend is a simple web interface to upload PDFs and submit queries.

```bash
streamlit run Home.py
```

Access the frontend at `http://localhost:8501/`.

## Usage

1. **Upload PDFs**: You can upload multiple PDF files using the interface on the home page.
2. **Ask Questions**: Once the PDFs are processed, you can ask questions about the content.
3. **Choose a Response Mode**:
   - **AI + RAG Response**: Uses a combination of AI and a vector store of the uploaded PDFs to provide a contextual answer.
   - **Smart AI Agent**: Routes the query to either AI, AI + RAG, or Wikipedia, based on the context of the query.

### Backend Routes

The backend supports the following API routes:

1. **AI Answer**:
   - **Endpoint**: `/AI_Answer/`
   - **Method**: POST
   - **Payload**:
     ```json
     {
       "query": "Your query",
       "context": "PDF content or other text"
     }
     ```
   - **Description**: Provides a direct AI-generated answer based on the query and the PDF context.

2. **Smart AI Agent**:
   - **Endpoint**: `/Smart_AI_Answer/`
   - **Method**: POST
   - **Payload**:
     ```json
     {
       "query": "Your query",
       "context": "PDF content or other text"
     }
     ```
   - **Description**: Routes the query to either an AI response, AI + RAG response, or Wikipedia search depending on the context.
