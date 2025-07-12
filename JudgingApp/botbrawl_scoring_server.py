from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
socketio = SocketIO(app)  # <-- Use SocketIO

NUM_JUDGES = 3  # Change this if you want a different number of judges

judges_data = [
    {"dmg": None, "agg": None, "ctrl": None} for _ in range(NUM_JUDGES)
]

DAMAGE_CHOICES = ["8-0", "7-1", "6-2", "5-3", "4-4", "3-5", "2-6", "1-7", "0-8"]
AGGRESSION_CHOICES = ["5-0", "4-1", "3-2", "2-3", "1-4", "0-5"]
CONTROL_CHOICES = ["6-0", "5-1", "4-2", "3-3", "2-4", "1-5", "0-6"]

OUTPUT_FILE = "botbrawl_scores.json"

def parse_score(score_str):
    a, b = map(int, score_str.split('-'))
    return a, b

def calculate_winner():
    red_wins = 0
    white_wins = 0
    for judge in judges_data:
        if None in judge.values():
            continue
        dmg_a, dmg_b = parse_score(judge["dmg"])
        agg_a, agg_b = parse_score(judge["agg"])
        ctrl_a, ctrl_b = parse_score(judge["ctrl"])

        total_a = dmg_a + agg_a + ctrl_a
        total_b = dmg_b + agg_b + ctrl_b

        if total_a > total_b:
            red_wins += 1
        elif total_b > total_a:
            white_wins += 1

    if red_wins > white_wins:
        return "Red Square"
    elif white_wins > red_wins:
        return "White Square"
    else:
        return "Tie"

def save_scores():
    data = {
        "judges": [],
        "winner": calculate_winner()
    }
    for idx, judge in enumerate(judges_data, start=1):
        if None in judge.values():
            total_red = total_white = None
        else:
            dmg_a, dmg_b = parse_score(judge["dmg"])
            agg_a, agg_b = parse_score(judge["agg"])
            ctrl_a, ctrl_b = parse_score(judge["ctrl"])
            total_red = dmg_a + agg_a + ctrl_a
            total_white = dmg_b + agg_b + ctrl_b

        judge_summary = {
            "judge": idx,
            "damage": judge["dmg"],
            "aggression": judge["agg"],
            "control": judge["ctrl"],
            "total_red": total_red,
            "total_white": total_white,
        }
        data["judges"].append(judge_summary)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    winner = calculate_winner()
    # Send all judge data to template
    judges_with_totals = []
    for judge in judges_data:
        if None in judge.values():
            total_red = total_white = None
        else:
            dmg_a, dmg_b = parse_score(judge["dmg"])
            agg_a, agg_b = parse_score(judge["agg"])
            ctrl_a, ctrl_b = parse_score(judge["ctrl"])
            total_red = dmg_a + agg_a + ctrl_a
            total_white = dmg_b + agg_b + ctrl_b
        judges_with_totals.append({
            **judge,
            "total_red": total_red if 'total_red' in locals() else None,
            "total_white": total_white if 'total_white' in locals() else None,
        })
    return render_template(
        "overview.html",
        judges=judges_with_totals,
        winner=winner
    )

@app.route("/judge/<int:judge_id>", methods=["GET", "POST"])
def judge(judge_id):
    if not (1 <= judge_id <= NUM_JUDGES):
        return "Invalid judge ID", 404

    judge_idx = judge_id - 1

    if request.method == "POST":
        judges_data[judge_idx]["dmg"] = request.form["dmg"]
        judges_data[judge_idx]["agg"] = request.form["agg"]
        judges_data[judge_idx]["ctrl"] = request.form["ctrl"]
        save_scores()
        # Emit update to all connected clients
        socketio.emit('update_overview')
        return redirect(url_for("judge", judge_id=judge_id))

    # The GET request should render the template, so this must be indented inside the function
    return render_template(
        "judge.html",
        judge_number=judge_id,
        damage_choices=DAMAGE_CHOICES,
        aggression_choices=AGGRESSION_CHOICES,
        control_choices=CONTROL_CHOICES,
        judge=judges_data[judge_idx]  # <--- Pass as 'judge'
    )

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")