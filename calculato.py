import random, time, pandas as pd

# === Data (with commas replaced by dots for Python) ===
data_text = """


"""

nums = [float(s.replace(',', '.')) for s in data_text.strip().split()]
random.seed(123)

LOW_AVG, HIGH_AVG = 0.2139, 0.2142
LOW_SUM, HIGH_SUM = LOW_AVG * 10, HIGH_AVG * 10
GROUP_SIZE = 10

start_time = time.time()
best_groups, best_leftovers = [], []
best_count = -1
TIME_LIMIT = 18.0

def try_extract(values):
    avail = values[:]
    groups = []
    while len(avail) >= GROUP_SIZE:
        found = None
        for _ in range(1200):
            sample = random.sample(avail, GROUP_SIZE)
            s = sum(sample)
            improved = True
            iters = 0
            while iters < 200 and not (LOW_SUM < s < HIGH_SUM) and improved:
                improved = False
                if s <= LOW_SUM:
                    sample.sort()
                    outside = sorted([v for v in avail if v not in sample], reverse=True)
                    for small in sample:
                        for cand in outside:
                            new_s = s - small + cand
                            if LOW_SUM < new_s < HIGH_SUM:
                                sample.remove(small)
                                sample.append(cand)
                                s = new_s
                                improved = True
                                break
                        if improved: break
                else:
                    sample.sort(reverse=True)
                    outside = sorted([v for v in avail if v not in sample])
                    for large in sample:
                        for cand in outside:
                            new_s = s - large + cand
                            if LOW_SUM < new_s < HIGH_SUM:
                                sample.remove(large)
                                sample.append(cand)
                                s = new_s
                                improved = True
                                break
                        if improved: break
                iters += 1
            if LOW_SUM < s < HIGH_SUM:
                found = sorted(sample)
                break
        if not found:
            break
        groups.append(found)
        for x in found:
            avail.remove(x)
    return groups, avail

attempt = 0
while time.time() - start_time < TIME_LIMIT:
    attempt += 1
    random.shuffle(nums)
    groups, leftovers = try_extract(nums)
    if len(groups) > best_count:
        best_count = len(groups)
        best_groups, best_leftovers = groups, leftovers
    if best_count >= 9:
        break

# === Create Excel ===
# Each group -> two columns: Group1, Group2, etc.
max_len = max(len(g) for g in best_groups)
data = {}
for i, group in enumerate(best_groups, start=1):
    data[f'Group {i}'] = group + [None] * (max_len - len(group))

df = pd.DataFrame(data)
# Add averages row
df.loc[max_len] = [round(sum(g)/len(g), 6) for g in best_groups]
# Add leftover values below
if best_leftovers:
    df.loc[max_len + 2, 'Leftovers'] = 'Leftover values (sorted)'
    for i, val in enumerate(sorted(best_leftovers), start=1):
        df.loc[max_len + 2 + i, 'Leftovers'] = val

# Save to Excel
output_file = "grouped_numbers.xlsx"
df.to_excel(output_file, index=False)

print(f"✅ Done! File '{output_file}' created successfully.")
print(f"Groups found: {len(best_groups)}, Leftovers: {len(best_leftovers)}")
