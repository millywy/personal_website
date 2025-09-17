"""Main CLI entrypoint for HKJC scraper."""

import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .constants import get_config
from .horse_detail import HorseDetailScraper
from .models import HorseRecord, ToplineData
from .racecard import RaceCardScraper
from .utils import (
    load_checkpoint,
    random_delay,
    save_checkpoint,
    save_final_output,
    setup_logging,
    validate_course,
    validate_date_format,
    validate_race_number,
)

# Load environment variables
load_dotenv()

console = Console()


@click.command()
@click.option(
    "--date",
    required=True,
    help="Race date in YYYY/MM/DD format (e.g., 2025/09/17)"
)
@click.option(
    "--course", 
    required=True,
    type=click.Choice(["HV", "ST"], case_sensitive=False),
    help="Racecourse code (HV for Happy Valley, ST for Sha Tin)"
)
@click.option(
    "--raceno",
    required=True,
    type=int,
    help="Race number (1-12)"
)
@click.option(
    "--out",
    required=True,
    help="Output JSON file path"
)
@click.option(
    "--checkpoint",
    help="Checkpoint file path for resuming interrupted runs"
)
@click.option(
    "--headful",
    is_flag=True,
    help="Run browser in headful mode (visible)"
)
@click.option(
    "--max-retries",
    type=int,
    default=3,
    help="Maximum number of retries per operation"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level"
)
def main(
    date: str,
    course: str,
    raceno: int,
    out: str,
    checkpoint: Optional[str],
    headful: bool,
    max_retries: int,
    log_level: str,
) -> None:
    """HKJC Race Data Scraper
    
    Scrapes horse race data from Hong Kong Jockey Club website.
    
    Example:
        python -m hkjc_scraper --date 2025/09/17 --course HV --raceno 1 --out hv_r1.json
    """
    
    # Setup logging
    logger = setup_logging(log_level)
    
    # Validate inputs
    if not validate_date_format(date):
        console.print("[red]Error: Invalid date format. Use YYYY/MM/DD[/red]")
        sys.exit(1)
    
    if not validate_course(course):
        console.print("[red]Error: Invalid course. Use HV or ST[/red]")
        sys.exit(1)
    
    if not validate_race_number(raceno):
        console.print("[red]Error: Invalid race number. Use 1-12[/red]")
        sys.exit(1)
    
    # Get configuration
    config = get_config()
    config["headless"] = not headful
    config["max_retries"] = max_retries
    
    console.print(f"[green]Starting HKJC scraper for {date} {course} Race {raceno}[/green]")
    console.print(f"[blue]Output: {out}[/blue]")
    if checkpoint:
        console.print(f"[blue]Checkpoint: {checkpoint}[/blue]")
    
    try:
        # Load checkpoint if provided
        horses = []
        if checkpoint and Path(checkpoint).exists():
            horses = load_checkpoint(checkpoint, logger)
            console.print(f"[yellow]Loaded checkpoint with {len(horses)} horses[/yellow]")
        
        # Run scraper
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=config["headless"],
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            
            try:
                # Initialize scrapers
                race_scraper = RaceCardScraper(browser, logger)
                detail_scraper = HorseDetailScraper(browser, logger)
                
                # Scrape race card if no checkpoint
                if not horses:
                    console.print("[blue]Scraping race card...[/blue]")
                    topline_data = race_scraper.scrape_race(date, course, raceno)
                    console.print(f"[green]Found {len(topline_data)} horses in race[/green]")
                else:
                    # Convert existing horses back to topline data for detail scraping
                    topline_data = []
                    for horse in horses:
                        topline_dict = horse.model_dump()
                        topline_dict["detail_url"] = None  # Will be re-extracted
                        topline_data.append(ToplineData(**topline_dict))
                
                # Scrape horse details
                if topline_data:
                    console.print("[blue]Scraping horse details...[/blue]")
                    
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                    ) as progress:
                        task = progress.add_task("Scraping horses...", total=len(topline_data))
                        
                        for i, horse_data in enumerate(topline_data):
                            try:
                                # Skip if we already have detail data (from checkpoint)
                                if (checkpoint and i < len(horses) and 
                                    horses[i].傷病記錄 and horses[i].往績紀錄):
                                    progress.update(task, advance=1)
                                    continue
                                
                                # Scrape details if we have a detail URL
                                if horse_data.detail_url:
                                    details = detail_scraper.scrape_horse_details(horse_data.detail_url)
                                    
                                    # Merge topline and detail data
                                    merged_data = horse_data.model_dump()
                                    merged_data.update(details)
                                    
                                    # Create final horse record
                                    horse_record = HorseRecord(**merged_data)
                                    
                                    # Update or add to horses list
                                    if i < len(horses):
                                        horses[i] = horse_record
                                    else:
                                        horses.append(horse_record)
                                    
                                    logger.info(f"Completed horse {i+1}/{len(topline_data)}: {horse_record.馬名}")
                                
                                # Save checkpoint every N horses
                                if checkpoint and (i + 1) % config["checkpoint_interval"] == 0:
                                    save_checkpoint(horses, checkpoint, logger)
                                
                                progress.update(task, advance=1)
                                random_delay()
                                
                            except Exception as e:
                                logger.error(f"Error scraping horse {i+1}: {e}")
                                progress.update(task, advance=1)
                                continue
                
                # Save final output
                console.print("[blue]Saving final output...[/blue]")
                save_final_output(horses, out, logger)
                
                console.print(f"[green]Successfully scraped {len(horses)} horses![/green]")
                console.print(f"[green]Output saved to: {out}[/green]")
                
            finally:
                browser.close()
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Scraping interrupted by user[/yellow]")
        if checkpoint:
            save_checkpoint(horses, checkpoint, logger)
            console.print(f"[yellow]Progress saved to checkpoint: {checkpoint}[/yellow]")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        console.print(f"[red]Fatal error: {e}[/red]")
        if checkpoint:
            save_checkpoint(horses, checkpoint, logger)
            console.print(f"[yellow]Progress saved to checkpoint: {checkpoint}[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    main()
