#!/usr/bin/env python3
"""
Land Surface Temperature Preprocessing
Processes Landsat data exported from Google Earth Engine
"""

import os
import numpy as np
import rasterio
from rasterio.plot import show
from pathlib import Path
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LSTPreprocessor:
    """Preprocess Landsat thermal data"""
    
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def clip_to_study_area(self, image_path, mask_path, output_path):
        """Clip raster to study area"""
        with rasterio.open(image_path) as src:
            data = src.read()
            profile = src.profile
            
        with rasterio.open(mask_path) as mask_src:
            mask_data = mask_src.read(1)
            
        # Apply mask
        masked_data = np.where(mask_data > 0, data, np.nan)
        
        # Write output
        profile.update(dtype=rasterio.float32)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(masked_data.astype(np.float32))
            
        logger.info(f"Clipped: {output_path}")
        
    def apply_median_filter(self, image_path, output_path, kernel_size=3):
        """Apply median filter to reduce noise"""
        from scipy.ndimage import median_filter
        
        with rasterio.open(image_path) as src:
            data = src.read(1)
            profile = src.profile
            
        # Apply median filter
        filtered = median_filter(data, size=kernel_size)
        
        # Write output
        profile.update(dtype=rasterio.float32)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(filtered.astype(np.float32), 1)
            
        logger.info(f"Filtered: {output_path}")
        
    def reproject_to_utm(self, image_path, output_path, target_crs='EPSG:32644'):
        """Reproject to UTM Zone 44N"""
        from rasterio.warp import calculate_default_transform, reproject, Resampling
        
        with rasterio.open(image_path) as src:
            transform, width, height = calculate_default_transform(
                src.crs, target_crs, src.width, src.height, *src.bounds
            )
            
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': target_crs,
                'transform': transform,
                'width': width,
                'height': height
            })
            
            with rasterio.open(output_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        rasterio.band(src, i),
                        rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=target_crs,
                        resampling=Resampling.bilinear
                    )
                    
        logger.info(f"Reprojected to {target_crs}: {output_path}")
        
    def calculate_statistics(self, image_path):
        """Calculate and log statistics"""
        with rasterio.open(image_path) as src:
            data = src.read(1)
            valid_data = data[~np.isnan(data)]
            
            stats = {
                'min': np.nanmin(data),
                'max': np.nanmax(data),
                'mean': np.nanmean(data),
                'std': np.nanstd(data),
                'count': np.sum(~np.isnan(data))
            }
            
            logger.info(f"Statistics for {Path(image_path).name}:")
            for key, value in stats.items():
                logger.info(f"  {key}: {value:.2f}")
                
            return stats
            
    def process_all(self):
        """Process all files in input directory"""
        logger.info(f"Processing files in {self.input_dir}")
        
        for file in self.input_dir.glob('*.tif'):
            logger.info(f"Processing: {file.name}")
            
            # Steps
            output_file = self.output_dir / file.name
            self.apply_median_filter(str(file), str(output_file))
            self.calculate_statistics(str(output_file))
            
        logger.info("Preprocessing complete!")


def main():
    parser = argparse.ArgumentParser(
        description='Preprocess Landsat thermal data'
    )
    parser.add_argument('--input', required=True, help='Input directory')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--kernel', type=int, default=3, help='Filter kernel size')
    
    args = parser.parse_args()
    
    processor = LSTPreprocessor(args.input, args.output)
    processor.process_all()


if __name__ == '__main__':
    main()
