import math

class CellNeighborhoodAnalyzer:
    """
    Analyzes cell neighborhoods and spatial interactions.
    """
    
    @staticmethod
    def compute_distances(cell_positions_a, cell_positions_b):
        """
        Computes distance metrics between two sets of cells.
        
        Args:
            cell_positions_a (list): List of dicts with 'x' and 'y' for population A.
            cell_positions_b (list): List of dicts with 'x' and 'y' for population B.
            
        Returns:
            dict: Distance statistics.
        """
        if not cell_positions_a or not cell_positions_b:
            return {"mean_distance": 0, "median_distance": 0, "min_distance": 0, "max_distance": 0, "std_distance": 0}
            
        distances = []
        for p1 in cell_positions_a:
            for p2 in cell_positions_b:
                distances.append(math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2))
                
        distances.sort()
        mean_d = sum(distances) / len(distances)
        
        return {
            "mean_distance": mean_d,
            "median_distance": distances[len(distances)//2],
            "min_distance": distances[0],
            "max_distance": distances[-1],
            "std_distance": math.sqrt(sum((x - mean_d)**2 for x in distances) / len(distances))
        }

    @staticmethod
    def immune_infiltration_score(tumor_cells, immune_cells, radius=100.0):
        """
        Computes an immune infiltration score based on proximity.
        
        Args:
            tumor_cells (list): Tumor cell positions.
            immune_cells (list): Immune cell positions.
            radius (float): Proximity radius.
            
        Returns:
            dict: Infiltration metrics.
        """
        in_proximity = 0
        for immune in immune_cells:
            for tumor in tumor_cells:
                dist = math.sqrt((immune['x'] - tumor['x'])**2 + (immune['y'] - tumor['y'])**2)
                if dist <= radius:
                    in_proximity += 1
                    break
                    
        total_immune = len(immune_cells)
        score = in_proximity / total_immune if total_immune > 0 else 0.0
        
        return {
            "infiltration_score": score,
            "immune_cells_in_proximity": in_proximity,
            "total_immune_cells": total_immune,
            "tumor_immune_ratio": len(tumor_cells) / total_immune if total_immune > 0 else float('inf')
        }
        
    @staticmethod
    def neighborhood_composition(cell_positions, cell_types, radius=50.0):
        """
        Analyzes the composition of cell types within neighborhoods.
        
        Args:
            cell_positions (list): Cell coordinates.
            cell_types (list): Corresponding cell types.
            radius (float): Neighborhood radius.
            
        Returns:
            dict: Composition percentages per cell type.
        """
        counts = {}
        for ctype in cell_types:
            counts[ctype] = counts.get(ctype, 0) + 1
            
        total = len(cell_types)
        composition = {k: (v / total * 100.0) for k, v in counts.items()} if total > 0 else {}
        
        return {
            "composition_percentages": composition,
            "total_cells_analyzed": total,
            "radius_used": radius
        }
