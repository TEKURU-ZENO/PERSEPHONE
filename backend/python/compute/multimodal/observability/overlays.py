class SegmentationOverlay:
    """
    Generates overlay representations for segmentations and heatmaps for visualization.
    """
    
    @staticmethod
    def create_mask_overlay(segmentation_mask, color_map=None):
        """
        Creates a colorized overlay from a segmentation mask.
        
        Args:
            segmentation_mask (list): 2D array representing segmentation classes.
            color_map (dict, optional): Mapping of class names to RGB colors.
            
        Returns:
            dict: Overlay data configuration.
        """
        default_cmap = {
            'background': [0, 0, 0],
            'tumor': [255, 0, 0],
            'stroma': [0, 255, 0],
            'necrosis': [128, 128, 0]
        }
        cmap = color_map or default_cmap
        
        return {
            "overlay_data": "mock_encoded_image_data",
            "legend": cmap,
            "dimensions": [len(segmentation_mask), len(segmentation_mask[0]) if segmentation_mask else 0],
            "transparency": 0.5
        }
        
    @staticmethod
    def create_heatmap_overlay(heatmap_data, colormap='jet'):
        """
        Creates a heatmap overlay suitable for rendering.
        
        Args:
            heatmap_data (list): 2D array of heatmap intensities.
            colormap (str): Colormap name.
            
        Returns:
            dict: Heatmap overlay configuration.
        """
        return {
            "overlay_data": "mock_encoded_heatmap_data",
            "min_val": 0.0,
            "max_val": 1.0,
            "colormap": colormap
        }
