#!/usr/bin/env python3
"""
Airflow Connection Setup Script

This script programmatically creates Airflow connections to avoid manual UI configuration.
Run this after Airflow initialization to set up database connections.

Usage:
    python setup_connections.py

Environment Variables:
    SCREENER_DB_HOST: PostgreSQL host (default: postgres)
    SCREENER_DB_PORT: PostgreSQL port (default: 5432)
    SCREENER_DB_NAME: Database name (default: screener_db)
    SCREENER_DB_USER: Database user (default: screener_user)
    SCREENER_DB_PASSWORD: Database password (required)
"""

import os
import sys
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_screener_db_connection() -> bool:
    """
    Create PostgreSQL connection for screener_db.

    Returns:
        True if connection created successfully, False otherwise
    """
    try:
        from airflow.models import Connection
        from airflow.utils.db import create_session

        # Get environment variables
        host = os.getenv('SCREENER_DB_HOST', 'postgres')
        port = int(os.getenv('SCREENER_DB_PORT', '5432'))
        schema = os.getenv('SCREENER_DB_NAME', 'screener_db')
        login = os.getenv('SCREENER_DB_USER', 'screener_user')
        password = os.getenv('SCREENER_DB_PASSWORD')

        if not password:
            logger.error("SCREENER_DB_PASSWORD environment variable not set")
            return False

        # Create connection object
        conn_id = 'screener_db'

        with create_session() as session:
            # Check if connection already exists
            existing_conn = session.query(Connection).filter(
                Connection.conn_id == conn_id
            ).first()

            if existing_conn:
                logger.info(f"Connection '{conn_id}' already exists, updating...")
                existing_conn.host = host
                existing_conn.port = port
                existing_conn.schema = schema
                existing_conn.login = login
                existing_conn.set_password(password)
            else:
                logger.info(f"Creating new connection '{conn_id}'...")
                new_conn = Connection(
                    conn_id=conn_id,
                    conn_type='postgres',
                    host=host,
                    port=port,
                    schema=schema,
                    login=login,
                )
                new_conn.set_password(password)
                session.add(new_conn)

            session.commit()
            logger.info(f"Connection '{conn_id}' configured successfully")
            logger.info(f"  Host: {host}")
            logger.info(f"  Port: {port}")
            logger.info(f"  Schema: {schema}")
            logger.info(f"  Login: {login}")

        return True

    except ImportError as e:
        logger.error(f"Failed to import Airflow modules: {e}")
        logger.error("Make sure Airflow is installed and AIRFLOW_HOME is set")
        return False
    except Exception as e:
        logger.error(f"Failed to create connection: {e}")
        return False


def test_connection(conn_id: str = 'screener_db') -> bool:
    """
    Test the database connection.

    Args:
        conn_id: Connection ID to test

    Returns:
        True if connection test passes, False otherwise
    """
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        logger.info(f"Testing connection '{conn_id}'...")

        hook = PostgresHook(postgres_conn_id=conn_id)

        # Execute simple query
        result = hook.get_first("SELECT version()")

        if result:
            logger.info(f"Connection test successful!")
            logger.info(f"PostgreSQL version: {result[0][:50]}...")
            return True
        else:
            logger.error("Connection test failed: no result returned")
            return False

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


def main():
    """Main function to set up all connections."""
    logger.info("=" * 80)
    logger.info("Airflow Connection Setup")
    logger.info("=" * 80)

    # Check if Airflow is initialized
    airflow_home = os.getenv('AIRFLOW_HOME')
    if not airflow_home:
        logger.error("AIRFLOW_HOME environment variable not set")
        logger.error("Please initialize Airflow first: airflow db init")
        sys.exit(1)

    logger.info(f"AIRFLOW_HOME: {airflow_home}")

    # Set up connections
    success = setup_screener_db_connection()

    if not success:
        logger.error("Failed to set up connections")
        sys.exit(1)

    # Test connection
    logger.info("")
    logger.info("Testing connection...")
    test_success = test_connection('screener_db')

    if not test_success:
        logger.warning("Connection created but test failed")
        logger.warning("Please check database is running and credentials are correct")
        sys.exit(1)

    logger.info("")
    logger.info("=" * 80)
    logger.info("Connection setup completed successfully!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("You can now:")
    logger.info("  1. Start Airflow webserver: airflow webserver")
    logger.info("  2. Start Airflow scheduler: airflow scheduler")
    logger.info("  3. Access UI at http://localhost:8080")


if __name__ == '__main__':
    main()
