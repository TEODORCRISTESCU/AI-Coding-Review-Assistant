"""Illustrative review fixture; deliberately not executable application code.

The snippets are strings so this file cannot run the seeded issues. They are
intended to be copied into a demo PR for the portfolio walkthrough.
"""

SQL_CONCATENATION = """
query = "SELECT * FROM users WHERE email = '" + user_email + "'"
"""

HARDCODED_PASSWORD = """
demo_password = "portfolio-demo-password"
"""

OFF_BY_ONE = """
for index in range(len(items) + 1):
    process(items[index])
"""

UNUSED_VARIABLE = """
def build_label(item):
    unused_label = item.name.upper()
    return item.name
"""
