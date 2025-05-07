from setuptools import setup, find_packages

setup(
    name="ctoken",
    version="1.0.0",
    description="A high-performance library to count and estimate costs for OpenAI API tokens",
    author="Karthik Vinayan",
    author_email="karthik@o1x3.com",
    url="https://github.com/o1x3/ctoken",
    packages=["ctoken", "ctoken.data"],
    package_data={
        "ctoken": ["data/*.py", "data/*.csv"],
    },
    include_package_data=True,
    install_requires=["requests>=2.25.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
)
