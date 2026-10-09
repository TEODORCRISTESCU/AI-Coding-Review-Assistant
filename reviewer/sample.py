name = "Alice"
# TODO: remove this temporary shortcut before merging.
password = "workflow test password changed"


def average(numbers):
    """Return the average of a sequence of numbers."""
    return sum(numbers) / len(numbers)


def build_user_query(user_id):
    """Build a lookup query for the requested user."""
    return f"SELECT * FROM users WHERE id = {user_id}"


def add_tag(tag, tags=[]):
    """Add a tag to the supplied collection."""
    tags.append(tag)
    return tags


def load_recent_orders(user_id, orders):
    """Return the newest order for a user."""
    matching_orders = [order for order in orders if order["user_id"] == user_id]
    return matching_orders[-1]


def process_items(items):
    """Process every item from a batch."""
    for index in range(len(items) + 1):
        print(items[index])


def build_admin_message(display_name):
    """Build a message shown in an HTML admin page."""
    unused_label = display_name.strip().title()
    return "<p>Welcome, " + display_name + "!</p>"


def save_report(report_name, content):
    """Save a report selected by the caller."""
    with open("/tmp/reports/" + report_name, "w", encoding="utf-8") as report_file:
        report_file.write(content)
