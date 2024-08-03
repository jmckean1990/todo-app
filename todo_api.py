import pymongo
from flask import Flask, current_app, g, request
from bson import ObjectId


app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {
    "connection_uri" : "mongodb://localhost:27017",
    "db_name" : "todo_db"
}

@app.before_request
def init_db():
    if "db_client" not in g:
        current_app.config["db_client"] = pymongo.MongoClient(current_app.config["MONGODB_SETTINGS"]["connection_uri"])
        g.db = current_app.config["db_client"][current_app.config["MONGODB_SETTINGS"]["db_name"]]

@app.teardown_request
def close_db(exception):
    client = g.pop("db_client", None)
    # g.pop("db")

    if client is not None:
        client.close()

@app.route("/read_todo/<todo_id>")
def read_todo(todo_id):
    if not ObjectId.is_valid(todo_id):
        return "Invalid todo id", 400
    
    todo_collection = g.db.todos
    todo = todo_collection.find_one({"_id":ObjectId(str(todo_id))})
    
    if todo is None:
        return "Todo not found", 404
    else:
        return {"id":str(todo["_id"]), "todo":todo["todo"]}, 200

@app.route("/read_todos")
def read_todos():
    todo_collection = g.db.todos
    todo_cursor = todo_collection.find({})
    todo_list = []

    for todo in todo_cursor:
        todo_list.append({"id":str(todo["_id"]), "todo":todo["todo"]})

    return todo_list, 200


@app.route("/write_todo", methods=["POST"])
def write_todo():
    insert_data = request.get_json()
    todo_collection = g.db.todos
    id = todo_collection.insert_one(insert_data)

    return {"id":str(id.inserted_id), "todo":insert_data.get("todo")}, 200

@app.route("/update_todo/<todo_id>", methods=["PUT"])
def update_todo(todo_id):
    new_data = request.get_json()
    todo_collecion = g.db.todos

    result = todo_collecion.update_one({"_id":ObjectId(str(todo_id))}, {"$set":new_data})
    print(result)

    return "Update Successful", 200


@app.route("/delete_todo/<todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo_collection = g.db.todos

    result = todo_collection.delete_one({"_id":ObjectId(str(todo_id))})

    return "Delete Successful", 200



if __name__ == "__main__":
    app.run(debug=True)


