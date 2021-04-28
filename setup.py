from setuptools import setup, find_packages
with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()
setup(
    name="yootto",
    version="0.1.3",
    description="yootto(ヨーッと) is tiny YouTube Music unofficial uploader",
    author="yanoshi",
    author_email="",
    url="https://github.com/yanoshi/yootto",
    packages=find_packages(),
    install_requires=install_requirements,
    python_requires='>3.6',
    entry_points={
        "console_scripts": [
            "yootto=yootto.core:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
