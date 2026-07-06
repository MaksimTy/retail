"""
Command-line interface for the retail AI agent.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from retail.agent.core import RetailAgent
from retail.config.settings import settings

app = typer.Typer(help="Retail AI Agent with Ontology-Augmented Generation (OAG)")
console = Console()

@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask the retail AI agent"),
):
    """Ask a question to the retail AI agent."""
    try:
        agent = RetailAgent()
        answer = agent.ask(question)
        console.print(Panel(answer, title="Answer", border_style="green"))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def chat():
    """Start an interactive chat session with the retail AI agent."""
    console.print("[bold green]Retail AI Agent - Interactive Chat[/bold green]")
    console.print("Type 'exit or 'quit' to exit.")
    
    agent = RetailAgent()
    
    while True:
        try:
            question = typer.prompt("\nAsk a question")
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            answer = agent.ask(question)
            console.print(Panel(answer, title="Answer", border_style="blue"))
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    console.print("\n[yellow]Goodbye![/yellow]")

@app.command()
def setup():
    """Set up the data warehouse by downloading and processing the UCI Online Retail dataset."""
    console.print("[bold blue]Setting up the data warehouse...[/bold blue]")
    
    try:
        # Import here to avoid circular imports
        from retail.data.source.uci_downloader import download_online_retail
        from retail.data.staging.cleaner import clean_and_save
        from retail.data.warehouse.loader import load_data
        
        # Step 1: Download data
        console.print("1. Downloading UCI Online Retail dataset...")
        df = download_online_retail()
        console.print(f"   Downloaded {len(df)} rows")
        
        # Step 2: Clean data
        console.print("2. Cleaning data...")
        clean_and_save()
        console.print("   Data cleaned and saved to staging area")
        
        # Step 3: Load into warehouse
        console.print("3. Loading data into the warehouse...")
        load_data()
        console.print("   Data loaded into the warehouse")
        
        console.print("[bold green]Setup completed successfully![/bold green]")
    except Exception as e:
        console.print(f"[red]Error during setup: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def info():
    """Show information about the agent and its configuration."""
    console.print("[bold blue]Retail AI Agent Information[/bold blue]")
    
    # Create a table for configuration
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("LLM Provider", settings.LLM_PROVIDER)
    table.add_row("Ollama Base URL", settings.OLLAMA_BASE_URL)
    table.add_row("Ollama Model", settings.OLLAMA_MODEL)
    table.add_row("OpenAI Model", settings.OPENAI_MODEL if settings.OPENAI_API_KEY else "Not configured")
    table.add_row("Anthropic Model", settings.ANTHROPIC_MODEL if settings.ANTHROPIC_API_KEY else "Not configured")
    table.add_row("Database Path", str(settings.DUCKDB_DATABASE_PATH))
    
    console.print(table)
    
    # Test LLM availability
    try:
        from retail.agent.llm.factory import create_llm_provider
        llm_provider = create_llm_provider()
        if llm_provider.is_available():
            console.print("[green]LLM Provider: Available[/green]")
        else:
            console.print("[red]LLM Provider: Not available[/red]")
    except Exception as e:
        console.print(f"[red]LLM Provider: Error - {e}[/red]")

if __name__ == "__main__":
    app()