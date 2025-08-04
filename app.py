from flask import Flask, render_template, request, redirect, url_for
import os
import boto3

# You will likely need a database e.g. DynamoDB so you might either boto3 or pynamodb
# Additional installs here:
#
#
#


app = Flask(__name__)

## Instantiate your database here:
#
#
#
def create_test_client():
    return app.test_client()

@app.route("/index")
def index():
    return 'hello world'

@app.route("/")
def home():
    # Complete the code below
    # The todo_list variable should be returned by running a scan on your DDB table,
    # which is then converted to a list

    # Create DynamoDB resource
    db = boto3.resource('dynamodb', region_name='ap-southeast-1')
    
    # Find table
    table = db.Table('todo-list-table')

    # Read all items from the table
    response = table.scan()

    # Convert into a list
    todo_list = response.get('Items', [])

    return render_template("base.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")

    # Create DynamoDB resource
    db = boto3.resource('dynamodb', region_name='ap-southeast-1')
    
    # Find table
    table = db.Table('todo-list-table')

    # To find the next taskId, we will scan the table for the current biggest taskId
    # and increment it by 1 for the new item
    # Perform a scan on the table
    response = table.scan()
    # Extract the taskIds from the response
    task_ids = [item['taskId'] for item in response.get('Items', [])]
    # Get the largest taskId (assuming taskId is a number)
    max_task_id = max(task_ids) if task_ids else 0

    # Create a new item to add
    to_add = { 'taskId': max_task_id + 1, 'title': title, 'completed': False }

    #Add item
    table.put_item(Item=to_add)

    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    # Updates an existing item
    # For this particular app, updating just toggles the completion between True / False
    # Create DynamoDB resource
    db = boto3.resource('dynamodb', region_name='ap-southeast-1')
    
    # Find table
    table = db.Table('todo-list-table')

    # Get the current completion status of the todo item
    response = table.get_item(Key={'taskId': todo_id})
    current_status = response['Item'].get('completed', False)

    table.update_item(Key={'taskId': todo_id}, 
                      UpdateExpression="SET completed = :val",  # Update the completed field to True
                      ExpressionAttributeValues={':val': not current_status}  # Toggle the value
    )

    return redirect(url_for("home"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    # Delete an item from the to-do list
    # Create DynamoDB resource
    db = boto3.resource('dynamodb', region_name='ap-southeast-1')
    
    # Find table
    table = db.Table('todo-list-table')

    # Delete item
    table.delete_item(Key={'taskId': todo_id})

    return redirect(url_for("home"))

if __name__ == "__main__":
    port =int(os.environ.get('PORT', 80))
    app.run(debug=True, port=port, host = '0.0.0.0')