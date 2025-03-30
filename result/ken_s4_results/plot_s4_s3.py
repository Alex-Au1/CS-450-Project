import glob
import re
import matplotlib.pyplot as plt


def process_files(path_pattern):
    """
    Process files matching the given glob pattern.
    Extracts lines for S3FIFO and S4FIFO, groups by cache size,
    computes the average miss ratio, and then calculates the difference:
       (S3FIFO miss ratio - S4FIFO miss ratio)
    Only cache sizes with both S3FIFO and S4FIFO entries are considered.

    Returns a list of tuples: (cache_size, difference), sorted by cache_size.
    """
    # Regular expression to capture algorithm (S4FIFO or S3FIFO), cache size, and miss ratio.
    pattern = re.compile(
        r"(S4FIFO|S3FIFO)(?:-\S+)?\s+cache size\s+(\d+),.*miss ratio\s+(\d+\.\d+)"
    )
    results = {}

    # Process each file matching the glob pattern.
    for file_path in glob.glob(path_pattern):
        with open(file_path, "r") as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    algo = match.group(1)
                    size = int(match.group(2))
                    miss_ratio = float(match.group(3))
                    key = (algo, size)
                    results.setdefault(key, []).append(miss_ratio)

    # Compute the average miss ratio for each (algorithm, cache size) pair.
    averages = {
        key: sum(miss_ratios) / len(miss_ratios) for key, miss_ratios in results.items()
    }

    # Organize data by cache size.
    diff_by_size = {}
    for (algo, size), avg in averages.items():
        diff_by_size.setdefault(size, {})[algo] = avg

    # Calculate the difference (S3FIFO - S4FIFO) for cache sizes where both are present.
    differences = []
    for size, algo_dict in diff_by_size.items():
        if "S3FIFO" in algo_dict and "S4FIFO" in algo_dict:
            diff = algo_dict["S4FIFO"] - algo_dict["S3FIFO"]
            differences.append((size, diff))

    # Sort by cache size.
    differences.sort(key=lambda x: x[0])
    return differences


# Process the two different datasets.
data1 = process_files("../project cachesim/all_with_s4/FIU/*")
data2 = process_files("../project cachesim/all_with_s4/MSR/*")

# Create subplots: one row, two columns.
fig, axs = plt.subplots(2, 1, figsize=(10, 6))

# Plot for the first dataset.
ax = axs[0]
sizes = [size for size, diff in data1]
diffs = [diff for size, diff in data1]
ax.scatter(sizes, diffs, alpha=0.7)
ax.set_xscale("log")
ax.set_xlabel("Cache Size")
ax.set_ylabel("Difference (S4FIFO - S3FIFO)")
ax.set_title("S4FIFO Miss Rate Improvement vs Cache Size (FIU)")
ax.axhline(0, color="gray", linestyle="--")  # Reference line at 0
ax.text(
    0.95,
    0.95,
    f"Avg: {sum(diffs) / len(diffs):.4f}",
    transform=ax.transAxes,
    ha="right",
    va="top",
    bbox=dict(facecolor="white", alpha=0.5),
)

# Plot for the second dataset.
ax = axs[1]
sizes = [size for size, diff in data2]
diffs = [diff for size, diff in data2]
ax.scatter(sizes, diffs, alpha=0.7)
ax.set_xscale("log")
ax.set_xlabel("Cache Size")
ax.set_ylabel("Difference (S4FIFO - S3FIFO)")
ax.set_title("S4FIFO Miss Rate Improvement vs Cache Size (MSR)")
ax.axhline(0, color="gray", linestyle="--")  # Reference line at 0
ax.text(
    0.95,
    0.95,
    f"Avg: {sum(diffs) / len(diffs):.4f}",
    transform=ax.transAxes,
    ha="right",
    va="top",
    bbox=dict(facecolor="white", alpha=0.5),
)
plt.tight_layout()
plt.savefig("delta_stacked.png")
