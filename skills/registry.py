SKILL_REGISTRY = []


def skill(cls):
    instance = cls()
    SKILL_REGISTRY.append(instance)
    return cls