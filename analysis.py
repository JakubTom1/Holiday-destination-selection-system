import numpy as np
from scipy.stats import spearmanr
import copy
import methods.topsis as topsis
import methods.rsm as rsm
import methods.UTA as UTA
import methods.AHP as AHP
import methods.Sp_Cs as Sp_Cs


def get_ids(res):
    if not res: return []
    if isinstance(res[0], (int, float, np.integer)):
        return [int(x) for x in res]
    return []


def generate_ahp_comparisons(weights):
    """
    Generates comparison list for the corrected AHP.py.
    Order: (0,1), (0,2), ..., (1,2), (1,3)...
    """
    n = len(weights)
    comparisons = []
    for i in range(n):
        for j in range(i + 1, n):
            if weights[j] == 0:
                val = 1.0
            else:
                val = weights[i] / weights[j]
            comparisons.append(val)
    return comparisons


def perform_analysis(data, lower, upper, weights, benefits):
    rankings = {}
    num_criteria = len(data[0]) - 1

    # 1. TOPSIS
    try:
        rankings['TOPSIS'] = get_ids(topsis.topsis(copy.deepcopy(data), lower, upper, weights, benefits))
    except Exception as e:
        print(f"TOPSIS error: {e}")
        rankings['TOPSIS'] = []

    # 2. RSM
    try:
        is_active = [1] * len(weights)
        rankings['RSM'] = get_ids(rsm.rsm(copy.deepcopy(data), lower, upper, is_active, benefits))
    except Exception as e:
        print(f"RSM error: {e}")
        rankings['RSM'] = []

    # 3. UTA
    try:
        comps = [5] * num_criteria
        u_idx = UTA.UTA_star(copy.deepcopy(data), lower, upper, weights, benefits, comps)
        if isinstance(u_idx, list):
            u_ids = [int(data[i][0]) for i in u_idx if i < len(data)]
            rankings['UTA'] = u_ids
        else:
            rankings['UTA'] = []
    except Exception as e:
        print(f"UTA error: {e}")
        rankings['UTA'] = []

    # 4. AHP (FIXED)
    try:
        crit_idxs = list(range(num_criteria))
        ahp_comparisons = generate_ahp_comparisons(weights)

        # Verify function exists and call it
        if hasattr(AHP, 'ahp'):
            rankings['AHP'] = get_ids(AHP.ahp(copy.deepcopy(data), lower, upper, crit_idxs, ahp_comparisons, benefits))
        else:
            print("AHP module missing 'ahp' function.")
            rankings['AHP'] = []
    except Exception as e:
        print(f"AHP error: {e}")
        rankings['AHP'] = []

    # 5. SP-CS
    try:
        if num_criteria > 3:
            sorted_indices = np.argsort(weights)[::-1]
            selected_crit_idxs = sorted_indices[:3].tolist()
        else:
            selected_crit_idxs = list(range(num_criteria))

        if hasattr(Sp_Cs, 'sp_cs'):
            rankings['SP-CS'] = get_ids(Sp_Cs.sp_cs(copy.deepcopy(data), lower, upper, selected_crit_idxs, benefits))
        elif hasattr(Sp_Cs, 'ranking_multidimensional'):
            rankings['SP-CS'] = get_ids(
                Sp_Cs.ranking_multidimensional(copy.deepcopy(data), lower, upper, weights, benefits))
        else:
            rankings['SP-CS'] = []
    except Exception as e:
        print(f"SP-CS error: {e}")
        rankings['SP-CS'] = []

    # --- Correlation & Consensus Logic ---
    valid_rankings = {k: v for k, v in rankings.items() if v and len(v) > 1}

    if len(valid_rankings) < 2:
        return None, None, "Not enough successful methods to perform comparison."

    methods = list(valid_rankings.keys())
    n = len(methods)
    corr_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                corr_matrix[i][j] = 1.0
            else:
                r1, r2 = valid_rankings[methods[i]], valid_rankings[methods[j]]
                common = list(set(r1) & set(r2))
                if len(common) > 5:
                    m1 = {x: k for k, x in enumerate(r1)}
                    m2 = {x: k for k, x in enumerate(r2)}
                    v1 = [m1[c] for c in common]
                    v2 = [m2[c] for c in common]
                    rho, _ = spearmanr(v1, v2)
                    corr_matrix[i][j] = rho
                else:
                    corr_matrix[i][j] = 0.0

    all_ids = set()
    for r in valid_rankings.values():
        all_ids.update(r)

    consensus_scores = {}
    for uid in all_ids:
        ranks = []
        for m in methods:
            try:
                r = valid_rankings[m].index(uid) + 1
                ranks.append(r)
            except ValueError:
                ranks.append(len(all_ids) + 1)

        consensus_scores[uid] = {
            'avg_rank': sum(ranks) / len(ranks),
            'ranks': ranks
        }

    sorted_consensus = sorted(consensus_scores.items(), key=lambda x: x[1]['avg_rank'])

    return valid_rankings, corr_matrix, sorted_consensus