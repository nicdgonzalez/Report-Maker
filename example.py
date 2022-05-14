from datetime import datetime
from report import Report

# The path to the file to output to.
file_path: str = './tmp/report.txt'

# Setting up a custom inventory (or leave blank to use the default):
inventory: dict = {
    '$': ['Candy Bar', 'Cookies', 'Gum'],
    '$$': ['Milk', 'Carrots', 'Coffee'],
    '$$$': ['Cat Food', 'Dog Food', 'Diapers']
}

inventory: dict = {}

# Create a Report object with an inventory and desired number of entries:
report: Report = Report(inventory, entries=50)

# Setup a custom format for the output file:
report.template = [
    'EXPENSE REPORT',
    '--------------',
    'NAME: {name}',
    '==============',
    '{report}',
    '--------------',
    'GENERATED ON: {datetime}'
]
# Setup a custom format for the entries:
report.item_fmt = '{price} = {item}'
# Align all of the separators:
report.auto_align = True

fmt: dict = {'name': 'Nicolas', 'datetime': datetime.now()}
# fmt: dict = {}
# Generate a report file:
report.generate_report(file_path, **fmt)

# Get the total cost as a string in dollar format ($0.00):
total_cost: str = report.calculate_total(file_path)
print(total_cost)
