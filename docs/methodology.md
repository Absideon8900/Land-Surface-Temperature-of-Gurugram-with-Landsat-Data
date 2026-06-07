# Methodology: Land Surface Temperature Analysis

## 1. Study Area

### Geographic Location
- **Region**: Gurugram (Gurgaon), Haryana, India
- **Coordinates**: 
  - Latitude: 28.4°N to 28.9°N
  - Longitude: 77.0°E to 77.7°E
- **Area**: ~1,255 km²
- **Characteristics**: Rapidly urbanizing city; capital of Haryana; part of Delhi metropolitan area

### Administrative Boundaries
Gurugram district includes:
- Municipal Corporation of Gurugram (MCG)
- Surrounding rural and semi-rural areas

## 2. Data Collection

### Primary Data Source: Google Earth Engine
- **Platform**: Google Earth Engine (https://earthengine.google.com/)
- **Advantages**:
  - Access to Landsat archive (30+ years)
  - Cloud computing for large-scale processing
  - Pre-processed, analysis-ready data
  - No data download limitations

### Satellite Sensors

#### Landsat 9
- **Launch Date**: September 27, 2021
- **Operational Since**: December 2021
- **Orbital Revisit**: 16 days
- **Spatial Resolution**: 30m (thermal bands)

#### Landsat 8
- **Launch Date**: February 11, 2013
- **Operational Since**: April 2013
- **Orbital Revisit**: 16 days
- **Spatial Resolution**: 30m (thermal bands)

### Thermal Bands Used

| Band | Designation | Wavelength | Application |
|------|-------------|------------|-------------|
| Band 10 | TIRS1 | 10.6-11.2 µm | Primary LST calculation |
| Band 11 | TIRS2 | 11.5-12.5 µm | Quality assurance |

### Data Selection Criteria
1. **Cloud Cover**: < 5% (quality threshold)
2. **Scene Quality**: QA_PIXEL < 100 (minimal artifacts)
3. **Date Range**: Full year (captures seasonal variation)
4. **Temporal Coverage**: 16-day repeat cycle

## 3. Preprocessing Steps

### 3.1 Data Collection from GEE
```
Landsat Collection 2, Level 2
↓
Filter by geographic bounds (Gurugram)
↓
Filter by temporal range (2024-01-01 to 2024-12-31)
↓
Filter by cloud cover (< 5%)
↓
Merge Landsat 8 & 9 collections
↓
Surface Temperature dataset
```

### 3.2 Quality Control
- Remove images with QA flags indicating:
  - Cloud cover (bit 3-4)
  - Cloud shadow (bit 5)
  - Snow (bit 6)
  - Water (bit 7)

### 3.3 Radiometric Correction
- USGS Collection 2 Level 2 data already includes:
  - Radiometric calibration
  - Atmospheric correction
  - Geometric registration (±15m RMS)

### 3.4 Noise Reduction
- **Method**: Median filter (3×3 kernel)
- **Purpose**: Reduce speckle while preserving edges
- **Implementation**: SciPy `ndimage.median_filter`

### 3.5 Reprojection
- **Target CRS**: UTM Zone 44N (EPSG:32644)
- **Method**: Bilinear resampling
- **Resolution**: 30m × 30m pixels

## 4. Land Surface Temperature Calculation

### 4.1 Temperature Derivation

The LST retrieval follows the standard USGS methodology:

#### Step 1: Extract Thermal Band
```
B10_DN = Digital Number from Band 10
```

#### Step 2: Radiometric Calibration
```
Lλ = (ML × B10_DN + AL)
Where:
  ML = Radiance Multiplicative Rescaling Coefficient (0.0003342)
  AL = Radiance Additive Rescaling Coefficient (0.1)
```

#### Step 3: Brightness Temperature Calculation
```
BT = K2 / ln((K1 / Lλ) + 1)
Where:
  K1 = 774.8853 W/(m² × sr × µm) [Landsat 9]
  K2 = 480.8883 K [Landsat 9]
```

#### Step 4: NDVI Calculation
```
NDVI = (NIR - Red) / (NIR + Red)
Where:
  NIR = Band 5 (Near Infrared)
  Red = Band 4 (Red)
```

#### Step 5: Pixel Proportion of Vegetation
```
Pv = ((NDVI - NDVImin) / (NDVImax - NDVImin))²
```

#### Step 6: Land Emissivity
```
ε = 0.004 × Pv + 0.986
```

#### Step 7: LST Calculation
```
LST = BT / (1 + (λ × BT / ρ) × ln(ε))

Where:
  λ = Wavelength (10.9 µm for Band 10)
  ρ = Boltzmann constant × wavelength / Planck constant
    = 1.4388 × 10⁻² m·K
  BT = Brightness Temperature (K)
```

#### Step 8: Convert to Celsius
```
LST_C = LST_K - 273.15
```

### 4.2 Uncertainty Estimation

**Factors Affecting LST Accuracy:**
- Atmospheric transmission errors: ±1-2 K
- Emissivity estimation: ±0.5-1.5 K
- Calibration uncertainty: ±0.3 K
- **Total Uncertainty**: ±2-3 K

## 5. Ancillary Analysis

### 5.1 NDVI Classification
```
NDVI Range    | Interpretation
< -0.1        | Water/Built-up
-0.1 to 0.3   | Urban/Low vegetation
0.3 to 0.6    | Moderate vegetation
> 0.6         | Dense forest/crops
```

### 5.2 Temperature Classification
```
Class | Temperature Range | Category
1     | < 15°C           | Very Cool
2     | 15-20°C          | Cool
3     | 20-25°C          | Moderate
4     | 25-30°C          | Warm
5     | 30-35°C          | Hot
6     | > 35°C           | Very Hot
```

## 6. Post-Processing

### 6.1 Spatial Smoothing
- **Method**: 3×3 moving median window
- **Iterations**: 1-2 passes
- **Purpose**: Reduce noise while preserving features

### 6.2 Statistical Analysis
- Calculate mean, standard deviation, min, max
- Generate histograms and distribution plots
- Identify outliers and anomalies

### 6.3 Zoning Analysis
- Aggregate pixels into meaningful zones
- Calculate zone statistics
- Identify urban heat islands

## 7. Visualization Outputs

### 7.1 Thematic Maps (QGIS)
1. **LST Gradient Map**
   - Color ramp: Blue (cool) → Red (hot)
   - Scale: 15-45°C

2. **NDVI Map**
   - Color ramp: Red (water) → Green (vegetation)
   - Scale: -1 to 1

3. **Temperature Classification Map**
   - 6-class categorization
   - Distinct colors for each class

4. **Urban Heat Island Map**
   - Temperature anomaly from mean
   - Identify hotspot zones

### 7.2 Statistical Plots
- Histograms of LST distribution
- Scatter plots (NDVI vs LST)
- Time series plots (seasonal trends)
- Profile plots (transects)

### 7.3 Cartographic Design
- Scale bar and north arrow
- Legend with detailed descriptions
- Title, date, and source attribution
- Projection information

## 8. Validation & Quality Assurance

### 8.1 Internal Validation
- Compare with adjacent imagery
- Check for artifacts and anomalies
- Verify statistical ranges
- Cross-check with ancillary data

### 8.2 External Validation
- Compare with in-situ measurements (if available)
- Validate with other LST products (MODIS, etc.)
- Accuracy assessment using validation points

### 8.3 Metadata Documentation
- Record all processing parameters
- Document data quality flags
- Note any corrections or adjustments
- Create reproducible processing chain

## 9. Limitations & Uncertainties

| Issue | Impact | Mitigation |
|-------|--------|-----------|
| Cloud cover | Data gaps | Use cloud-free scenes |
| Atmospheric effects | ±1-2 K error | Use L2 corrected data |
| Emissivity variation | ±0.5-1.5 K | Use NDVI-based estimation |
| Thermal lag | Temporal shift | Use consistent acquisition time |
| Sensor differences | L8 vs L9 data | Cross-calibrate before merging |

## 10. References

1. USGS Landsat Collection 2, Level-2 Data
   - https://www.usgs.gov/landsat/landsat-collection-2

2. Barsi, J. A., et al. (2014). "Landsat-8 Thermal Infrared Sensor Radiometric Calibration and Characterization"

3. Li, Z. L., et al. (2013). "Satellite-based land surface temperature estimation"

4. Roy, D. P., et al. (2014). "Landsat-8: Science and product vision for terrestrial global change research"

5. Gorelick, N., et al. (2017). "Google Earth Engine: Planetary-scale geospatial analysis for everyone"
