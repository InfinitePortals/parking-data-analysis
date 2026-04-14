import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("test.csv")

# Convert hour to int
df["collected_hour"] = df["collected_hour"].astype(int)

# GROUP AGAIN to collapse multiple days into one value per hour
grouped = df.groupby(["garage_name", "collected_hour"])["avg_percent_full"].mean().reset_index()

# Plot
for garage in grouped["garage_name"].unique():
    garage_data = grouped[grouped["garage_name"] == garage].sort_values("collected_hour")
    
    plt.plot(
        garage_data["collected_hour"],
        garage_data["avg_percent_full"],
        marker="o",
        label=garage
    )

plt.xlabel("Hour of Day")
plt.ylabel("Average Percent Full")
plt.title("Average Garage Fullness by Hour of Day")
plt.xticks(range(0, 24))
plt.legend()
plt.tight_layout()
plt.show()