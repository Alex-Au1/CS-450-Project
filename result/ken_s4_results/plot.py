import re
import matplotlib.pyplot as plt

# Simulating the full input text as if it were read from a file
full_text = open("fiu_madmax_queue_ratios.txt", "r").read()
num_series = 5

# Parse all data
lines = full_text.strip().splitlines()
all_data = {}
current_ratio = ""

cmap = plt.get_cmap("winter")  # 'winter' transitions from blue to green
colors = [cmap(i / (num_series - 1)) for i in range(num_series)]

for line in lines:
    if line.startswith("#"):
        current_ratio = line[2:].strip()
        all_data[current_ratio] = []
    else:
        match = re.search(r"cache size\s+(\d+),.*?miss ratio (\d+\.\d+)", line)
        if match:
            cache_size = int(match.group(1))
            miss_ratio = float(match.group(2))
            all_data[current_ratio].append((cache_size, miss_ratio))

# Plotting
plt.figure(figsize=(10, 6))
i = 0
for ratio, values in all_data.items():
    values.sort()
    sizes = [v[0] for v in values]
    misses = [v[1] for v in values]
    plt.plot(
        sizes,
        misses,
        marker="^" if i == 5 else ("s" if i == 6 else "o"),
        label=f"{ratio}",
        color="#e24f3e" if i == 5 else ("#e24f3e" if i == 6 else colors[i]),
    )
    i += 1
plt.xlabel("Cache Size (B)")
plt.ylabel("Miss Ratio")
plt.title("Miss Ratio vs Cache Size (Lower is Better)")
plt.legend()
plt.grid(True)
plt.xscale("log")
plt.tight_layout()
plt.savefig("plt.png")
