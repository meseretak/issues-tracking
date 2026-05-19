import sys

file_path = "frontend/app.js"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Line 554 corresponds to index 553
    target_line = "    el.innerHTML = '<div class=\"empty-state\"><i class=\"fa fa-running\"></i><h3>No Active Sprint</h3><p>Start a sprint to use the Kanban board</p><button class=\"btn btn-primary\" onclick=\"nav('sprints')\">Go to Sprints</button></div>';\n"
    
    if "nav('sprints')" in lines[553]:
        lines[553] = "    el.innerHTML = `<div class=\"empty-state\"><i class=\"fa fa-running\"></i><h3>No Active Sprint</h3><p>Start a sprint to use the Kanban board</p><button class=\"btn btn-primary\" onclick=\"nav('sprints')\">Go to Sprints</button></div>`;\n"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("Successfully fixed syntax error on line 554.")
    else:
        print("Target string not found on line 554. Content is: " + repr(lines[553]))

except Exception as e:
    print("Error:", e)
sys.exit(0)
