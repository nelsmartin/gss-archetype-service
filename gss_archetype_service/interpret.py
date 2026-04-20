from gss_archetype_service.archetypes import ArchetypeResult
from gss_archetype_service.preprocess import NOMINAL_COLUMNS, ORDINAL_COLUMNS


def interpret(result: ArchetypeResult, value_labels: dict[str, dict[int, str]]) -> list[dict]:
    scaler = result.preprocessor.named_transformers_["ordinal"]
    ohe = result.preprocessor.named_transformers_["nominal"]
    n_ordinal = len(ORDINAL_COLUMNS)
    total = int(result.sizes.sum())

    archetypes = []
    for i, centroid in enumerate(result.centroids):
        size = int(result.sizes[i])
        archetype: dict = {"size": size, "share": round(size / total, 4)}

        ordinal_original = scaler.inverse_transform(centroid[:n_ordinal].reshape(1, -1))[0]
        for name, val in zip(ORDINAL_COLUMNS, ordinal_original):
            archetype[name] = round(float(val), 2)

        offset = n_ordinal
        for col, cats in zip(NOMINAL_COLUMNS, ohe.categories_):
            n = len(cats)
            block = centroid[offset : offset + n]
            code = int(cats[block.argmax()])
            archetype[col] = value_labels.get(col, {}).get(code, f"code_{code}")
            offset += n

        archetypes.append(archetype)

    return archetypes
