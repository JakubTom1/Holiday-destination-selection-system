import numpy as np
from typing import List
import copy


def ahp(input_data: List[List[float]], lower_limits: List, upper_limits: List, criteria_idxs: List,
        criteria_comparison: List, benefit_attributes: List) -> List:
    # --- 1. Validation and Filtering ---
    number_of_criteria = len(lower_limits)

    if not all(len(lst) == number_of_criteria for lst in [lower_limits, upper_limits, criteria_idxs]):
        print("Incompatible input data length")
        return []

    data_matrix = []
    ids = []

    # Extract Data and Filter by Limits
    for row in input_data:
        idx = row[0]
        values = row[1:]  # Skip ID

        keep = True
        filtered_values = []

        for i, crit_idx in enumerate(criteria_idxs):
            val = values[crit_idx]

            # Check Limits (benefit or cost)
            if val < lower_limits[i] or val > upper_limits[i]:
                keep = False
                break

            filtered_values.append(val)

        if keep:
            ids.append(int(idx))
            data_matrix.append(filtered_values)

    if not data_matrix:
        return []

    data_np = np.array(data_matrix, dtype=float)
    num_alternatives = len(data_np)
    dim = len(criteria_idxs)

    # --- 2. Criteria Weights (Matrix A) ---
    A = np.eye(dim)
    idx = 0
    for i in range(dim):
        for j in range(i + 1, dim):
            if idx < len(criteria_comparison):
                val = criteria_comparison[idx]
                # Protect against user entering 0 weight ratio
                if val == 0: val = 1e-9
                A[i][j] = val
                A[j][i] = 1.0 / val
                idx += 1

    # Normalize Matrix A -> B
    col_sums = A.sum(axis=0)
    B = A / col_sums

    # Criteria Weights vector w
    w = B.sum(axis=1) / dim

    # Consistency Check (Optional / Warning only)
    Aw = np.dot(A, w)
    lambda_max = np.mean(Aw / w)
    CI = (lambda_max - dim) / (dim - 1) if dim > 1 else 0
    r = [0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
    RI = r[dim - 1] if dim <= 10 else 1.49
    CR = CI / RI if RI != 0 else 0

    # --- 3. Alternatives Scoring (Matrix V) ---
    v = np.zeros((dim, num_alternatives))

    for k in range(dim):
        col_values = data_np[:, k].copy()

        # --- FIX: PROTECT AGAINST DIVISION BY ZERO ---
        # Replace 0 with a tiny number (epsilon) to allow division
        col_values[col_values == 0] = 1e-9

        is_benefit = (benefit_attributes[criteria_idxs[k]] == 1)

        # Vectorized comparison: col_values / col_values (matrix expansion)
        if is_benefit:
            # v1/v2
            comp_mat = col_values[:, None] / col_values
        else:
            # v2/v1 (for minimization/cost)
            comp_mat = col_values / col_values[:, None]

            # Normalize columns
        col_sums_mat = comp_mat.sum(axis=0)
        norm_mat = comp_mat / col_sums_mat

        # Average row to get priority vector for this criterion
        v[k, :] = norm_mat.sum(axis=1) / num_alternatives

    # --- 4. Final Scoring ---
    # Dot product: Weights * Alternative Scores
    final_scores = np.dot(w, v)

    # Sort results
    results = list(zip(ids, final_scores))
    results.sort(key=lambda x: x[1], reverse=True)

    return [r[0] for r in results]