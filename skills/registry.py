SKILL_REGISTRY = []

def skill(cls):
    """
    Decorator used to registers skills automatically.
    """


    SKILL_REGISTRY.append(cls())

    return cls