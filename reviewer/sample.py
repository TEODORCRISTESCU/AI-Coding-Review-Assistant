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
