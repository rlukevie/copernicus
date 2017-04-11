import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

from copernicus_tools.settings import *


class PreviewCreator:
    def __init__(self, product, preview_factor=0.3):
        self.product_to_analyze = product
        self._filename = product.title[:-1]+'.png'
        self.preview_output_path = os.path.join(product_lab_output_directory,
                                                self._filename)
        self.preview_factor = preview_factor

    def run(self):
        band_r_file = self.product_to_analyze.images_60m['B04']
        band_g_file = self.product_to_analyze.images_60m['B03']
        band_b_file = self.product_to_analyze.images_60m['B02']
        band_r_path = os.path.join(os.path.join(product_data_directory,
                                   self.product_to_analyze.title),
                                   band_r_file)
        band_g_path = os.path.join(os.path.join(product_data_directory,
                                   self.product_to_analyze.title),
                                   band_g_file)
        band_b_path = os.path.join(os.path.join(product_data_directory,
                                   self.product_to_analyze.title),
                                   band_b_file)
        dataset_r = rasterio.open(band_r_path)
        dataset_g = rasterio.open(band_g_path)
        dataset_b = rasterio.open(band_b_path)

        crs = dataset_r.crs

        # TODO: refactor reprojection (all 3 bands together)

        # band r
        band_r = dataset_r.read(1)*8
        new_band_r = np.empty(shape=(
            int(round(band_r.shape[0] * self.preview_factor)),
            int(round(band_r.shape[1] * self.preview_factor))))
        aff = dataset_r.transform
        newaff = rasterio.Affine(aff.a / self.preview_factor, aff.b, aff.c,
                                 aff.d, aff.e / self.preview_factor, aff.f)
        reproject(
            band_r, new_band_r,
            src_transform=aff,
            dst_transform=newaff,
            src_crs=crs,
            dst_crs=crs,
            resample=Resampling.bilinear)
        new_band_r = new_band_r.astype('uint16')

        # band g
        band_g = dataset_g.read(1)*8
        new_band_g = np.empty(shape=(
            int(round(band_g.shape[0] * self.preview_factor)),
            int(round(band_g.shape[1] * self.preview_factor))))
        aff = dataset_g.transform
        newaff = rasterio.Affine(aff.a / self.preview_factor, aff.b, aff.c,
                                 aff.d, aff.e / self.preview_factor, aff.f)
        reproject(
            band_g, new_band_g,
            src_transform=aff,
            dst_transform=newaff,
            src_crs=crs,
            dst_crs=crs,
            resample=Resampling.bilinear)
        new_band_g = new_band_g.astype('uint16')

        #band b
        band_b = dataset_b.read(1)*8
        new_band_b = np.empty(shape=(
            int(round(band_b.shape[0] * self.preview_factor)),
            int(round(band_b.shape[1] * self.preview_factor))))
        aff = dataset_b.transform
        newaff = rasterio.Affine(aff.a / self.preview_factor, aff.b, aff.c,
                                 aff.d, aff.e / self.preview_factor, aff.f)
        reproject(
            band_b, new_band_b,
            src_transform=aff,
            dst_transform=newaff,
            src_crs=crs,
            dst_crs=crs,
            resample=Resampling.bilinear)
        new_band_b = new_band_b.astype('uint16')

        transform = dataset_r.transform

        preview_file = rasterio.open(self.preview_output_path, 'w',
                                     driver='png',
                                     height=band_r.shape[0],
                                     width=band_r.shape[1],
                                     count=3,
                                     dtype=band_r.dtype,
                                     crs=crs,
                                     transform=transform
                                     )
        preview_file.write(new_band_r, 1)
        preview_file.write(new_band_g, 2)
        preview_file.write(new_band_b, 3)
        preview_file.close()

        self.product_to_analyze.lab_history['preview'] = True
        self.product_to_analyze.preview_image_path = self.preview_output_path
