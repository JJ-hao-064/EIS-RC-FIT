import numpy as np
import matplotlib.pyplot as plt
import os


# =========================================================
# ZView 风格误差分析
# =========================================================
def calc_zview_errors(freq, Z, Z_fit, model):

    residual_real = Z.real - Z_fit.real
    residual_imag = Z.imag - Z_fit.imag

    residual_complex = Z - Z_fit

    modulus = np.abs(Z)

    # ZView modulus weighting
    weight = 1 / np.maximum(modulus**2, 1e-30)

    # =====================================================
    # Chi-square
    # =====================================================
    chi_square = np.sum(
        weight * (
            residual_real**2 +
            residual_imag**2
        )
    )

    dof = max(len(Z)*2 - len(model.parameters_), 1)

    reduced_chi_square = chi_square / dof

    # =====================================================
    # Sum of Squares
    # =====================================================
    sum_of_squares = np.sum(
        residual_real**2 +
        residual_imag**2
    )

    # =====================================================
    # Relative Error
    # =====================================================
    relative_error = (
        np.abs(residual_complex)
        / np.maximum(np.abs(Z), 1e-30)
    )

    relative_error_percent = relative_error * 100

    mean_relative_error = np.mean(relative_error_percent)

    max_relative_error = np.max(relative_error_percent)

    # =====================================================
    # RMSE
    # =====================================================
    rmse = np.sqrt(
        np.mean(
            np.abs(residual_complex)**2
        )
    )

    weighted_rmse = np.sqrt(
        np.mean(
            weight *
            np.abs(residual_complex)**2
        )
    )

    return {

        "Chi_square": chi_square,

        "Reduced_chi_square": reduced_chi_square,

        "Sum_of_squares": sum_of_squares,

        "RMSE": rmse,

        "Weighted_RMSE": weighted_rmse,

        "Mean_relative_error_percent":
            mean_relative_error,

        "Max_relative_error_percent":
            max_relative_error,

        "Residual_real": residual_real,

        "Residual_imag": residual_imag,

        "Relative_error_percent":
            relative_error_percent
    }


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