from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    default_one_time_text = "config system console\nset output standard\nend"
    default_looped_text = ""

    one_time_text = default_one_time_text
    output_script = ""
    looped_text = default_looped_text
    
    if request.method == 'POST':
        one_time_text = request.form.get("one_time", default_one_time_text)
        looped_text = request.form.get("looped", default_looped_text)
        
        if 'general_status' in request.form:
            one_time_text += "\nget sys status"
            looped_text += "\nfnsysctl date"
            looped_text += "\nget sys perf status"

        one_time_commands = one_time_text.split("\n")
        looped_commands = looped_text.split("\n")
        
        script_lines = [":INIT", "count=1", "\n", ":MAIN"]
        
        # Add one-time commands
        one_time_section = []
        for cmd in one_time_commands:
            cmd = cmd.strip()
            if cmd:
                if cmd.startswith("pause "):
                    one_time_section.append(cmd)
                else:
                    one_time_section.append(f"sendln '{cmd}'")
        
        if one_time_section:
            script_lines.append("; One time outputs")
            script_lines.extend(one_time_section)
        
        script_lines.append("goto Outputs")
        script_lines.append("")
        script_lines.append(":Outputs")
        
        # Add looped commands
        for cmd in looped_commands:
            cmd = cmd.strip()
            if cmd:
                if cmd.startswith("pause "):
                    script_lines.append(cmd)
                else:
                    script_lines.append(f"sendln '{cmd}'")
        
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
        
        output_script = "\n".join(script_lines)
    
    return render_template('index.html', output_script=output_script, one_time_text=one_time_text, looped_text=looped_text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8100)
