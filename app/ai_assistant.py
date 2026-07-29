from flask import Blueprint, render_template, request, Response, stream_with_context, current_app
from app import db
from app.models import (BudgetTransaction, Task, Workout, Mood, CodingEntry,
                        CommunityPost, MotivationalQuote, Habit, HabitRecord)
import json

ai_bp = Blueprint('ai', __name__)


def _gather_context():
    lines = []

    transactions = BudgetTransaction.query.order_by(BudgetTransaction.date.desc()).limit(10).all()
    if transactions:
        lines.append("Recent budget transactions:")
        for t in transactions:
            lines.append(f"  - {t.title}: ${t.amount} ({t.type}) on {t.date.strftime('%Y-%m-%d')}")

    tasks = Task.query.order_by(Task.due_date.asc()).limit(10).all()
    if tasks:
        lines.append("Tasks:")
        for t in tasks:
            status = "done" if t.completed else "pending"
            lines.append(f"  - {t.title} (due {t.due_date.strftime('%Y-%m-%d')}, {status})")

    workouts = Workout.query.order_by(Workout.date.desc()).limit(5).all()
    if workouts:
        lines.append("Recent workouts:")
        for w in workouts:
            lines.append(f"  - {w.title}: {w.duration} mins on {w.date.strftime('%Y-%m-%d')}")

    moods = Mood.query.order_by(Mood.date.desc()).limit(5).all()
    if moods:
        lines.append("Recent mood entries:")
        for m in moods:
            lines.append(f"  - {m.title} on {m.date.strftime('%Y-%m-%d')}")

    entries = CodingEntry.query.order_by(CodingEntry.date_posted.desc()).limit(5).all()
    if entries:
        lines.append("Recent coding journal entries:")
        for e in entries:
            lines.append(f"  - {e.title} on {e.date_posted.strftime('%Y-%m-%d')}")

    posts = CommunityPost.query.order_by(CommunityPost.date_posted.desc()).limit(5).all()
    if posts:
        lines.append("Recent community posts:")
        for p in posts:
            lines.append(f"  - \"{p.title}\" by {p.author}")

    quotes = MotivationalQuote.query.order_by(MotivationalQuote.date_posted.desc()).limit(3).all()
    if quotes:
        lines.append("Recent motivational quotes:")
        for q in quotes:
            lines.append(f"  - \"{q.content}\" — {q.author}")

    habits = Habit.query.all()
    if habits:
        lines.append("Habits being tracked:")
        for h in habits:
            completed = sum(1 for r in h.records if r.status)
            lines.append(f"  - {h.name}: {completed}/{len(h.records)} days completed")

    return "\n".join(lines) if lines else "No data recorded yet across any module."


@ai_bp.route('/')
def index():
    return render_template('ai/index.html')


@ai_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
    if not messages:
        return Response('data: {"error": "No messages provided"}\n\n', mimetype='text/event-stream')

    api_key = current_app.config.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        def err():
            yield 'data: {"error": "ANTHROPIC_API_KEY not configured. Add it to your .env file."}\n\n'
        return Response(stream_with_context(err()), mimetype='text/event-stream')

    context_data = _gather_context()
    system_prompt = (
        "You are a helpful AI assistant embedded in Mega App, a personal productivity platform. "
        "You have access to the user's live data across all modules:\n\n"
        f"{context_data}\n\n"
        "Use this data to give personalised, actionable advice. Be concise and encouraging."
    )

    def generate():
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            with client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=4096,
                thinking={"type": "adaptive", "budget_tokens": 2000},
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    payload = json.dumps({"text": text})
                    yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            payload = json.dumps({"error": str(e)})
            yield f"data: {payload}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')
