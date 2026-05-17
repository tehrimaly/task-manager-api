from flask import Flask, jsonify, request
from datetime import datetime
import uuid
import os

app = Flask(__name__)
tasks = {}


def create_task(title, description="", priority="medium"):
    """Create a new task with validation and error handling."""
    if not title or not isinstance(title, str):
        raise ValueError("Title must be a non-empty string.")
    if priority not in ("low", "medium", "high"):
        raise ValueError("Priority must be 'low', 'medium', or 'high'.")
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "title": title.strip(),
        "description": description.strip(),
        "priority": priority,
        "completed": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    tasks[task_id] = task
    return task


def get_task(task_id):
    """Retrieve a task by ID."""
    if not task_id:
        raise ValueError("Task ID cannot be empty.")
    task = tasks.get(task_id)
    if task is None:
        raise KeyError(f"Task '{task_id}' not found.")
    return task


def update_task(task_id, **kwargs):
    """Update allowed fields of an existing task."""
    task = get_task(task_id)
    allowed = {"title", "description", "priority", "completed"}
    for key, value in kwargs.items():
        if key not in allowed:
            raise ValueError(f"Field '{key}' cannot be updated.")
        if key == "priority" and value not in ("low", "medium", "high"):
            raise ValueError("Priority must be 'low', 'medium', or 'high'.")
        if key == "completed" and not isinstance(value, bool):
            raise TypeError("'completed' must be a boolean.")
        task[key] = value
    return task


def delete_task(task_id):
    """Delete a task by ID and return the deleted task."""
    task = get_task(task_id)
    del tasks[task_id]
    return task


def list_tasks(filter_completed=None, priority=None):
    """List all tasks with optional filters."""
    result = list(tasks.values())
    if filter_completed is not None:
        result = [t for t in result if t["completed"] == filter_completed]
    if priority is not None:
        result = [t for t in result if t["priority"] == priority]
    return result


@app.route("/tasks", methods=["GET"])
def api_list_tasks():
    completed = request.args.get("completed")
    priority = request.args.get("priority")
    if completed is not None:
        completed = completed.lower() == "true"
    return jsonify(list_tasks(filter_completed=completed, priority=priority))


@app.route("/tasks", methods=["POST"])
def api_create_task():
    data = request.get_json(silent=True) or {}
    try:
        task = create_task(
            data.get("title", ""),
            data.get("description", ""),
            data.get("priority", "medium"),
        )
        return jsonify(task), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/tasks/<task_id>", methods=["GET"])
def api_get_task(task_id):
    try:
        return jsonify(get_task(task_id))
    except KeyError as e:
        return jsonify({"error": str(e)}), 404


@app.route("/tasks/<task_id>", methods=["PUT"])
def api_update_task(task_id):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(update_task(task_id, **data))
    except KeyError as e:
        return jsonify({"error": str(e)}), 404
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/tasks/<task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    try:
        return jsonify(delete_task(task_id))
    except KeyError as e:
        return jsonify({"error": str(e)}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
