"""
Material estimation from construction elements
"""
from typing import List, Dict, Tuple

Point2D = Tuple[float, float]


class MaterialEstimate:
    """Represents material quantity estimate"""
    def __init__(self, material_type: str):
        self.type = material_type  # PAINT, FLOORING, PLASTER, etc.
        self.quantity = 0.0
        self.unit = ""  # m2, m3, kg, etc.
        self.cost_per_unit = 0.0
        self.total_cost = 0.0
        self.waste_factor = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "type": self.type,
            "quantity": self.quantity,
            "unit": self.unit,
            "cost_per_unit": self.cost_per_unit,
            "total_cost": self.total_cost,
            "waste_factor": self.waste_factor
        }


class MaterialEstimator:
    """Estimate material quantities and costs"""
    
    def __init__(self):
        self.estimates: List[MaterialEstimate] = []
        
        # Default unit costs (Turkish market approximation)
        self.unit_costs = {
            "paint": 15.0,  # TL/m2
            "flooring": 50.0,  # TL/m2
            "plaster": 25.0,  # TL/m2
            "concrete": 400.0,  # TL/m3
            "tiles": 30.0,  # TL/m2
        }
    
    def estimate_paint(self, walls: List[Dict], 
                      wall_thickness_m: float = 0.25) -> MaterialEstimate:
        """Estimate paint/coating needed"""
        
        total_wall_length = sum(w.get("length_m", 0) for w in walls)
        wall_height_m = 3.0  # Standard wall height
        
        # Calculate wall area (minus openings)
        wall_area = total_wall_length * wall_height_m
        
        # Subtract window areas (rough estimate)
        window_area_deduction = wall_area * 0.15  # 15% for windows
        net_wall_area = wall_area - window_area_deduction
        
        # Add waste factor
        waste_factor = 0.15
        paint_area = net_wall_area * (1 + waste_factor)
        
        estimate = MaterialEstimate("PAINT")
        estimate.quantity = paint_area
        estimate.unit = "m2"
        estimate.cost_per_unit = self.unit_costs["paint"]
        estimate.waste_factor = waste_factor
        estimate.total_cost = paint_area * estimate.cost_per_unit
        
        self.estimates.append(estimate)
        return estimate
    
    def estimate_flooring(self, rooms: List[Dict],
                         waste_factor: float = 0.10) -> MaterialEstimate:
        """Estimate flooring material needed"""
        
        total_room_area = sum(r.get("area_m2", 0) for r in rooms)
        
        # Add waste factor
        flooring_area = total_room_area * (1 + waste_factor)
        
        estimate = MaterialEstimate("FLOORING")
        estimate.quantity = flooring_area
        estimate.unit = "m2"
        estimate.cost_per_unit = self.unit_costs["flooring"]
        estimate.waste_factor = waste_factor
        estimate.total_cost = flooring_area * estimate.cost_per_unit
        
        self.estimates.append(estimate)
        return estimate
    
    def estimate_plaster(self, walls: List[Dict],
                        plaster_thickness_m: float = 0.02) -> MaterialEstimate:
        """Estimate plaster material needed"""
        
        total_wall_length = sum(w.get("length_m", 0) for w in walls)
        wall_height_m = 3.0
        
        # Calculate plaster volume
        plaster_area = total_wall_length * wall_height_m
        plaster_volume = plaster_area * plaster_thickness_m  # m3
        
        # Plaster density: ~1500 kg/m3
        plaster_weight = plaster_volume * 1500
        
        estimate = MaterialEstimate("PLASTER")
        estimate.quantity = plaster_weight
        estimate.unit = "kg"
        estimate.cost_per_unit = self.unit_costs["plaster"]
        estimate.waste_factor = 0.05
        estimate.total_cost = plaster_weight * (estimate.cost_per_unit / 50)  # kg to cost
        
        self.estimates.append(estimate)
        return estimate
    
    def estimate_tiles(self, rooms: List[Dict],
                      tile_coverage_ratio: float = 0.5) -> MaterialEstimate:
        """Estimate tile material needed"""
        
        total_area = sum(r.get("area_m2", 0) for r in rooms)
        
        # Only tile 50% of rooms (bathrooms, kitchens)
        tiled_area = total_area * tile_coverage_ratio
        
        # Add waste
        waste_factor = 0.15
        tile_area = tiled_area * (1 + waste_factor)
        
        estimate = MaterialEstimate("TILES")
        estimate.quantity = tile_area
        estimate.unit = "m2"
        estimate.cost_per_unit = self.unit_costs["tiles"]
        estimate.waste_factor = waste_factor
        estimate.total_cost = tile_area * estimate.cost_per_unit
        
        self.estimates.append(estimate)
        return estimate
    
    def get_total_cost(self) -> float:
        """Get total estimated cost"""
        return sum(e.total_cost for e in self.estimates)
    
    def get_cost_by_type(self, material_type: str) -> float:
        """Get cost for specific material type"""
        return sum(e.total_cost for e in self.estimates 
                  if e.type == material_type)
    
    def get_all_estimates(self) -> List[Dict]:
        """Get all estimates as dictionaries"""
        return [e.to_dict() for e in self.estimates]
    
    def generate_summary(self) -> Dict:
        """Generate cost summary"""
        total_cost = self.get_total_cost()
        
        summary = {
            "total_estimated_cost": total_cost,
            "material_count": len(self.estimates),
            "materials": self.get_all_estimates(),
            "cost_breakdown": {
                e.type: self.get_cost_by_type(e.type)
                for e in self.estimates
            }
        }
        
        return summary