"""
Radiology file loader module.

Provides loaders for DICOM and NIfTI medical imaging formats.
"""

class RadiologyLoader:
    """Loader class for radiology imaging data formats."""

    @staticmethod
    def load_dicom(filepath: str) -> dict:
        """
        Load metadata and structure from a DICOM file in mock mode.
        
        Args:
            filepath: Path to the DICOM file.
            
        Returns:
            Dictionary containing mock DICOM metadata.
        """
        return {
            "is_mock": True,
            "patient_id": "P-mock-12345",
            "modality": "CT",
            "dimensions": [512, 512],
            "voxel_spacing": [0.976, 0.976, 1.5],
            "manufacturer": "Mock Medical Systems",
            "study_date": "20230101",
            "slice_count": 150
        }

    @staticmethod
    def load_nifti(filepath: str) -> dict:
        """
        Load metadata and structure from a NIfTI file in mock mode.
        
        Args:
            filepath: Path to the NIfTI file.
            
        Returns:
            Dictionary containing mock NIfTI metadata.
        """
        return {
            "is_mock": True,
            "dimensions": 3,
            "voxel_spacing": [1.0, 1.0, 1.0],
            "affine_matrix": [
                [1.0, 0.0, 0.0, -128.0],
                [0.0, 1.0, 0.0, -128.0],
                [0.0, 0.0, 1.0, -128.0],
                [0.0, 0.0, 0.0, 1.0]
            ],
            "data_shape": [256, 256, 128]
        }
