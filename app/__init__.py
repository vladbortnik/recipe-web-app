from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import logging
from rich.logging import RichHandler
from rich.console import Console
# from flask_debugtoolbar import DebugToolbarExtension  # Import the DebugToolbarExtension

##########################################################################################
################     STANDARD     SETUP       ############################################ 
##########################################################################################

# # Create a Console instance for rich text
# console = Console()

# # Configure the logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(message)s",
#     datefmt="[%X]",
#     handlers=[RichHandler(console=console)]
# )

# # Create a logger instance
# logger = logging.getLogger("rich.console")
# # logger = logging.getLogger("rich.console").setLevel(logging.DEBUG)

# # Example usage within __init__.py (optional)
# logger.debug("=== RICH.LOGGER INITIATED ===")


##########################################################################################
################     COLOR OUTPUT SETUP for Docker      ##################################
##########################################################################################


# # Create a Console instance for rich text with force_terminal=True
# console = Console(force_terminal=True)

# # Create a RichHandler instance with rich_tracebacks=True and force enable color
# rich_handler = RichHandler(
#     console=console, 
#     rich_tracebacks=True,
#     markup=True,  # Ensure markup is enabled
#     log_time_format="[%X]",
#     rich_tracebacks=True
# )

# # Configure the logging with RichHandler
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(message)s",
#     handlers=[rich_handler]
# )

# # Create a logger instance
# logger = logging.getLogger("rich.console")

# # Example usage
# logger.debug("[bold red]This is red and bold[/bold red]")


##########################################################################################
#######################   LOGGER: to_File && to_Console   ################################
##########################################################################################

# Create a Console instance for rich text
console = Console()

# Create handlers
console_handler = RichHandler(console=console)
file_handler = logging.FileHandler('app.log')  # Log to a file named 'app.log'

# Set log level for handlers
console_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# Create a custom formatter for the file handler if desired
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

# Configure the logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[console_handler, file_handler]
)

# Create a logger instance
logger = logging.getLogger("rich.console & rich.file")

# Example usage within __init__.py (optional)
logger.debug("=== FILE && CONSOLE `RICH.LOGGER` INITIATED ===")


##########################################################################################
##########################################################################################
##########################################################################################




# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
# toolbar = DebugToolbarExtension()  # Create toolbar instance

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message_category = "info"
    # toolbar.init_app(app)  # Initialize the toolbar

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        # Import routes
        from . import routes

    return app
