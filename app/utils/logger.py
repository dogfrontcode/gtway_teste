"""
Custom logging utilities with colors and formatting.
"""
import sys
from datetime import datetime


class Colors:
    """ANSI color codes."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_RED = '\033[41m'
    BG_BLUE = '\033[44m'


def format_timestamp():
    """Get formatted timestamp."""
    return datetime.now().strftime('%H:%M:%S')


def log_success(message: str):
    """Log success message."""
    timestamp = format_timestamp()
    print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.GREEN}✓{Colors.RESET} {Colors.BRIGHT_WHITE}{message}{Colors.RESET}")
    sys.stdout.flush()


def log_error(message: str):
    """Log error message."""
    timestamp = format_timestamp()
    print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.RED}✗{Colors.RESET} {Colors.BRIGHT_RED}{message}{Colors.RESET}")
    sys.stdout.flush()


def log_warning(message: str):
    """Log warning message."""
    timestamp = format_timestamp()
    print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.YELLOW}⚠{Colors.RESET} {Colors.BRIGHT_YELLOW}{message}{Colors.RESET}")
    sys.stdout.flush()


def log_info(message: str):
    """Log info message."""
    timestamp = format_timestamp()
    print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {Colors.CYAN}ℹ{Colors.RESET} {Colors.BRIGHT_WHITE}{message}{Colors.RESET}")
    sys.stdout.flush()


def log_api(method: str, endpoint: str, status: int, duration_ms: float = None):
    """Log API request."""
    timestamp = format_timestamp()
    
    # Color based on status
    if status < 300:
        status_color = Colors.GREEN
        icon = "✓"
    elif status < 400:
        status_color = Colors.YELLOW
        icon = "→"
    else:
        status_color = Colors.RED
        icon = "✗"
    
    # Method colors
    method_colors = {
        'GET': Colors.BLUE,
        'POST': Colors.GREEN,
        'PUT': Colors.YELLOW,
        'PATCH': Colors.YELLOW,
        'DELETE': Colors.RED,
    }
    method_color = method_colors.get(method, Colors.WHITE)
    
    duration_str = f" ({duration_ms:.0f}ms)" if duration_ms else ""
    
    print(
        f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} "
        f"{status_color}{icon}{Colors.RESET} "
        f"{method_color}{method:6}{Colors.RESET} "
        f"{Colors.BRIGHT_WHITE}{endpoint}{Colors.RESET} "
        f"{status_color}{status}{Colors.RESET}"
        f"{Colors.BRIGHT_BLACK}{duration_str}{Colors.RESET}"
    )
    sys.stdout.flush()


def log_startup_banner():
    """Print startup banner."""
    banner = f"""
{Colors.BRIGHT_CYAN}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              {Colors.BRIGHT_WHITE}💳  Payment Gateway API{Colors.BRIGHT_CYAN}                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
{Colors.RESET}
{Colors.BRIGHT_WHITE}🚀 Servidor iniciado com sucesso!{Colors.RESET}

{Colors.BRIGHT_CYAN}►{Colors.RESET} Backend:  {Colors.BRIGHT_YELLOW}http://localhost:5001{Colors.RESET}
{Colors.BRIGHT_CYAN}►{Colors.RESET} Swagger:  {Colors.BRIGHT_YELLOW}http://localhost:5001/swagger/{Colors.RESET}
{Colors.BRIGHT_CYAN}►{Colors.RESET} Frontend: {Colors.BRIGHT_YELLOW}http://localhost:5173{Colors.RESET}

{Colors.BRIGHT_GREEN}✓{Colors.RESET} Banco de dados: {Colors.GREEN}Conectado{Colors.RESET}
{Colors.BRIGHT_GREEN}✓{Colors.RESET} JWT: {Colors.GREEN}Configurado{Colors.RESET}
{Colors.BRIGHT_GREEN}✓{Colors.RESET} CORS: {Colors.GREEN}Habilitado{Colors.RESET}

{Colors.BRIGHT_BLACK}Pressione Ctrl+C para parar{Colors.RESET}
"""
    print(banner)
    sys.stdout.flush()


def log_transaction(action: str, txid: str, amount: float, tenant: str):
    """Log transaction event."""
    timestamp = format_timestamp()
    print(
        f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} "
        f"{Colors.BRIGHT_GREEN}💳{Colors.RESET} "
        f"{Colors.BRIGHT_WHITE}{action}{Colors.RESET} "
        f"{Colors.CYAN}{txid}{Colors.RESET} "
        f"{Colors.BRIGHT_GREEN}R$ {amount:.2f}{Colors.RESET} "
        f"{Colors.BRIGHT_BLACK}({tenant}){Colors.RESET}"
    )
    sys.stdout.flush()


def log_webhook(status: str, url: str, attempt: int):
    """Log webhook event."""
    timestamp = format_timestamp()
    
    if status == 'success':
        icon = "✓"
        color = Colors.GREEN
    else:
        icon = "✗"
        color = Colors.RED
    
    print(
        f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} "
        f"{color}🔔 Webhook{Colors.RESET} "
        f"{color}{icon} {status}{Colors.RESET} "
        f"{Colors.BRIGHT_BLACK}(tentativa {attempt}){Colors.RESET} "
        f"{Colors.CYAN}{url[:50]}...{Colors.RESET}"
    )
    sys.stdout.flush()
