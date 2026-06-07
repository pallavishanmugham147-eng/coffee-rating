# ☕ The Coffee Journal

A full-stack Coffee Rating Application where users can browse, vote for, and add their favorite coffee drinks. Vote counts are persisted in a SQLite database via a FastAPI backend.

![Coffee Journal](images/espresso.png)

---

## 🌟 Features

- 📋 **Browse Coffees** — View a curated catalog of coffee drinks with descriptions and categories
- ❤️ **Vote System** — Click the heart button to vote for your favorite brew; votes persist in a real database
- ➕ **Add New Brews** — Suggest new coffee drinks via a modal form with category and image selection
- 🔍 **Search & Filter** — Search by name/description and filter by category (Bold, Creamy, Sweet, Cold)
- 📊 **Live Stats Bar** — Shows total brews cataloged, total votes cast, and the current top-voted brew
- 🔄 **Reset Database** — Restore the original default seed coffees and vote tallies
- 🏆 **Leaderboard Ranking** — Cards are ranked by votes with `#1`, `#2`, `#3` badges
- 🍞 **Toast Notifications** — Friendly feedback toasts for votes, additions, and errors

---

## 🛠️ Tech Stack

| Layer      | Technology          |
|------------|---------------------|
| Frontend   | HTML5, Vanilla CSS, JavaScript (ES6+) |
| Icons      | [Lucide Icons](https://lucide.dev/) |
| Fonts      | Google Fonts (Outfit, Playfair Display) |
| Backend    | Python 3 + [FastAPI](https://fastapi.tiangolo.com/) |
| Database   | SQLite (via Python `sqlite3` standard library) |
| Server     | [Uvicorn](https://www.uvicorn.org/) ASGI server |

---

## 📁 Project Structure

```
coffee-rating/
├── index.html          # Frontend HTML structure
├── styles.css          # All styling (dark glassmorphism theme)
├── app.js              # Frontend application logic (fetch, render, vote)
├── images/             # Coffee drink images
│   ├── espresso.png
│   ├── cappuccino.png
│   ├── latte.png
│   └── coldbrew.png
├── backend/
│   ├── main.py         # FastAPI application, API routes, SQLite logic
│   ├── start_backend.py # Server launcher script (Uvicorn)
│   └── verify_api.py   # Automated API test suite
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- `fastapi` and `uvicorn` installed:

```bash
pip install fastapi uvicorn
```

### Run the Backend

```bash
python backend/start_backend.py
```

The server will start at:
- **API:** `http://127.0.0.1:8000/api`
- **Frontend:** `http://127.0.0.1:8000/`

### Open the App

Navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🔌 API Endpoints

| Method | Endpoint                    | Description                          |
|--------|-----------------------------|--------------------------------------|
| GET    | `/api/coffees`              | Fetch all coffees from the database  |
| POST   | `/api/coffees`              | Add a new coffee drink               |
| POST   | `/api/coffees/{id}/vote`    | Increment vote count for a coffee    |
| POST   | `/api/coffees/reset`        | Reset database to default seed data  |

### Example: Vote for a Coffee

```bash
curl -X POST http://127.0.0.1:8000/api/coffees/1/vote
```

### Example: Add a New Coffee

```bash
curl -X POST http://127.0.0.1:8000/api/coffees \
  -H "Content-Type: application/json" \
  -d '{"name": "Cortado", "description": "Equal parts espresso and warm milk.", "category": "Bold & Strong", "image_choice": "espresso"}'
```

---

## 🧪 Running API Tests

With the backend running, execute the automated test suite:

```bash
python backend/verify_api.py
```

This verifies all 6 API behaviors: listing, voting, adding, duplicate rejection, list size, and database reset.

---

## 🎨 Default Coffees

| Name       | Category           | Initial Votes |
|------------|--------------------|---------------|
| Latte      | Sweet & Smooth     | 15            |
| Espresso   | Bold & Strong      | 12            |
| Cold Brew  | Cold & Refreshing  | 10            |
| Cappuccino | Creamy & Balanced  | 8             |

---

## 📸 Screenshots

> Start the server and visit `http://127.0.0.1:8000/` to see the full experience.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
