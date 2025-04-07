# 🧪 SaaS GUI Testing Tool v1.0 (Partially working)

This is a FastAPI + React-based web service that allows users to compare the visual styling of a live website against a Figma design. It helps QA Engineers, Designers, and Developers automatically detect styling mismatches in GUI elements.

---

## ✨ Features

- ✅ Compare live website CSS styles against Figma designs
- 🎯 Identify mismatches in font, color, spacing, and more
- 🎨 Accepts either CSS selectors or full-page scan
- 📄 Generates detailed HTML/JSON reports
- 🧾 Downloadable PDF reports with differences
- 🌍 CORS-enabled frontend/backend integration
- 💬 CLI & API logging with detailed debug messages

---

## 📁 Project Structure

```
SaaSGUITesting/
├── backend/
│   ├── comparison_engine.py      # Core logic for scraping and comparing
│   ├── element_comparator.py     # Style comparison rules
│   ├── logger.py                 # Logging setup
│   ├── report_generator.py       # PDF report generation
│   └── tests/
│       └── test_api.py           # Backend tests
├── frontend/
│   └── src/
│       └── TestRunner.jsx        # React component to run the test
├── logs/
│   └── guicomparator.log         # Log file for backend activity
├── .env                          # FIGMA_ACCESS_TOKEN here
└── main.py                       # Entry point for FastAPI backend
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/SaaSGUITesting.git
cd SaaSGUITesting
```

### 2. Install backend dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # (or source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

> ⚠️ Required: Playwright dependencies and Chromium browser
```bash
pip install playwright
playwright install
```

### 3. Set up `.env` with your Figma token

Create `.env` in the root folder:

```
FIGMA_ACCESS_TOKEN=your_figma_token_here
```

### 4. Start the FastAPI server

```bash
uvicorn main:app --reload
```

### 5. Start the frontend (React)

```bash
cd frontend
npm install
npm run dev
```

---

## 🌐 API Endpoints

| Method | Endpoint               | Description                    |
|--------|------------------------|--------------------------------|
| POST   | `/api/run-test`        | Run a visual test              |
| POST   | `/api/store-differences` | Store test results for PDF     |
| GET    | `/api/generate-pdf`   | Download the PDF report        |
| GET    | `/docs`               | Swagger UI for API testing     |

---

## 📅 Example Payload for `/api/run-test`

```json
{
  "website_url": "https://example.com",
  "figma_url": "https://www.figma.com/file/XXXXX/Project?node-id=123%3A456",
  "selectors": "#main-button, .navbar-logo"
}
```

---

## 📌 Notes

- The service extracts computed styles using Playwright.
- Figma API requires public file access and a valid token.
- For full comparison, element naming in Figma should reflect the website structure.

---

## 👨‍💼 Author

Developed by [@NicholasWhit3](https://github.com/NicholasWhit3)  
Need help? Feel free to open an issue or message me.

---

## 📄 License

MIT License
