from flask import Flask, render_template, request, redirect, url_for, session
import os
import boto3
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)  # Generates a secure random key

sort_tuple = ('taskId', True)  # Default sort by newest

def create_test_client():
    return app.test_client()

def pagination_scan(table):
    """
    This function scans the DynamoDB table and handles pagination.
    It returns all items in the table.
    """
    response = table.scan()
    items = response.get('Items', [])
    
    # Continue scanning if there are more items to retrieve
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    return items

@app.route("/index")
def index():
    return 'hello world'

#Links with display
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
    todo_list = pagination_scan(table)

    # Retrieve the sort_tuple from session, or use default of sorting by Newest if not set
    sort_tuple = session.get('sort_tuple', ('taskId', True))

    # Sort the todo_list based on user selection
    todo_list.sort(key=lambda x: x[sort_tuple[0]], reverse=sort_tuple[1])

    return render_template("base.html", todo_list=todo_list)


@app.route("/updatetaskpost", methods=['GET', 'POST'])
def update_task_post():
    todo_title = request.args.get('todo_title')
    todo_id = int(request.args.get('todo_id'))
    if request.method == 'POST':
        new_title = request.form.get("title")

        # Create DynamoDB resource
        db = boto3.resource('dynamodb', region_name='ap-southeast-1')
        
        # Find table
        table = db.Table('todo-list-table')

        table.update_item(Key={'taskId': todo_id}, 
                        UpdateExpression="SET title = :val",  # Update the title
                        ExpressionAttributeValues={':val': new_title}  # Toggle the value
        )

        return redirect(url_for("home"))


        
    return render_template("updatetask.html", todo_title=todo_title, todo_id=todo_id)




#Links without display
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
    result_items = pagination_scan(table)
    # Extract the taskIds from the response
    task_ids = [item['taskId'] for item in result_items]
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


@app.route("/update_task/<int:todo_id>")
def update_task(todo_id):
    #Updates the task name
    #Creates the dynamo resource
    db = boto3.resource('dynamodb', region_name='ap-southeast-1')
    
    #Find table
    table = db.Table('todo-list-table')

    #Get the current name of the task
    response = table.get_item(Key={'taskId': todo_id})
    current_title = response['Item'].get('title')

    return redirect(url_for('update_task_post', todo_title=current_title, todo_id=todo_id))




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

@app.route("/rearrange/<sort_string>")
def rearrange(sort_string):
    sort_string = sort_string.split('x')
    if sort_string[0] == 'a':
        # Sort by Time
        sort_key = 'taskId'
    elif sort_string[0] == 'b':
        # Sort by A-Z
        sort_key = 'title'
    session['sort_tuple'] = (sort_key, sort_string[1]=='b') # False for ascending, True for descending

    return redirect(url_for("home"))

if __name__ == "__main__":
    port =int(os.environ.get('PORT', 80))
    app.run(port=port, host = '0.0.0.0')