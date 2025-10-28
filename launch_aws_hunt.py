import subprocess
import sys
import os

# Change to workspace directory
os.chdir(r'C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace')

# Launch AWS hunt with automated input
result = subprocess.run(
    [sys.executable, 'launch_jupiter_unified.py'],
    input='4\ny\n',
    text=True,
    capture_output=False
)
