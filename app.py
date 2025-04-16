from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    default_one_time_text = "####################### Start one time outputs #######################\nconfig system console\nset output standard\nend"
    default_looped_text = "####################### Start looped outputs #######################\nfnsysctl date\n"

    one_time_text = default_one_time_text
    looped_text = default_looped_text
    output_script = ""

    # Capture checkbox states
    batched_logs_checked = 'batched_logs' in request.form
    wait_prompt_checked = 'wait_prompt' in request.form
    vdom_aware_checked = 'vdom_aware' in request.form
    general_status_checked = 'general_status' in request.form
    cpu_memory_checked = 'cpu_memory' in request.form
    cpu_profile_checked = 'cpu_profile' in request.form
    ips_checked = 'ips' in request.form
    wad_checked = 'wad' in request.form

    if request.method == 'POST':
        one_time_text = request.form.get("one_time", default_one_time_text)
        looped_text = request.form.get("looped", default_looped_text)
        wait_prompt_checked = 'wait_prompt' in request.form

        
        if 'general_status' in request.form:
            one_time_text += "\nget sys status"
            looped_text += "\nfnsysctl date\nget sys perf status"

        one_time_commands = one_time_text.split("\n")
        looped_commands = looped_text.split("\n")
        
        script_lines = [":INIT", "count=1", "\n", ":MAIN"]
        
        # Add monitoring script if wait_prompt is selected
        if wait_prompt_checked:
            script_lines.insert(0, "; monitoring script\nFGTprompt='[\\w\\.\\-]+(?: \\\([\\w\\.\\-]+\\\))? # '\n;")
        
        # Add one-time commands
        one_time_section = []
        for cmd in one_time_text.split("\n"):
            cmd = cmd.strip()
            if cmd:
                if cmd.startswith("pause "):
                    one_time_section.append(cmd)
                else:
                    one_time_section.append(f"sendln '{cmd}'")
                if wait_prompt_checked:
                    one_time_section.append("call ics")

        if one_time_section:
            script_lines.append("; One time outputs")
            script_lines.extend(one_time_section)

        script_lines.append("goto Outputs")
        script_lines.append("")
        script_lines.append(":Outputs")

        # Add looped commands
        looped_section = []
        for cmd in looped_text.split("\n"):
            cmd = cmd.strip()
            if cmd:
                if cmd.startswith("pause "):
                    looped_section.append(cmd)
                else:
                    looped_section.append(f"sendln '{cmd}'")
                if wait_prompt_checked:
                    looped_section.append("call ics")

        script_lines.extend(looped_section)
        
        script_lines.extend([
            "call looping",
            "goto Outputs",
            "return",
            "",
            ":looping",
            "if count > 10000 then",
            "  end",
            "else",
            "  count=count+1",
            "  return",
            "endif"
        ])
        
        # Add the :ics section if wait_prompt is selected
        if wait_prompt_checked:
            script_lines.append("")
            script_lines.append(":ics")
            script_lines.append("waitregex FGTprompt")
            script_lines.append("mpause 100")
            script_lines.append("return")

        output_script = "\n".join(script_lines)
        
    return render_template(
        'index.html',
        output_script=output_script,
        one_time_text=one_time_text,
        looped_text=looped_text,
        batched_logs_checked=batched_logs_checked,
        wait_prompt_checked=wait_prompt_checked,
        vdom_aware_checked=vdom_aware_checked,
        general_status_checked=general_status_checked
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8100)
