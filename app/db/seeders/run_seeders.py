"""Main seeder runner."""

import asyncio
import sys

from app.config.settings import Settings
from app.db.database import DatabaseManager
from app.db.seeders import SeederRegistry
from app.db.seeders.seeds import *  # noqa: F403
from app.logger import logger


async def run_all_seeders(specific_seeders: list[str] | None = None):
    """
    Run all registered seeders or specific ones.

    Args:
        specific_seeders: List of seeder names to run. If None, runs all seeders.
    """
    settings = Settings.initialize()
    db_manager = DatabaseManager()

    try:
        await db_manager.initialize(settings)
        logger.info("Database connection established")

        # Get all registered seeders
        seeder_classes = SeederRegistry.get_seeders()

        if not seeder_classes:
            logger.warning("No seeders registered!")
            return

        if specific_seeders:
            seeder_classes = [
                s
                for s in seeder_classes
                if s.__name__ in specific_seeders or s().name in specific_seeders
            ]

            if not seeder_classes:
                logger.error(f"No seeders found matching: {specific_seeders}")
                return

        logger.info(f"Found {len(seeder_classes)} seeder(s) to run")

        async with db_manager.get_session() as session:
            for seeder_class in seeder_classes:
                seeder = seeder_class()
                logger.info(f"Running seeder: {seeder.name} (order: {seeder.order})")

                try:
                    await seeder.seed(session)
                    await session.commit()
                    logger.info(f"✓ {seeder.name} completed successfully")
                except Exception as e:
                    logger.error(f"✗ {seeder.name} failed", error=str(e))
                    await session.rollback()
                    raise

        logger.info("All seeders completed successfully!")

    except Exception as e:
        logger.error("Error running seeders", error=str(e))
        raise
    finally:
        await db_manager.close()
        logger.info("Database connection closed")


async def main():
    """Main entry point for seeder runner."""
    # Parse command line arguments
    specific_seeders = None
    if len(sys.argv) > 1:
        specific_seeders = sys.argv[1:]
        logger.info(f"Running specific seeders: {specific_seeders}")
    else:
        logger.info("Running all registered seeders...")

    await run_all_seeders(specific_seeders)


if __name__ == "__main__":
    asyncio.run(main())
