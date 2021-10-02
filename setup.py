import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="landslide_sentry",
    version="0.0.1",
    author="Qiuyang Chen, Chenyu Zhang",
    author_email="qiuyangschen@gmail.com, goodzhcy@gmail.com",
    description="Landside detection pipeline using geosat data and neural network. Created for 2021 NASA space apps challenge - Team SENTRY",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChenyuZhang16/nasa-space-app-sentry",
    project_urls={
        "Bug Tracker": "https://github.com/ChenyuZhang16/nasa-space-app-sentry/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
)