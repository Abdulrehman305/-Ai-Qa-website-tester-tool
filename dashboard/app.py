from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess, os

app = FastAPI()
templates = Jinja2Templates(directory="dashboard/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "status": None})


@app.post("/run")
def run_script(request: Request, script_name: str = Form(...)):
    try:
        # Run your script (example: python scripts/my_script.py)
        result = subprocess.run(
            ["python", f"scripts/{script_name}.py"],
            capture_output=True,
            text=True
        )
        status = "Success" if result.returncode == 0 else "Error"
        output = result.stdout or result.stderr
    except Exception as e:
        status = "Error"
        output = str(e)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "status": status, "output": output}
    )
