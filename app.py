import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='.')

DB_PATH = 'archery.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.executescript('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,  -- bow, arrow, sight, etc.
            brand TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            location TEXT,
            weather TEXT,
            distance_m INTEGER,
            bow_id INTEGER,
            arrow_id INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (bow_id) REFERENCES equipment(id),
            FOREIGN KEY (arrow_id) REFERENCES equipment(id)
        );

        CREATE TABLE IF NOT EXISTS ends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            end_number INTEGER NOT NULL,
            arrows INTEGER NOT NULL DEFAULT 6,
            score INTEGER NOT NULL,
            grouping_cm REAL,
            notes TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS personal_bests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            value REAL NOT NULL,
            session_id INTEGER,
            achieved_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
    ''')
    
    # Seed sample data if empty
    c.execute("SELECT COUNT(*) FROM equipment")
    if c.fetchone()[0] == 0:
        c.executescript('''
            INSERT INTO equipment (name, type, brand, notes) VALUES
                ('Recurve Pro', 'bow', 'Hoyt', '68" 40lbs'),
                ('Carbon Express', 'arrow', 'Easton', '400 spine, 29"'),
                ('Compound Beast', 'bow', 'Mathews', '70lbs, 29" draw'),
                ('X10 Arrows', 'arrow', 'Easton', '27" 700 spine');

            INSERT INTO sessions (date, location, weather, distance_m, bow_id, arrow_id, notes) VALUES
                ('2024-03-01', 'Outdoor Range A', 'Sunny, 5mph wind', 18, 1, 2, 'Good session'),
                ('2024-03-08', 'Indoor Club', 'Indoor', 18, 1, 2, 'Personal best day'),
                ('2024-03-15', 'Outdoor Range A', 'Cloudy', 30, 3, 4, 'Tried longer distance');

            INSERT INTO ends (session_id, end_number, arrows, score, grouping_cm, notes) VALUES
                (1, 1, 6, 52, 8.5, 'Warm up'),
                (1, 2, 6, 55, 7.2, null),
                (1, 3, 6, 57, 6.8, 'Finding rhythm'),
                (1, 4, 6, 58, 6.1, null),
                (2, 1, 6, 56, 6.5, null),
                (2, 2, 6, 59, 5.8, null),
                (2, 3, 6, 60, 4.9, 'Perfect end!'),
                (2, 4, 6, 58, 5.5, null),
                (3, 1, 6, 48, 12.3, 'Adjusting for distance'),
                (3, 2, 6, 51, 10.8, null),
                (3, 3, 6, 54, 9.5, null);
        ''')
    
    conn.commit()
    conn.close()

# ── SESSIONS ──────────────────────────────────────────────────────────────────

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    conn = get_db()
    rows = conn.execute('''
        SELECT s.*, 
               b.name as bow_name, a.name as arrow_name,
               COUNT(e.id) as end_count,
               COALESCE(SUM(e.score), 0) as total_score,
               COALESCE(AVG(e.grouping_cm), 0) as avg_grouping
        FROM sessions s
        LEFT JOIN equipment b ON s.bow_id = b.id
        LEFT JOIN equipment a ON s.arrow_id = a.id
        LEFT JOIN ends e ON s.id = e.session_id
        GROUP BY s.id
        ORDER BY s.date DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/sessions', methods=['POST'])
def add_session():
    d = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO sessions (date, location, weather, distance_m, bow_id, arrow_id, notes)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (d['date'], d.get('location'), d.get('weather'),
               d.get('distance_m'), d.get('bow_id'), d.get('arrow_id'), d.get('notes')))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': session_id}), 201

@app.route('/api/sessions/<int:sid>', methods=['DELETE'])
def delete_session(sid):
    conn = get_db()
    conn.execute('DELETE FROM sessions WHERE id=?', (sid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── ENDS ──────────────────────────────────────────────────────────────────────

@app.route('/api/sessions/<int:sid>/ends', methods=['GET'])
def get_ends(sid):
    conn = get_db()
    rows = conn.execute('SELECT * FROM ends WHERE session_id=? ORDER BY end_number', (sid,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/sessions/<int:sid>/ends', methods=['POST'])
def add_end(sid):
    d = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COALESCE(MAX(end_number),0)+1 FROM ends WHERE session_id=?', (sid,))
    end_num = c.fetchone()[0]
    c.execute('''INSERT INTO ends (session_id, end_number, arrows, score, grouping_cm, notes)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (sid, end_num, d.get('arrows', 6), d['score'], d.get('grouping_cm'), d.get('notes')))
    conn.commit()
    conn.close()
    return jsonify({'ok': True}), 201

@app.route('/api/ends/<int:eid>', methods=['DELETE'])
def delete_end(eid):
    conn = get_db()
    conn.execute('DELETE FROM ends WHERE id=?', (eid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── EQUIPMENT ─────────────────────────────────────────────────────────────────

@app.route('/api/equipment', methods=['GET'])
def get_equipment():
    conn = get_db()
    rows = conn.execute('SELECT * FROM equipment ORDER BY type, name').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/equipment', methods=['POST'])
def add_equipment():
    d = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO equipment (name, type, brand, notes) VALUES (?, ?, ?, ?)',
              (d['name'], d['type'], d.get('brand'), d.get('notes')))
    conn.commit()
    conn.close()
    return jsonify({'ok': True}), 201

@app.route('/api/equipment/<int:eid>', methods=['DELETE'])
def delete_equipment(eid):
    conn = get_db()
    conn.execute('DELETE FROM equipment WHERE id=?', (eid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

# ── STATS ─────────────────────────────────────────────────────────────────────

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    
    # Overall stats
    totals = conn.execute('''
        SELECT 
            COUNT(DISTINCT s.id) as total_sessions,
            COUNT(e.id) as total_ends,
            COALESCE(SUM(e.score), 0) as total_score,
            COALESCE(MAX(e.score), 0) as best_end,
            COALESCE(AVG(e.score), 0) as avg_end_score,
            COALESCE(MIN(e.grouping_cm), 0) as best_grouping,
            COALESCE(AVG(e.grouping_cm), 0) as avg_grouping
        FROM sessions s LEFT JOIN ends e ON s.id = e.session_id
    ''').fetchone()
    
    # Session totals for chart
    sessions_chart = conn.execute('''
        SELECT s.date, s.location,
               COALESCE(SUM(e.score), 0) as total,
               COALESCE(AVG(e.score), 0) as avg_end,
               COALESCE(AVG(e.grouping_cm), 0) as avg_group
        FROM sessions s LEFT JOIN ends e ON s.id = e.session_id
        GROUP BY s.id ORDER BY s.date ASC LIMIT 20
    ''').fetchall()

    # Best session
    best_session = conn.execute('''
        SELECT s.date, s.location, SUM(e.score) as total
        FROM sessions s JOIN ends e ON s.id = e.session_id
        GROUP BY s.id ORDER BY total DESC LIMIT 1
    ''').fetchone()

    conn.close()
    return jsonify({
        'totals': dict(totals),
        'sessions_chart': [dict(r) for r in sessions_chart],
        'best_session': dict(best_session) if best_session else None
    })

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    init_db()
    print("🏹 Archery Tracker running at http://localhost:5050")
    app.run(debug=True, port=5050)
