import json
import http.client
import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="*")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

@app.post("/cars/find")
async def find_cars():
    body = await quart.request.get_data()
    body = json.loads(body)
    # print to console
    # print(body)
    conn = http.client.HTTPSConnection("gw.dod.com.tr")
    payload = json.dumps({
        "categoryIds": body["categoryIds"] if "categoryIds" in body else [2],
        "brands": body["brands"] if "brands" in body else [],
        "models": body["models"] if "models" in body else [0],
        "fuelTypes":[],
        "gearTypes": [], 
        "year": body["year"] if "year" in body else {
            "minYear": 0,
            "maxYear": 0
        },
        "km": body["km"] if "km" in body else {
            "minKm": 0,
            "maxKm": 0
        },
        "price": body["price"] if "price" in body else {
            "minPrice": 0,
            "maxPrice": 0
        },
        "guarantyStates": [],
        "cityCodes": body["cityCodes"] if "cityCodes" in body else [],
        "firms": [],
        "vehicleVarieties": [],
        "vehicleEngineCapacities": [],
        "vehicleEnginePowers": [],
        "drivenWheels": [],
        "vehicleClassess": [],
        "vehicleTypes": [],
        "vehicleColors": [],
        "stockEntryDate": 0,
        "inner360": False,
        "isCampaignVehicle": False,
        "isRentable": False,
        "fileNumber": "",
        "keyword": "",
        "currencyCode": "",
        "sortingCriteria": 0,
        "viewType": 0,
        "pagination": body["pagination"] if "pagination" in body else {
            "page": 1,
            "pageSize": 20
        },
        "isQueryParam": True,
        "hardwarelevel": []
    })
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0',
    }
    conn.request("POST", "/gw-search/SearchByFieldDodCarDetailIndex", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return data.decode("utf-8")

@app.post("/todos/<string:username>")
async def add_todo(username):
    request = await quart.request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request["todo"])
    return quart.Response(response='OK', status=200)

@app.get("/todos/<string:username>")
async def get_todos(username):
    return quart.Response(response=json.dumps(_TODOS.get(username, [])), status=200)

@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request = await quart.request.get_json(force=True)
    todo_idx = request["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return quart.Response(response='OK', status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=80)

if __name__ == "__main__":
    main()
