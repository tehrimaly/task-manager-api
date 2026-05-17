import pytest
from app import app, tasks, create_task, get_task, update_task, delete_task, list_tasks

@pytest.fixture(autouse=True)
def clear_tasks():
    tasks.clear()
    yield
    tasks.clear()

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

# create_task tests
def test_create_normal():
    task = create_task("Buy groceries", "Milk and eggs", "high")
    assert task["title"] == "Buy groceries"
    assert task["priority"] == "high"
    assert task["completed"] is False

def test_create_default_priority():
    task = create_task("Simple task")
    assert task["priority"] == "medium"

def test_create_strips_whitespace():
    task = create_task("  Clean room  ")
    assert task["title"] == "Clean room"

def test_create_empty_title_raises():
    with pytest.raises(ValueError):
        create_task("")

def test_create_invalid_priority_raises():
    with pytest.raises(ValueError):
        create_task("Task", priority="urgent")

# get_task tests
def test_get_normal():
    task = create_task("Read book")
    fetched = get_task(task["id"])
    assert fetched["title"] == "Read book"

def test_get_nonexistent_raises():
    with pytest.raises(KeyError):
        get_task("fake-id")

def test_get_empty_id_raises():
    with pytest.raises(ValueError):
        get_task("")

# update_task tests
def test_update_title():
    task = create_task("Old title")
    updated = update_task(task["id"], title="New title")
    assert updated["title"] == "New title"

def test_update_completed():
    task = create_task("Exercise")
    updated = update_task(task["id"], completed=True)
    assert updated["completed"] is True

def test_update_invalid_field_raises():
    task = create_task("Sleep")
    with pytest.raises(ValueError):
        update_task(task["id"], created_at="2024-01-01")

def test_update_invalid_priority_raises():
    task = create_task("Walk")
    with pytest.raises(ValueError):
        update_task(task["id"], priority="critical")

def test_update_completed_non_bool_raises():
    task = create_task("Study")
    with pytest.raises(TypeError):
        update_task(task["id"], completed="yes")

# delete_task tests
def test_delete_normal():
    task = create_task("Temp task")
    deleted = delete_task(task["id"])
    assert deleted["title"] == "Temp task"
    assert task["id"] not in tasks

def test_delete_nonexistent_raises():
    with pytest.raises(KeyError):
        delete_task("fake-id")

def test_double_delete_raises():
    task = create_task("Once")
    delete_task(task["id"])
    with pytest.raises(KeyError):
        delete_task(task["id"])

# list_tasks tests
def test_list_empty():
    assert list_tasks() == []

def test_list_all():
    create_task("A")
    create_task("B")
    assert len(list_tasks()) == 2

def test_list_filter_completed():
    t1 = create_task("Done")
    create_task("Pending")
    update_task(t1["id"], completed=True)
    result = list_tasks(filter_completed=True)
    assert len(result) == 1

def test_list_filter_priority():
    create_task("High one", priority="high")
    create_task("Low one", priority="low")
    result = list_tasks(priority="high")
    assert len(result) == 1

def test_list_no_match_returns_empty():
    create_task("Medium task")
    assert list_tasks(priority="high") == []