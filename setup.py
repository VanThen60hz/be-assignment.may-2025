from setuptools import setup, find_packages

setup(
    name="messaging-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.23",
        "alembic>=1.12.1",
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.0.0",
        "pydantic>=2.4.2",
        "email-validator>=2.1.0",
    ],
)
