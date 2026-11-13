import os
import subprocess


def run_python_file(working_directory: str, file_path: str, args: list[str] | None = None) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        # Will be True or False
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'"{file_path}" does not exist or is not a regular file'
        if not target_file.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        command = ["python", target_file]

        if args is not None:
            command.extend(args)
        completed_process = subprocess.run(command,cwd=working_directory,capture_output=True,text=True,timeout=30,)

        output_parts = []

        if completed_process.returncode != 0:
            output_parts.append(f"Process exited with code {completed_process.returncode}")

        if not completed_process.stdout and not completed_process.stderr:
            output_parts.append("No output produced")
        else:
            if completed_process.stdout:
                output_parts.append(f"STDOUT:\n{completed_process.stdout}")
            if completed_process.stderr:
                output_parts.append(f"STDERR:\n{completed_process.stderr}")

        output = "\n".join(output_parts)
        return output
    except Exception as e: # noqa: BLE001 - tool functions must always return a string
        return f"Error: executing Python file: {e}"

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Runs a specified Python file relative to the working directory with optional command-line arguments, returning its exit code, stdout and stderr",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path of the Python file to run, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of command-line arguments to pass to the Python file (default is no arguments)",
                },
            },
            "required": ["file_path"],
        },
    },
}
