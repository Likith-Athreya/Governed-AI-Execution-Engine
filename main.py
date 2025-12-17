from agentic.graph import graph
from core.audit_logger import init_db

init_db()

user_input = "Show customer names only"

result = graph.invoke({
    "user_input": user_input
})

print("\n====")
print("USER INPUT:")
print(user_input)

print("\nFINAL GOVERNED RESULT:")
print(result["final_result"])
print("====")
