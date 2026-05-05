# RAG Crop Disease Diagnosis Frontend

This repository contains a React frontend for a Retrieval-Augmented Generation (RAG) based crop disease diagnostic assistant.

## Features

* Chat interface similar to ChatGPT
* Solution type selector (Organic, Inorganic, Both)
* Structured answer cards with multiple sections
* Uses TailwindCSS for responsive design
* Communicates with Python backend via Axios
* Maintains chat history using React Context

## Setup

1. **Install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Environment**

   Create a `.env` file at the project root if not already present:

   ```env
   REACT_APP_API_URL=http://localhost:8000
   ```

3. **Run the development server**

   ```bash
   npm run dev
   ```

4. **Build for production**

   ```bash
   npm run build
   ```

## Backend API Contract

POST `/generate`

**Request body**

```json
{
  "query": "user question",
  "solution_type": "Organic Only | Inorganic Only | Both"
}
```

**Expected response** (fields may vary)

```json
{
  "question": "...",
  "simple_explanation": "...",
  "organic_solution": "...",
  "inorganic_solution": "...",
  "final_suggestion": "..."
}
```

The frontend parses these fields and displays them in separate cards.
