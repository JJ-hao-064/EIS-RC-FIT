# EIS Second-Order RC Fitting and ZView-Style Error Analysis

This project batch-fits electrochemical impedance spectroscopy (EIS) data using a second-order RC equivalent circuit and exports ZView-style error metrics, fitted parameters, point-wise residuals, and figures.

## Features

- Batch processing by temperature folder and SOC folder
- Supports `.csv`, `.xlsx`, and `.xls` input files
- Fits the equivalent circuit:

```text
R0-p(R1,C1)-p(R2,C2)
```

- Uses modulus weighting during fitting
- Calculates:
  - Chi-square
  - Reduced chi-square
  - Sum of squares
  - RMSE
  - Weighted RMSE
  - Mean relative error (%)
  - Maximum relative error (%)
  - Real and imaginary residuals
- Exports an Excel report and PNG figures

## Project Structure

```text
.
├── FIT.py                 # Main batch fitting script
├── error_analysis.py      # Error metrics and plotting utilities
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Installation

Python 3.10 or later is recommended.

Create a Conda environment:

```bash
conda create -n eis-fit python=3.10
conda activate eis-fit
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the fitting script with the root data directory:

```bash
python FIT.py "path/to/root_dir"
```

By default, outputs are saved to:

```text
path/to/root_dir/EIS_ERROR_ANALYSIS/
```

To specify a custom output directory:

```bash
python FIT.py "path/to/root_dir" --output-dir "path/to/output_dir"
```

To process only selected temperature or SOC folders:

```bash
python FIT.py "path/to/root_dir" \
  --temperatures TJ-EIS-C4-T25 TJ-EIS-C4-T35 \
  --socs 15SOC 50SOC 100SOC
```

## Outputs

The script creates:

```text
EIS_ERROR_ANALYSIS/
├── second_order_rc_zview_error_analysis.xlsx
└── figures/
    ├── <temperature>_Nyquist.png
    ├── <temperature>_Residual_Real.png
    ├── <temperature>_Residual_Imag.png
    └── <temperature>_Relative_Error.png
```

The Excel workbook contains two sheets:

| Sheet | Description |
|---|---|
| `fit_summary` | Fitted parameters and aggregate error metrics for each temperature/SOC spectrum |
| `point_errors` | Point-wise fitted values, residuals, absolute errors, and relative errors |

## Main Parameters

The main model settings are defined near the top of `FIT.py`:

```python
CIRCUIT = "R0-p(R1,C1)-p(R2,C2)"
INITIAL_GUESS = [0.001, 0.001, 1.0, 0.001, 10.0]
LOWER_BOUNDS = [0, 0, 1e-8, 0, 1e-8]
UPPER_BOUNDS = [0.1, 0.1, 1e6, 0.1, 1e6]
```

Adjust these values if your battery system, units, or impedance range differs.

## License

MIT License