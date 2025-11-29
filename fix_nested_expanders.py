import re
import sys

def find_nested_expanders(lines):
    """
    Find nested st.expander() calls by tracking indentation levels.
    Returns list of (line_no, indentation, line_content) for nested expanders.
    """
    nested_expanders = []
    expander_stack = []  # Stack of (line_no, indent_level)
    
    for i, line in enumerate(lines, 1):
        # Calculate indentation
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        
        # Check if this is an expander line
        if re.match(r'\s*with\s+st\.expander\s*\(', line):
            # If there's already an expander on the stack, this is nested
            if expander_stack:
                nested_expanders.append((i, indent, line))
            
            # Push this expander onto the stack
            expander_stack.append((i, indent))
        
        # Pop expanders from stack when we dedent past their level
        # Check if we've left the scope of any expanders
        if expander_stack:
            # If current line is less indented than the last expander, pop it
            while expander_stack and (not stripped or indent <= expander_stack[-1][1]):
                if stripped:  # Only pop if this is not a blank line
                    expander_stack.pop()
                    if not expander_stack:
                        break
                else:
                    break
    
    return nested_expanders

def fix_nested_expanders(input_file, output_file, backup_file):
    """
    Replace nested st.expander() with st.container() while preserving indentation.
    """
    # Read file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Create backup
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # Find nested expanders
    nested = find_nested_expanders(lines)
    
    if not nested:
        print("No nested expanders found.")
        return []
    
    # Replace nested expanders with containers
    changes = []
    for line_no, indent, original_line in nested:
        idx = line_no - 1
        old_line = lines[idx]
        
        # Extract the indentation
        spaces = ' ' * indent
        # Replace st.expander(...) with st.container()
        new_line = spaces + 'with st.container():\n'
        
        lines[idx] = new_line
        changes.append({
            'line': line_no,
            'old': old_line.rstrip(),
            'new': new_line.rstrip(),
            'indent': indent
        })
    
    # Write fixed file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return changes

# Main execution
if __name__ == "__main__":
    input_file = "app.py"
    output_file = "app.py"
    backup_file = "app.py.bak"
    
    changes = fix_nested_expanders(input_file, output_file, backup_file)
    
    if changes:
        print(f"Fixed {len(changes)} nested expanders:\n")
        
        # Read the file again to show context
        with open(output_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        for change in changes:
            line_no = change['line']
            print(f"Line {line_no}: replaced `with st.expander(...)` -> `with st.container()`")
            
            # Show 3 lines before
            start = max(0, line_no - 4)
            for i in range(start, line_no - 1):
                print(f"  {i+1:4d} | {all_lines[i].rstrip()}")
            
            # Show the changed line
            print(f"  {line_no:4d} | {change['new']}  <-- CHANGED")
            
            # Show 3 lines after
            end = min(len(all_lines), line_no + 3)
            for i in range(line_no, end):
                print(f"  {i+1:4d} | {all_lines[i].rstrip()}")
            
            print()
        
        print("Nested expanders fixed. Ready to run.")
    else:
        print("No nested expanders found. File unchanged.")
