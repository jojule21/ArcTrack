ArcTrack: Archery Performance Tracker

**ArcTrack** is a full-stack web application designed for archers to log training sessions, manage equipment, and visualize performance trends over time. The platform focuses on data-driven improvement by tracking shot accuracy and consistency across different environments and gear configurations. 

---

Core Features

* **Session Management**: Log training dates, locations, weather conditions, and shooting distances. 
* **End-by-End Logging**: Record scores, arrow counts, and grouping measurements (in cm) for every "end" within a session.
* **Equipment Tracking**: Maintain a digital inventory of bows, arrows, and accessories to see how specific gear affects your performance.
* **Performance Analytics**: Automated calculation of total scores, average end scores, and shot dispersion (grouping) trends.
* **Data Visualization**: Real-time dashboard featuring progression charts for scores and grouping consistency using custom canvas-based rendering.

---

## Technical Stack

* **Frontend**: HTML5, CSS3 (Custom "Cinzel" Dark Theme), and Vanilla JavaScript.
* **Backend**: Python with the Flask web framework.
* **Database**: SQLite for persistent storage of sessions, equipment, and performance data.
* **API**: RESTful JSON endpoints for seamless communication between the frontend and the database.

---

## Database Schema

The system utilizes a relational SQLite database with the following structure:

| Table | Description |
| :--- | :--- |
| **`equipment`** | Stores gear details like name, type (bow/arrow), brand, and technical notes. |
| **`sessions`** | Tracks high-level training data including date, location, and equipment used. |
| **`ends`** | Contains individual round data: scores, arrow counts, and grouping metrics. |
| **`personal_bests`** | Automatically logs record-breaking achievements in various categories. |

---

## Getting Started

1.  **Install Dependencies**:
    ```bash
    pip install flask
    ```
2.  **Run the Application**:
    ```bash
    python app.py
    ```
3.  **Access the Tracker**:
    Navigate to `http://localhost:5050` in your web browser.

---

## Development Note 
This project is currently in active development, focusing on enhancing the **grouping and scatter analysis** engine to provide deeper insights into shot consistency trends across multiple training sessions. 
