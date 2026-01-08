"""Main entry point for the Healthcare UX News Agent."""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import get_settings
from src.agents.healthcare_news_agent import HealthcareNewsAgent
from src.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


def run_once(days_back: int = 7):
    """
    Run the agent once and exit.

    Args:
        days_back: Number of days to look back for articles
    """
    logger.info("Running agent in single-run mode")

    agent = HealthcareNewsAgent()

    # Verify setup first
    if not agent.verify_setup():
        logger.error("Setup verification failed. Please check your configuration.")
        sys.exit(1)

    # Run the agent
    stats = agent.run(days_back=days_back)

    # Print summary
    print("\n" + "="*60)
    print("HEALTHCARE UX NEWS AGENT - RUN SUMMARY")
    print("="*60)
    print(f"Articles collected: {stats['articles_collected']}")
    print(f"Articles analyzed: {stats['articles_analyzed']}")
    print(f"Articles published: {stats['articles_published']}")

    if stats.get('errors'):
        print(f"\nErrors encountered: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")

    print("="*60 + "\n")

    logger.info("Agent run complete")


def run_scheduled():
    """Run the agent on a schedule."""
    import schedule
    import time

    logger.info("Running agent in scheduled mode")

    settings = get_settings()
    interval_hours = settings.agent_run_interval_hours

    agent = HealthcareNewsAgent()

    # Verify setup first
    if not agent.verify_setup():
        logger.error("Setup verification failed. Please check your configuration.")
        sys.exit(1)

    def job():
        """Scheduled job function."""
        logger.info("Starting scheduled agent run")
        try:
            stats = agent.run()
            logger.info(f"Scheduled run complete: {stats['articles_published']} articles published")
        except Exception as e:
            logger.error(f"Error in scheduled run: {e}")

    # Schedule the job
    schedule.every(interval_hours).hours.do(job)

    # Run immediately on start
    logger.info(f"Running initial job, then every {interval_hours} hours")
    job()

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def verify_setup():
    """Verify that the agent is configured correctly."""
    logger.info("Verifying agent setup")

    agent = HealthcareNewsAgent()

    if agent.verify_setup():
        print("\n✓ Setup verification successful!")
        print("\nYour Notion database is accessible and ready to receive articles.")
        print("\nRun the agent with: python -m src.main run")
    else:
        print("\n✗ Setup verification failed")
        print("\nPlease check the logs for details and ensure:")
        print("  1. Your .env file is configured with all required API keys")
        print("  2. Your Notion database exists and is shared with the integration")
        print("  3. Your Notion database has the correct schema")
        sys.exit(1)


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Healthcare UX News Agent - Collect and analyze relevant news"
    )

    parser.add_argument(
        "command",
        choices=["run", "schedule", "verify"],
        help="Command to execute: 'run' (run once), 'schedule' (run on schedule), 'verify' (check setup)"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back for articles (default: 7)"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="Optional log file path"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(log_level=args.log_level, log_file=args.log_file)

    # Execute command
    try:
        if args.command == "run":
            run_once(days_back=args.days)
        elif args.command == "schedule":
            run_scheduled()
        elif args.command == "verify":
            verify_setup()

    except KeyboardInterrupt:
        logger.info("Interrupted by user, exiting")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
