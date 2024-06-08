# RGB TGI Extraction

This script extracts triangular greenness index (TGI) values from red-green-blue (RGB) imagery.

## Inputs
The script takes a directory path containing plot clipped TIF images

## Outputs
The script outputs a CSV with TGI values for each plot. The reported TGI value is a plot average.

## Arguments and Flags

* **Positional Arguments:** 
    * **Directory containing plot clipped TIFF images:** 'dir'
    
* **Optional Arguments:**
    * **Output directory:** '-o', '--outdir', default='tgi_extraction_out'
 
* **Required Arguments:**
    * **Season fieldbook:** '-f', '--fieldbook'
