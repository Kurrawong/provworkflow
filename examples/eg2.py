from provworkflow import Workflow, Block, Entity

# set up the Workflow and Block
w = Workflow(label="My Simple Workflow 2")
b = Block()

# Block 1
b.used = [
    Entity(value="local data"),
    Entity(uri="http://example.com/endpoint"),
]
e_int = Entity(label="Internal Entity")
e_ext = Entity(label="External Entity", external=True)
b.generated = [e_int, e_ext]
w.blocks.append(b)

# Block 2
b2 = Block()
b2.used = [Entity(value="other local data"), e_int, e_ext]
b2.generated.append(
    Entity(uri="http://somewhere-on-s3/d/e/f", label="Final Workflow Output")
)
w.blocks.append(b2)

# print out
print(w.prov_to_graph().serialize(format="turtle"))
