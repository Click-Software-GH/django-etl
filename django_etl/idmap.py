from collections import defaultdict


class IDMap:
    """Keeps legacy ID -> New ID mapping per model"""

    def __ini__(self):
        self.map = defaultdict(dict)

    def add(self, model_name, old_id, new_id):
        self.map[model_name][old_id] = new_id

    def get(self, model_name, old_id):
        return self.map[model_name].get(old_id)
