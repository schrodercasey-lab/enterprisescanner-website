"""
Setup configuration for Enterprise Scanner Phase 3
Automated Remediation & Monitoring Platform
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version info
version_info = {}
with open("modules/__version__.py") as f:
    exec(f.read(), version_info)

# Read README
readme_file = Path(__file__).parent / "README_PHASE3.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = "Enterprise Scanner Phase 3: Automated Remediation & Monitoring"

# Read requirements
requirements_file = Path(__file__).parent / "requirements-phase3.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="enterprise-scanner-phase3",
    version=version_info['__version__'],
    author="Enterprise Scanner Team",
    author_email="security@enterprisescanner.com",
    description="Phase 3: Automated Remediation & Continuous Security Monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://enterprisescanner.com",
    project_urls={
        "Documentation": "https://enterprisescanner.com/docs",
        "Source": "https://github.com/schrodercasey-lab/enterprisescanner-website",
        "Bug Tracker": "https://github.com/schrodercasey-lab/enterprisescanner-website/issues",
    },
    packages=find_packages(include=['modules', 'modules.*', 'cli', 'cli.*', 'api', 'api.*']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'ipython>=8.0.0',
        ],
        'docs': [
            'sphinx>=7.0.0',
            'sphinx-rtd-theme>=1.3.0',
        ],
        'full': [
            'requests>=2.28.0',
            'cryptography>=41.0.0',
            'pyyaml>=6.0',
            'python-dotenv>=1.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'phase3-cli=cli.phase3_cli:main',
            'phase3-health=api.phase3_health:main',
            'phase3-migrate=migrations.phase3_migrations:main',
        ],
    },
    include_package_data=True,
    package_data={
        'modules': ['templates/*.tpl', 'remediation_output/*'],
        'templates': ['remediation/*.tpl'],
    },
    zip_safe=False,
    keywords=[
        'security',
        'vulnerability',
        'remediation',
        'monitoring',
        'automation',
        'compliance',
        'devops',
        'enterprise',
    ],
    platforms=['any'],
)
