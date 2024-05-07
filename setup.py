from setuptools import setup

def parse_requirements(file_path):
    with open(file_path) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

requirements = parse_requirements("requirements.txt")

setup(
    name="aidetour",
    version="0.1.0",
    description="Translate OpenAI API requests to Anthropic API requests/responses for the Claude 3 models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cleesmith/Aidetour",
    author="Clee Smith",
    author_email="cleesmith2006@gmail.com",
    py_modules=["Aidetour"],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'aidetour=Aidetour:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
