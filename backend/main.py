from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import sqlite3
import os

# Set database path in the backend folder
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BACKEND_DIR, "coffees.db")
FRONTEND_DIR = os.path.dirname(BACKEND_DIR)

# Seed data helper
def seed_db(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM coffees")
    default_coffees = [
        ("Espresso", "A concentrated, bold shot of coffee brewed under high pressure. Intense flavor with a rich crema.", "Bold & Strong", "images/espresso.png", 12),
        ("Cappuccino", "Equal parts espresso, steamed milk, and thick milk foam. Perfectly balanced coffee taste with a creamy texture.", "Creamy & Balanced", "images/cappuccino.png", 8),
        ("Latte", "A smooth blend of espresso and steamed milk, topped with a thin layer of foam. Light, creamy, and soothing.", "Sweet & Smooth", "images/latte.png", 15),
        ("Cold Brew", "Coarsely ground coffee steeped in cold water for 12 to 24 hours. Smooth, naturally sweet, and low in acidity.", "Cold & Refreshing", "images/coldbrew.png", 10),
    ]
    cursor.executemany("""
        INSERT INTO coffees (name, description, category, image_path, votes)
        VALUES (?, ?, ?, ?, ?)
    """, default_coffees)
    conn.commit()

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coffees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            image_path TEXT NOT NULL,
            votes INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    
    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM coffees")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_db(conn)
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database and seed if empty
    init_db()
    yield

app = FastAPI(
    title="The Coffee Journal API",
    description="A FastAPI backend with SQLite to store coffee ratings and votes.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware to allow the frontend to access the API even if loaded via local file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic request body schema
class CoffeeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=10, max_length=200)
    category: str
    image_choice: str

# Map frontend image choices to local file paths
IMAGE_MAPPING = {
    "espresso": "images/espresso.png",
    "cappuccino": "images/cappuccino.png",
    "latte": "images/latte.png",
    "coldbrew": "images/coldbrew.png"
}

# --- API Endpoints ---

@app.get("/api/coffees")
def get_coffees():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, category, image_path, votes FROM coffees")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.post("/api/coffees/{id}/vote")
def vote_coffee(id: int):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if coffee exists
        cursor.execute("SELECT id FROM coffees WHERE id = ?", (id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee with ID {id} not found"
            )
            
        # Increment vote count
        cursor.execute("UPDATE coffees SET votes = votes + 1 WHERE id = ?", (id,))
        conn.commit()
        
        # Fetch and return updated record
        cursor.execute("SELECT id, name, description, category, image_path, votes FROM coffees WHERE id = ?", (id,))
        updated = cursor.fetchone()
        conn.close()
        return dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.post("/api/coffees", status_code=status.HTTP_201_CREATED)
def create_coffee(coffee: CoffeeCreate):
    image_path = IMAGE_MAPPING.get(coffee.image_choice.lower(), "images/espresso.png")
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check for case-insensitive duplicate names
        cursor.execute("SELECT id FROM coffees WHERE LOWER(name) = ?", (coffee.name.lower(),))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A coffee named '{coffee.name}' already exists."
            )
            
        cursor.execute("""
            INSERT INTO coffees (name, description, category, image_path, votes)
            VALUES (?, ?, ?, ?, 0)
        """, (coffee.name, coffee.description, coffee.category, image_path))
        conn.commit()
        
        new_id = cursor.lastrowid
        cursor.execute("SELECT id, name, description, category, image_path, votes FROM coffees WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row)
    except HTTPException:
        raise
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A coffee named '{coffee.name}' already exists."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.post("/api/coffees/reset")
def reset_coffees():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        seed_db(conn)
        conn.close()
        return {"message": "Database successfully reset to default seeds!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset database: {str(e)}"
        )

# --- Static Files Serving ---

# Serve the static images directory
images_dir = os.path.join(FRONTEND_DIR, "images")
if os.path.exists(images_dir):
    app.mount("/images", StaticFiles(directory=images_dir), name="images")

# Serve index.html, app.js, and styles.css directly at standard paths
@app.get("/")
def get_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/index.html")
def get_index_html():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/app.js")
def get_app_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "app.js"))

@app.get("/styles.css")
def get_styles_css():
    return FileResponse(os.path.join(FRONTEND_DIR, "styles.css"))
