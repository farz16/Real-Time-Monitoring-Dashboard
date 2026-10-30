"""
Kumbh-Drishti AI: Dynamic Evacuation & Emergency Routing Engine
Computes optimal non-choked evacuation pathways and creates rapid Ambulance Green Corridors.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
from PIL import Image


class EvacuationRoutingEngine:
    def __init__(self):
        # Define Kumbh Mela Sector Topology
        self.sectors = {
            "G1": {"name": "Triveni Sangam Ghat (Main)", "x": 0.5, "y": 0.85, "type": "ghat"},
            "G2": {"name": "Ram Ghat (West)", "x": 0.2, "y": 0.75, "type": "ghat"},
            "G3": {"name": "Dashashwamedh Ghat (East)", "x": 0.8, "y": 0.75, "type": "ghat"},
            "B1": {"name": "Shahi Bridge (Choke Point)", "x": 0.5, "y": 0.60, "type": "bridge"},
            "S1": {"name": "Sector 4 Holding Area", "x": 0.25, "y": 0.45, "type": "sector"},
            "S2": {"name": "Sector 6 Open Ground", "x": 0.75, "y": 0.45, "type": "sector"},
            "EX1": {"name": "Main Exit 1 (Railway Station)", "x": 0.2, "y": 0.15, "type": "exit"},
            "EX2": {"name": "Bypass Exit 2 (Ring Road)", "x": 0.5, "y": 0.15, "type": "exit"},
            "EX3": {"name": "Emergency Exit 3 (Hospital Corridor)", "x": 0.8, "y": 0.15, "type": "exit"}
        }
        
        # Connections between sectors
        self.edges = [
            ("G1", "B1"), ("G2", "S1"), ("G3", "S2"),
            ("B1", "S1"), ("B1", "S2"), ("B1", "EX2"),
            ("S1", "EX1"), ("S1", "EX2"),
            ("S2", "EX2"), ("S2", "EX3")
        ]

    def compute_optimal_routes(self, sector_densities):
        """
        Computes dynamic diversion paths based on current real-time density per sector.
        - Green paths: Safe (< 2.5 p/m²)
        - Yellow paths: Moderately congested (2.5 - 4.0 p/m²)
        - Red / Blocked paths: Critical stampede hazard (> 4.0 p/m²)
        """
        # Determine blocked / critical nodes
        blocked_nodes = set()
        for sec_id, density in sector_densities.items():
            if density >= 4.2:
                blocked_nodes.add(sec_id)
                
        # Primary diversion recommendation for Sangam Ghat (G1)
        if "B1" in blocked_nodes or "G1" in blocked_nodes:
            evacuation_strategy = {
                "status": "EMERGENCY DIVERSION ACTIVE",
                "blocked_zones": ["Shahi Bridge (B1)", "Triveni Sangam Gate (G1)"],
                "recommended_pedestrian_path": ["G1 -> G2 (Ram Ghat) -> S1 -> Exit 1 (Station Road)"],
                "recommended_bypass_path": ["G3 (East) -> S2 -> Exit 3 (Ring Road)"],
                "ambulance_green_corridor": ["Hospital Corridor -> S2 -> G3"],
                "action_command": "CLOSE Shahi Bridge entry gates. Divert incoming flow 50% West and 50% East."
            }
        else:
            evacuation_strategy = {
                "status": "STANDARD ROUTING (NORMAL FLOW)",
                "blocked_zones": [],
                "recommended_pedestrian_path": ["G1 -> B1 -> Exit 2 (Main)"],
                "recommended_bypass_path": ["G2 -> S1 -> Exit 1", "G3 -> S2 -> Exit 3"],
                "ambulance_green_corridor": ["Exit 3 -> S2 -> B1 -> G1"],
                "action_command": "Maintain normal two-way regulated crowd movement."
            }
            
        return evacuation_strategy

    def render_schematic_map(self, sector_densities, high_risk_sector="G1"):
        """
        Draws a high-contrast tactical command map of the Kumbh Mela layout with live zone status.
        """
        fig, ax = plt.subplots(figsize=(10, 6.5), facecolor='#0f172a')
        ax.set_facecolor('#0f172a')
        
        # Plot edges
        for (u, v) in self.edges:
            x_vals = [self.sectors[u]["x"], self.sectors[v]["x"]]
            y_vals = [self.sectors[u]["y"], self.sectors[v]["y"]]
            
            # Check edge status
            u_dense = sector_densities.get(u, 1.5)
            v_dense = sector_densities.get(v, 1.5)
            max_dense = max(u_dense, v_dense)
            
            if max_dense >= 4.2:
                edge_color = '#ef4444' # Red (Blocked)
                line_style = '--'
                line_width = 3.0
            elif max_dense >= 3.0:
                edge_color = '#f59e0b' # Yellow
                line_style = '-'
                line_width = 2.5
            else:
                edge_color = '#22c55e' # Green
                line_style = '-'
                line_width = 2.0
                
            ax.plot(x_vals, y_vals, color=edge_color, linestyle=line_style, linewidth=line_width, zorder=1)

        # Plot nodes (Sectors)
        for sec_id, data in self.sectors.items():
            density = sector_densities.get(sec_id, 1.5)
            if density >= 4.2:
                node_color = '#ef4444' # Red Alert
                border_color = '#fca5a5'
            elif density >= 3.0:
                node_color = '#f59e0b' # Amber Warning
                border_color = '#fde68a'
            else:
                node_color = '#10b981' # Green Normal
                border_color = '#a7f3d0'
                
            circle = plt.Circle((data["x"], data["y"]), 0.045, color=node_color, ec=border_color, lw=2.5, zorder=3)
            ax.add_patch(circle)
            
            # Node labels
            ax.text(data["x"], data["y"], sec_id, color='white', weight='bold', 
                    fontsize=10, ha='center', va='center', zorder=4)
            
            # Subtitle label with density
            label_text = f"{data['name']}\n[{density:.1f} p/m²]"
            ax.text(data["x"], data["y"] - 0.08, label_text, color='#e2e8f0', 
                    fontsize=8, ha='center', va='top', weight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", fc="#1e293b", ec="#334155", alpha=0.9))

        # Title and styling
        ax.set_title("Kumbh-Drishti AI: Real-Time Tactical Evacuation & Zone Congestion Map", 
                     color='#38bdf8', fontsize=13, weight='bold', pad=15)
        ax.set_xlim(0.05, 0.95)
        ax.set_ylim(0.02, 0.98)
        ax.axis('off')
        
        # Save to buffer
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=130, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        buf.seek(0)
        
        return Image.open(buf)
