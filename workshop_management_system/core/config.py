"""Core Configuration Module.

Description:
- This module is responsible for core configuration and read values from
environment file.

"""

from environs import Env

env: Env = Env()
env.read_env(path=".env")

# Database

DATABASE_URL: str = env.str("DATABASE_URL")

# Super Admin
SUPERUSER_NAME: str = env.str("SUPERUSER_NAME")
SUPERUSER_USERNAME: str = env.str("SUPERUSER_USERNAME")
SUPERUSER_EMAIL: str = env.str("SUPERUSER_EMAIL")
SUPERUSER_PASSWORD: str = env.str("SUPERUSER_PASSWORD")
