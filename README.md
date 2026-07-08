# ArcTrack: Archery Performance Tracker

**ArcTrack** is a full-stack web application for archers to log training sessions, manage equipment, and visualize performance trends over time. The platform focuses on data-driven improvement by tracking shot accuracy and consistency across different environments and gear configurations.

<!-- TODO: add a screenshot — this is a visual project, show the charts!
![Dashboard](docs/screenshot_dashboard.png)
-->

## Core Features

- **Session Management** — log training dates, locations, weather conditions, and shooting distances.
- **End-by-End Logging** — record scores, arrow counts, and grouping measurements (cm) for every end within a session.
- **Equipment Tracking** — maintain a digital inventory of bows, arrows, and accessories to see how gear affects performance.
- **Performance Analytics** — automated total scores, average end scores, and shot-dispersion (grouping) trends.
- **Data Visualization** — real-time dashboard with custom canvas-based progression charts.

## Technical Stack

- **Backend:** Python / Flask with a RESTful JSON API
- **Database:** SQLite (4-table relational schema: `equipment`, `sessions`, `ends`, `personal_bests`)
- **Frontend:** HTML5, CSS3, vanilla JavaScript with custom canvas rendering

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/sessions` | List / create training sessions |
| DELETE | `/api/sessions/<id>` | Delete a session |
| GET/POST | `/api/sessions/<id>/ends` | List / log ends (auto-numbered) |
| DELETE | `/api/ends/<id>` | Delete an end |
| GET/POST | `/api/equipment` | List / add equipment |
| DELETE | `/api/equipment/<id>` | Remove equipment |
| GET | `/api/stats` | Aggregate stats + chart series |

## Getting Started

```bash
pip install -r requirements.txt
python app.py
# open http://localhost:5050
```

## Tests

```bash
pip install pytest
pytest
```

Tests run against a temporary database and cover the sessions, ends, equipment, and stats endpoints. CI runs them on every push via GitHub Actions.
