"""Azure Data Analytics Pipeline & Interactive SQL Workbench Web Application."""
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from pipeline.etl import calculate_analytics_summary, execute_sql_query, load_raw_data, DATA_PATH

app = FastAPI(
    title="Azure Data Analytics & BI Pipeline",
    description="Enterprise Cloud Data Lakehouse ETL, Aggregations & Interactive SQL Workbench",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

class QueryRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render executive BI dashboard."""
    analytics = calculate_analytics_summary()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "analytics": analytics
    })

@app.get("/api/analytics")
async def get_analytics():
    """Retrieve summarized BI metrics."""
    return calculate_analytics_summary()

@app.post("/api/query")
async def run_query(payload: QueryRequest):
    """Execute SQL query in the analytics lakehouse."""
    result = execute_sql_query(payload.query)
    return result

@app.get("/api/export")
async def export_csv():
    """Export dataset as CSV."""
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=azure_sales_dataset.csv"})
    return JSONResponse({"error": "Dataset not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
