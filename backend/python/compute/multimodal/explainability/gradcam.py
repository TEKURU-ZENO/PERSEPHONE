class GradCAMGenerator:
    """
    Generates Gradient-weighted Class Activation Maps (Grad-CAM) to explain model predictions.
    """
    
    @staticmethod
    def generate_heatmap(patch_data, model_output=None, target_class='tumor'):
        """
        Generates a Grad-CAM heatmap for a given image patch.
        
        Args:
            patch_data (dict): Data for the image patch.
            model_output (dict, optional): Outputs from the model.
            target_class (str): The class to generate the heatmap for.
            
        Returns:
            dict: Heatmap data and statistics.
        """
        # Mock 2D heatmap generation
        size = 16
        heatmap = [[(i + j) / (2.0 * size) for j in range(size)] for i in range(size)]
        
        return {
            "heatmap": heatmap,
            "target_class": target_class,
            "activation_stats": {
                "mean": 0.5,
                "max": 1.0,
                "coverage_fraction": 0.75
            },
            "resolution": [size, size]
        }
        
    @staticmethod
    def batch_heatmaps(patches, target_class='tumor'):
        """
        Generates Grad-CAM heatmaps for a batch of patches.
        
        Args:
            patches (list): List of patch data.
            target_class (str): Target class.
            
        Returns:
            list: List of heatmap dictionaries.
        """
        return [GradCAMGenerator.generate_heatmap(p, target_class=target_class) for p in patches]
