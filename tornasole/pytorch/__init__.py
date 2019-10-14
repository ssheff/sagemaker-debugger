from .hook import TornasoleHook
from .collection import Collection, CollectionManager

from .collection import (
    get_collections,
    get_collection,
    load_collections,
    add_to_collection,
    add_to_default_collection,
    reset_collections,
)
from .singleton_utils import get_hook, set_hook
from tornasole import SaveConfig, SaveConfigMode, ReductionConfig
from tornasole import modes
