from helper import app

# Import route modules for side-effect registration on shared FunctionApp.
from . import create_weblab_activity
from . import get_weblab_activity
from . import get_treatment_activity
from . import health_activity
from . import list_weblabs_activity
from . import update_allocation_activity
from . import validate_weblab_id_activity

__all__ = ["app"]
