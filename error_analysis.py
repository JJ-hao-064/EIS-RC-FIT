import numpy as np
import matplotlib.pyplot as plt
import os
from error_analysis import calc_zview_errors

# =========================================================
# 保存残差图
# =========================================================
def save_residual_plot(
    freq,
    errors,
    save_path,
    title=""
):

    plt.figure(figsize=(6,5))

    plt.semilogx(
        freq,
        errors["Residual_real"],
        'o-',
        label='Real residual'
    )

    plt.semilogx(
        freq,
        errors["Residual_imag"],
        's-',
        label='Imag residual'
    )

    plt.axhline(
        0,
        color='black',
        linestyle='--'
    )

    plt.xlabel("Frequency (Hz)")

    plt.ylabel("Residual (Ω)")

    plt.title(title)

    plt.legend()

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        save_path,
        dpi=300
    )

    plt.close()


# =========================================================
# 保存 Relative Error 图
# =========================================================
def save_relative_error_plot(
    freq,
    errors,
    save_path,
    title=""
):

    plt.figure(figsize=(6,5))

    plt.semilogx(
        freq,
        errors["Relative_error_percent"],
        'o-'
    )

    plt.xlabel("Frequency (Hz)")

    plt.ylabel("Relative Error (%)")

    plt.title(title)

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        save_path,
        dpi=300
    )

    plt.close()