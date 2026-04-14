import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("Top_5_Busiest_Hours.csv")

day_map = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday"
}

df["weekday_name"] = df["weekday"].map(day_map)

weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def format_hour(hour_value):
    hour_value = int(hour_value)
    if hour_value == 0:
        return "12 AM"
    elif hour_value < 12:
        return f"{hour_value} AM"
    elif hour_value == 12:
        return "12 PM"
    else:
        return f"{hour_value - 12} PM"


for garage_name in df["garage_name"].unique():
    garage_df = df[df["garage_name"] == garage_name].copy()

    garage_df["weekday_name"] = pd.Categorical(
        garage_df["weekday_name"],
        categories=weekday_order,
        ordered=True
    )

    garage_df = garage_df.sort_values(["weekday_name", "rn"])

    pivot_values = garage_df.pivot(index="weekday_name", columns="rn", values="avg_percent_full")
    pivot_hours = garage_df.pivot(index="weekday_name", columns="rn", values="str_hour")

    pivot_values = pivot_values.dropna(how="all")
    pivot_hours = pivot_hours.loc[pivot_values.index]

    x = np.arange(len(pivot_values.index))
    width = 0.1

    plt.figure(figsize=(13, 7))

    num_ranks = len(pivot_values.columns)
    offsets = np.linspace(
    -(num_ranks - 1) / 2,
    (num_ranks - 1) / 2,
    num_ranks
) * (width * 1.8)

    for i, rank in enumerate(pivot_values.columns):
        bars = plt.bar(
            x + offsets[i],
            pivot_values[rank],
            width=width,
            color="#4C72B0",
            alpha=0.85
        )

        for j, bar in enumerate(bars):
            hour_value = pivot_hours.iloc[j, i]
            height = bar.get_height()

            if not pd.isna(hour_value) and not pd.isna(height):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 1.2,
                    format_hour(hour_value),
                    ha="center",
                    va="bottom",
                    fontsize=6
                )

    plt.xticks(x, pivot_values.index, fontsize=10)
    plt.yticks(fontsize=10)
    plt.xlabel("Day of Week", fontsize=11)
    plt.ylabel("Average Percent Full", fontsize=11)
    plt.title(f"Top 5 Busiest Hours by Day - {garage_name}", fontsize=14, pad=18)

    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.ylim(0, max(100, pivot_values.max().max() + 12))
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])

    safe_name = garage_name.replace(" ", "_")
    plt.savefig(f"{safe_name}_top5_hours.png", dpi=220, bbox_inches="tight")
    plt.show()
    plt.close()