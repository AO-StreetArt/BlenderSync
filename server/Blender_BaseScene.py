import rethinkdb as r
r.connect("localhost", 28015).repl()
r.db("test").table_create("objects").run()
r.table("objects").insert({
	"name": "Cube",
	"type": "Mesh",
	"subtype": "Cube",
	"location": {"x": 0.0, "y": 0.0, "z": 0.0},
	"rotation_euler": {"x": 0.0, "y": 0.0, "z": 0.0},
	"rotation_quaternion": {"a": 0.0, "b": 0.0, "c": 0.0, "d": 0.0},
	"scale": {"x": 0.0, "y": 0.0, "z": 0.0}
}).run()
r.table("objects").insert({
	"name": "Lamp",
	"type": "Lamp",
	"subtype": "Spot",
	"location": {"x": 5.0, "y": 0.0, "z": 0.0},
	"rotation_euler": {"x": 0.0, "y": 0.0, "z": 0.0},
	"rotation_quaternion": {"a": 0.0, "b": 0.0, "c": 0.0, "d": 0.0},
	"scale": {"x": 0.0, "y": 0.0, "z": 0.0}
}).run()
r.table("objects").insert({
	"name": "Camera",
	"type": "Camera",
	"subtype": "Camera",
	"location": {"x": 0.0, "y": 0.0, "z": 0.0},
	"rotation_euler": {"x": 0.0, "y": 0.0, "z": 0.0},
	"rotation_quaternion": {"a": 0.0, "b": 0.0, "c": 0.0, "d": 0.0},
	"scale": {"x": 0.0, "y": 0.0, "z": 0.0}
}).run()