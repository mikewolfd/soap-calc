from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist
import subprocess
import sys
from pathlib import Path

def generate_schemas():
    """Run the schema generation script."""
    script_path = Path(__file__).parent / "scripts" / "generate_schemas.py"
    print(f"Generating schemas using {script_path}...")
    try:
        subprocess.check_call([sys.executable, str(script_path)])
    except subprocess.CalledProcessError as e:
        print(f"Error generating schemas: {e}")
        sys.exit(1)

class BuildPy(build_py):
    """Custom build_py command to generate schemas before building."""
    def run(self):
        generate_schemas()
        super().run()

class SDist(sdist):
    """Custom sdist command to generate schemas before creating source distribution."""
    def run(self):
        generate_schemas()
        super().run()

setup(
    cmdclass={
        'build_py': BuildPy,
        'sdist': SDist,
    },
)
