from backend.python.compute.multimodal.pathology.wsi_loader import WSILoader
from backend.python.compute.multimodal.pathology.tiler import SlideTiler

class PatchDataset:
    """
    Clinical/Scientific Purpose:
    Provides a framework-agnostic dataset interface for pathology patches. 
    It streams standardized inputs and labels to training/inference loops, integrating 
    clinical metadata (like patient labels) with morphological data.
    """

    def __init__(self, patches: list, labels: list = None, transform=None):
        self.patches = patches
        self.labels = labels
        self.transform = transform

    def __len__(self) -> int:
        return len(self.patches)

    def __getitem__(self, idx: int) -> dict:
        """
        Retrieves patch data and metadata at a given index.
        """
        patch = self.patches[idx]
        
        # Apply mock transform if callable
        if self.transform is not None and callable(self.transform):
            patch = self.transform(patch)
            
        return {
            "patch_data": patch,
            "label": self.labels[idx] if self.labels else None,
            "index": idx
        }

    @classmethod
    def from_slide(cls, slide_path: str, patch_size: int = 256):
        """
        Composes WSILoader and SlideTiler to create a dataset directly from a whole slide image.
        """
        slide_metadata = WSILoader.load_slide(slide_path)
        coordinates = SlideTiler.tile_slide(slide_metadata, patch_size=patch_size)
        patches = SlideTiler.extract_patches(slide_metadata, coordinates)
        return cls(patches=patches)
