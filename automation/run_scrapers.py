"""
PromoChecker - Automated Scraper Runner
Runs all spiders and imports data to database
"""
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def run_spider(spider_name: str, output_file: str) -> bool:
    """
    Run a Scrapy spider and save output to JSON file
    
    Args:
        spider_name: Name of the spider to run
        output_file: Path to output JSON file
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"  Running spider: {spider_name}")
    print(f"{'='*60}")
    
    try:
        # Remove old output file if exists
        output_path = PROJECT_ROOT / output_file
        if output_path.exists():
            output_path.unlink()
            print(f"  Removed old file: {output_file}")
        
        # Run scrapy spider
        result = subprocess.run(
            ['scrapy', 'crawl', spider_name, '-o', output_file],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            # Check if file was created and has data
            if output_path.exists():
                with open(output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    item_count = len(data)
                    print(f" Spider completed: {item_count} items scraped")
                    return True
            else:
                print(f" Spider failed: Output file not created")
                return False
        else:
            print(f" Spider failed with exit code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f" Spider timed out after 10 minutes")
        return False
    except Exception as e:
        print(f" Error running spider: {e}")
        return False


def run_normalization() -> bool:
    """
    Run normalization script to process scraped data
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f" Running normalization")
    print(f"{'='*60}")
    
    try:
        # Get Python executable from venv
        if os.name == 'nt':  # Windows
            python_exe = PROJECT_ROOT / 'venv' / 'Scripts' / 'python.exe'
        else:  # Linux/Mac
            python_exe = PROJECT_ROOT / 'venv' / 'bin' / 'python'
        
        # Run normalization script
        result = subprocess.run(
            [str(python_exe), 'normalize_all.py'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(" Normalization completed")
            # Print output to see match results
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f" Normalization failed with exit code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f" Normalization timed out after 5 minutes")
        return False
    except Exception as e:
        print(f" Error running normalization: {e}")
        return False


def import_to_database() -> bool:
    """
    Import normalized data to PostgreSQL database
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f" Importing to database")
    print(f"{'='*60}")
    
    try:
        # Get Python executable from venv
        if os.name == 'nt':  # Windows
            python_exe = PROJECT_ROOT / 'venv' / 'Scripts' / 'python.exe'
        else:  # Linux/Mac
            python_exe = PROJECT_ROOT / 'venv' / 'bin' / 'python'
        
        # Run database import script
        result = subprocess.run(
            [str(python_exe), 'database/import_to_db.py'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(" Database import completed")
            # Print output to see import results
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f" Database import failed with exit code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f" Database import timed out after 5 minutes")
        return False
    except Exception as e:
        print(f" Error importing to database: {e}")
        return False


def run_full_pipeline():
    """
    Run the complete scraping pipeline:
    1. Run all spiders
    2. Normalize data
    3. Import to database
    """
    start_time = datetime.now()
    print(f"\n{'#'*60}")
    print(f" Starting PromoChecker automated scraping")
    print(f" Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")
    
    # Define spiders and their output files
    spiders = [
        ('mytekproducts', 'mytek_laptops.json'),
        ('tunisianet_laptops', 'tunisianet_laptops.json'),
        ('spacenetproducts', 'spacenet_laptops.json')
    ]
    
    # Track results
    results = {
        'spiders': {},
        'normalization': False,
        'database_import': False
    }
    
    # Step 1: Run all spiders
    for spider_name, output_file in spiders:
        success = run_spider(spider_name, output_file)
        results['spiders'][spider_name] = success
    
    # Check if at least one spider succeeded
    if not any(results['spiders'].values()):
        print("\n All spiders failed! Aborting pipeline.")
        return results
    
    # Step 2: Run normalization
    results['normalization'] = run_normalization()
    
    if not results['normalization']:
        print("\n Normalization failed! Aborting pipeline.")
        return results
    
    # Step 3: Import to database
    results['database_import'] = import_to_database()
    
    # Print summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n{'#'*60}")
    print(f" Pipeline Summary")
    print(f"{'#'*60}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"\n  Spiders:")
    for spider_name, success in results['spiders'].items():
        status = "" if success else ""
        print(f"  {status} {spider_name}")
    print(f"\n Normalization: {'' if results['normalization'] else ''}")
    print(f" Database Import: {'' if results['database_import'] else ''}")
    
    all_success = (
        any(results['spiders'].values()) and
        results['normalization'] and
        results['database_import']
    )
    
    if all_success:
        print(f"\n Pipeline completed successfully!")
    else:
        print(f"\n  Pipeline completed with some failures")
    
    print(f"{'#'*60}\n")
    
    return results


if __name__ == "__main__":
    run_full_pipeline()
