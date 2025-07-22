from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class GameState:
    selected_unit: Optional[object] = None
    selected_city: Optional[object] = None
    status_msg: str = ""
    valid_moves: List[Tuple[int, int]] = field(default_factory=list)
    path_map: Dict[Tuple[int, int], List[Tuple[int, int]]] = field(default_factory=dict)
    # Add more gameplay state fields as needed (no GUI rects)
