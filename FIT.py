import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from impedance.models.circuits import CustomCircuit


# =========================================================
# ZView 风格误差分析
# =========================================================
def calc_zview_errors(freq, Z, Z_fit, model):
    residual_real = Z.real - Z_fit.real
    residual_imag = Z.imag - Z_fit.imag
    residual_complex = Z - Z_fit

    modulus = np.abs(Z)
    weight = 1 / np.maximum(modulus ** 2, 1e-30)

    chi_square = np.sum(
        weight * (residual_real ** 2 + residual_imag ** 2)
    )

    dof = max(len(Z) * 2 - len(model.parameters_), 1)
    reduced_chi_square = chi_square / dof

    sum_of_squares = np.sum(
        residual_real ** 2 + residual_imag ** 2
    )

    relative_error = np.abs(residual_complex) / np.maximum(np.abs(Z), 1e-30)
    relative_error_percent = relative_error * 100

    rmse = np.sqrt(np.mean(np.abs(residual_complex) ** 2))

    weighted_rmse = np.sqrt(
        np.mean(weight * np.abs(residual_complex) ** 2)
    )

    return {
        "Chi_square": chi_square,
        "Reduced_chi_square": reduced_chi_square,
        "Sum_of_squares": sum_of_squares,
        "RMSE": rmse,
        "Weighted_RMSE": weighted_rmse,
        "Mean_relative_error_percent": np.mean(relative_error_percent),
        "Max_relative_error_percent": np.max(relative_error_percent),
        "Residual_real": residual_real,
        "Residual_imag": residual_imag,
        "Relative_error_percent": relative_error_percent,
    }


# =========================================================
# 根目录
# =========================================================
root_dir = r"E:\姜京浩仿真\姜京浩仿真\5个波原始数据\TJ-EIS-C4"

output_dir = os.path.join(root_dir, "EIS_ERROR_ANALYSIS")
fig_dir = os.path.join(output_dir, "图片")

os.makedirs(output_dir, exist_ok=True)
os.makedirs(fig_dir, exist_ok=True)


# =========================================================
# 二阶 RC 等效电路
# =========================================================
circuit = "R0-p(R1,C1)-p(R2,C2)"

initial_guess = [
    0.001,   # R0
    0.001,   # R1
    1.0,     # C1
    0.001,   # R2
    10.0     # C2
]

lower_bounds = [
    0,
    0,
    1e-8,
    0,
    1e-8
]

upper_bounds = [
    0.1,
    0.1,
    1e6,
    0.1,
    1e6
]


# =========================================================
# 温度和 SOC
# =========================================================
temp_folders = [
    "TJ-EIS-C4-T0",
    "TJ-EIS-C4-T-10",
    "TJ-EIS-C4-T15",
    "TJ-EIS-C4-T25",
    "TJ-EIS-C4-T35",
    "TJ-EIS-C4-T45",
    "TJ-EIS-C4-T55"
]

soc_list = [
    "15SOC",
    "40SOC",
    "50SOC",
    "60SOC",
    "75SOC",
    "85SOC",
    "100SOC"
]


all_results = []
all_point_errors = []


# =========================================================
# 主循环
# =========================================================
for temp in temp_folders:

    temp_path = os.path.join(root_dir, temp)

    if not os.path.exists(temp_path):
        print(f"不存在: {temp_path}")
        continue

    print(f"\n===== {temp} =====")

    colors = plt.cm.tab10(np.linspace(0, 1, len(soc_list)))

    # 当前温度下的总图
    fig_nyq = plt.figure(figsize=(8, 7))
    fig_res_real = plt.figure(figsize=(8, 6))
    fig_res_imag = plt.figure(figsize=(8, 6))
    fig_rel = plt.figure(figsize=(8, 6))

    has_plot = False
    has_res_real = False
    has_res_imag = False
    has_rel = False

    for i, soc in enumerate(soc_list):

        soc_path = os.path.join(temp_path, soc)
        eis_path = os.path.join(soc_path, "EIS")

        if not os.path.exists(eis_path):
            print(f"  没有EIS文件夹: {eis_path}")
            continue

        files = [
            f for f in os.listdir(eis_path)
            if f.lower().endswith((".xlsx", ".xls", ".csv"))
            and not f.startswith("~$")
        ]

        if not files:
            print(f"  没有数据文件: {eis_path}")
            continue

        file = files[0]
        file_path = os.path.join(eis_path, file)

        print(f"  拟合: {soc} -> {file}")

        try:
            # =================================================
            # 读取数据
            # =================================================
            if file_path.lower().endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # A列 Frequency
            # C列 Z'
            # D列 Z''
            freq = pd.to_numeric(df.iloc[:, 0], errors="coerce").to_numpy()
            Zr = pd.to_numeric(df.iloc[:, 2], errors="coerce").to_numpy()
            Zi = pd.to_numeric(df.iloc[:, 3], errors="coerce").to_numpy()

            data = pd.DataFrame({
                "freq": freq,
                "Zr": Zr,
                "Zi": Zi
            }).dropna()

            data = data[data["freq"] > 0]

            if len(data) < 6:
                print("  数据点不足")
                continue

            # 高频到低频排序，不删点
            data = data.sort_values(by="freq", ascending=False)

            freq = data["freq"].to_numpy()
            Zr = data["Zr"].to_numpy()
            Zi = data["Zi"].to_numpy()

            Z = Zr + 1j * Zi

            # =================================================
            # 拟合
            # =================================================
            model = CustomCircuit(
                circuit,
                initial_guess=initial_guess
            )

            model.fit(
                freq,
                Z,
                bounds=(lower_bounds, upper_bounds),
                method="trf",
                maxfev=50000,
                weight_by_modulus=True
            )

            Z_fit = model.predict(freq)

            if (
                np.any(np.isnan(Z_fit.real))
                or np.any(np.isnan(Z_fit.imag))
                or np.any(np.isinf(Z_fit.real))
                or np.any(np.isinf(Z_fit.imag))
            ):
                print("  拟合发散")
                continue

            # =================================================
            # 误差分析
            # =================================================
            errors = calc_zview_errors(freq, Z, Z_fit, model)
            p = model.parameters_

            all_results.append({
                "温度": temp,
                "SOC": soc,
                "文件": file,
                "点数": len(freq),

                "R0": p[0],
                "R1": p[1],
                "C1": p[2],
                "R2": p[3],
                "C2": p[4],

                "Chi_square": errors["Chi_square"],
                "Reduced_chi_square": errors["Reduced_chi_square"],
                "Sum_of_squares": errors["Sum_of_squares"],
                "RMSE": errors["RMSE"],
                "Weighted_RMSE": errors["Weighted_RMSE"],
                "Mean_relative_error_percent": errors["Mean_relative_error_percent"],
                "Max_relative_error_percent": errors["Max_relative_error_percent"],
            })

            residual_complex = Z - Z_fit

            for k in range(len(freq)):
                all_point_errors.append({
                    "温度": temp,
                    "SOC": soc,
                    "文件": file,
                    "Frequency_Hz": freq[k],

                    "Z_real_exp": Z.real[k],
                    "Z_imag_exp": Z.imag[k],
                    "Z_real_fit": Z_fit.real[k],
                    "Z_imag_fit": Z_fit.imag[k],

                    "Residual_real": errors["Residual_real"][k],
                    "Residual_imag": errors["Residual_imag"][k],

                    "Abs_error": np.abs(residual_complex[k]),
                    "Relative_error_percent": errors["Relative_error_percent"][k],
                })

            # =================================================
            # 当前温度下，不同 SOC 画在同一张图
            # =================================================

            # Nyquist
            plt.figure(fig_nyq.number)
            plt.plot(
                Zr,
                -Zi,
                "o",
                color=colors[i],
                markersize=5,
                alpha=0.7
            )

            plt.plot(
                Z_fit.real,
                -Z_fit.imag,
                "-",
                color=colors[i],
                linewidth=2,
                label=soc
            )

            has_plot = True

            # Real residual
            plt.figure(fig_res_real.number)
            plt.semilogx(
                freq,
                errors["Residual_real"],
                "o-",
                color=colors[i],
                linewidth=2,
                markersize=5,
                label=soc
            )
            has_res_real = True

            # Imag residual
            plt.figure(fig_res_imag.number)
            plt.semilogx(
                freq,
                errors["Residual_imag"],
                "s-",
                color=colors[i],
                linewidth=2,
                markersize=5,
                label=soc
            )
            has_res_imag = True

            # Relative error
            plt.figure(fig_rel.number)
            plt.semilogx(
                freq,
                errors["Relative_error_percent"],
                "o-",
                color=colors[i],
                linewidth=2,
                markersize=5,
                label=soc
            )
            has_rel = True

            print(
                f"  ✅ {soc} 成功 | "
                f"Chi²={errors['Chi_square']:.3e}, "
                f"Weighted_RMSE={errors['Weighted_RMSE']:.3e}, "
                f"Mean_RE={errors['Mean_relative_error_percent']:.2f}%"
            )

        except Exception as e:
            print(f"  ❌ {soc} 失败: {e}")
            continue

    # =========================================================
    # 保存当前温度下的总图
    # =========================================================

    if has_plot:
        plt.figure(fig_nyq.number)
        plt.xlabel("Z' (Ω)")
        plt.ylabel("-Z'' (Ω)")
        plt.title(f"{temp} Nyquist 二阶RC拟合")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        save_path = os.path.join(fig_dir, f"{temp}_Nyquist.png")
        plt.savefig(save_path, dpi=300)

    if has_res_real:
        plt.figure(fig_res_real.number)
        plt.axhline(0, color="black", linestyle="--", linewidth=1)
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Real Residual (Ω)")
        plt.title(f"{temp} Real Residual")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        save_path = os.path.join(fig_dir, f"{temp}_Residual_Real.png")
        plt.savefig(save_path, dpi=300)

    if has_res_imag:
        plt.figure(fig_res_imag.number)
        plt.axhline(0, color="black", linestyle="--", linewidth=1)
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Imag Residual (Ω)")
        plt.title(f"{temp} Imag Residual")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        save_path = os.path.join(fig_dir, f"{temp}_Residual_Imag.png")
        plt.savefig(save_path, dpi=300)

    if has_rel:
        plt.figure(fig_rel.number)
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Relative Error (%)")
        plt.title(f"{temp} Relative Error")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        save_path = os.path.join(fig_dir, f"{temp}_Relative_Error.png")
        plt.savefig(save_path, dpi=300)

    plt.close("all")


# =========================================================
# 保存 Excel
# =========================================================
df_out = pd.DataFrame(all_results)
df_point = pd.DataFrame(all_point_errors)

excel_path = os.path.join(output_dir, "二阶RC_ZView误差分析.xlsx")

with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    df_out.to_excel(writer, sheet_name="拟合参数与总误差", index=False)
    df_point.to_excel(writer, sheet_name="逐频点误差", index=False)

print("\n全部完成")
print(f"\n结果保存:\n{excel_path}")
print(f"图片保存:\n{fig_dir}")