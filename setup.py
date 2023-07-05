from setuptools import setup, find_packages

setup(
    name="MultiClone",
    version="0.1.0",
    author="Henrik Dueholm",
    author_email="henrikdue@yahoo.dk",
    packages=find_packages(
        where=".",
        include=["multiclone*"]
    ),
    scripts=["app_main.py", "bin/test_main.py"],
    url="https://github.com/HenrikDueholm/App_MultiClone",
    license='LICENSE',
    description="A multi-cloning application for side by side cloning and post clone linking.",
    long_description=open('README.md').read(),
    install_requires=[
        'importlib-metadata; python_version >= "3.8"',
    ],
    entry_points={
        "console_scripts": [
            "multiclone = app_main:main"
        ]
    }
)