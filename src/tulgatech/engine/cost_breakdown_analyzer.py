"""
Detailed cost breakdown and analysis
"""
from typing import List, Dict, Tuple


class CostItem:
    """Represents a cost line item"""
    def __init__(self, item_id: str, category: str, description: str):
        self.id = item_id
        self.category = category  # MATERIALS, LABOR, EQUIPMENT, etc.
        self.description = description
        self.quantity = 0.0
        self.unit = ""
        self.unit_cost = 0.0
        self.total_cost = 0.0
        self.markup_percent = 0.0
        self.final_cost = 0.0
    
    def calculate_cost(self):
        """Calculate total and final cost"""
        self.total_cost = self.quantity * self.unit_cost
        markup_amount = self.total_cost * (self.markup_percent / 100)
        self.final_cost = self.total_cost + markup_amount
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "category": self.category,
            "description": self.description,
            "quantity": self.quantity,
            "unit": self.unit,
            "unit_cost": self.unit_cost,
            "total_cost": self.total_cost,
            "markup_percent": self.markup_percent,
            "final_cost": self.final_cost
        }


class CostBreakdownAnalyzer:
    """Analyze and break down project costs"""
    
    def __init__(self):
        self.items: List[CostItem] = []
        self.categories = {}
        self.total_cost = 0.0
        self.contingency_percent = 10.0  # Default 10%
    
    def add_cost_item(self, item: CostItem):
        """Add cost item"""
        item.calculate_cost()
        self.items.append(item)
        
        # Update category totals
        if item.category not in self.categories:
            self.categories[item.category] = 0.0
        self.categories[item.category] += item.final_cost
    
    def analyze_materials(self, material_estimates: List[Dict]) -> Dict:
        """Analyze material costs from estimates"""
        material_total = 0.0
        
        for mat in material_estimates:
            item = CostItem(
                f"MAT_{len(self.items):03d}",
                "MATERIALS",
                mat.get("type", "Material")
            )
            item.quantity = mat.get("quantity", 0)
            item.unit = mat.get("unit", "m2")
            item.unit_cost = mat.get("cost_per_unit", 0)
            item.markup_percent = 15.0  # 15% markup on materials
            
            self.add_cost_item(item)
            material_total += item.final_cost
        
        return {
            "material_items": len(material_estimates),
            "material_total": material_total
        }
    
    def analyze_labor(self, labor_estimate: Dict) -> Dict:
        """Analyze labor costs"""
        avg_worker_daily_cost = 200.0  # TL per day
        
        total_worker_days = labor_estimate.get("total_worker_days", 0)
        
        item = CostItem("LAB_001", "LABOR", "Labor Costs")
        item.quantity = total_worker_days
        item.unit = "worker-days"
        item.unit_cost = avg_worker_daily_cost
        item.markup_percent = 20.0  # 20% markup on labor
        
        self.add_cost_item(item)
        
        return {
            "worker_days": total_worker_days,
            "labor_total": item.final_cost
        }
    
    def analyze_equipment(self, project_duration_days: int) -> Dict:
        """Analyze equipment rental costs"""
        daily_equipment_cost = 100.0  # TL per day
        
        item = CostItem("EQP_001", "EQUIPMENT", "Equipment Rental")
        item.quantity = project_duration_days
        item.unit = "days"
        item.unit_cost = daily_equipment_cost
        item.markup_percent = 10.0
        
        self.add_cost_item(item)
        
        return {
            "duration_days": project_duration_days,
            "equipment_total": item.final_cost
        }
    
    def calculate_contingency(self) -> float:
        """Calculate contingency cost"""
        subtotal = sum(item.final_cost for item in self.items)
        contingency = subtotal * (self.contingency_percent / 100)
        return contingency
    
    def get_total_cost(self) -> float:
        """Get total project cost with contingency"""
        subtotal = sum(item.final_cost for item in self.items)
        contingency = self.calculate_contingency()
        return subtotal + contingency
    
    def get_cost_by_category(self) -> Dict[str, float]:
        """Get cost breakdown by category"""
        breakdown = {}
        for item in self.items:
            if item.category not in breakdown:
                breakdown[item.category] = 0.0
            breakdown[item.category] += item.final_cost
        return breakdown
    
    def get_detailed_breakdown(self) -> Dict:
        """Get detailed cost breakdown"""
        subtotal = sum(item.final_cost for item in self.items)
        contingency = self.calculate_contingency()
        total = subtotal + contingency
        
        return {
            "items": [item.to_dict() for item in self.items],
            "category_totals": self.get_cost_by_category(),
            "subtotal": subtotal,
            "contingency_percent": self.contingency_percent,
            "contingency_amount": contingency,
            "total_cost": total,
            "cost_per_m2": total / 100 if 100 > 0 else 0  # Placeholder area
        }
    
    def generate_summary_report(self) -> str:
        """Generate text summary report"""
        breakdown = self.get_detailed_breakdown()
        
        report = """
PROJECT COST BREAKDOWN REPORT
=============================

COST BY CATEGORY:
"""
        for category, cost in breakdown["category_totals"].items():
            report += f"\n{category}: {cost:,.2f} TL"
        
        report += f"""

SUMMARY:
--------
Subtotal: {breakdown['subtotal']:,.2f} TL
Contingency ({breakdown['contingency_percent']}%): {breakdown['contingency_amount']:,.2f} TL
TOTAL PROJECT COST: {breakdown['total_cost']:,.2f} TL

Cost per m²: {breakdown['cost_per_m2']:,.2f} TL/m²
"""
        
        return report