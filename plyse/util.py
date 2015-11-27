# -*- coding: utf-8 -*-


def load_module(class_path):
    parts = class_path.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)

    for comp in parts[1:]:
        m = getattr(m, comp)

    return m

