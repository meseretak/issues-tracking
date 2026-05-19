with open(r'frontend\app.js', encoding='utf-8') as f:
    js = f.read()

# Let's search for "onclick="nav('sprints')"" or similar and replace it
# The exact error was:
# el.innerHTML = '<div class="empty-state"><i class="fa fa-running"></i><h3>No Active Sprint</h3><p>Start a sprint to use the Kanban board</p><button class="btn btn-primary" onclick="nav('sprints')">Go to Sprints</button></div>';

bad_line = "onclick=\"nav('sprints')\""
good_line = "onclick=\\\"nav(\\'sprints\\')\\\""

# Let's replace the whole string to be completely safe:
old_block = "'<div class=\"empty-state\"><i class=\"fa fa-running\"></i><h3>No Active Sprint</h3><p>Start a sprint to use the Kanban board</p><button class=\"btn btn-primary\" onclick=\"nav('sprints')\">Go to Sprints</button></div>'"
new_block = "'<div class=\"empty-state\"><i class=\"fa fa-running\"></i><h3>No Active Sprint</h3><p>Start a sprint to use the Kanban board</p><button class=\"btn btn-primary\" onclick=\"nav(\\'sprints\\')\">Go to Sprints</button></div>'"

if old_block in js:
    js = js.replace(old_block, new_block)
    print("Fixed via block replacement!")
else:
    # Let's do a direct replace of the bad onclick:
    js = js.replace("onclick=\"nav('sprints')\"", "onclick=\"nav(\\'sprints\\')\"")
    print("Fixed via simple replace!")

with open(r'frontend\app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Saved fixed app.js!")
