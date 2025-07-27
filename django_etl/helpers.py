# migration_core/helpers
#
def clean_text(value):
    return value.strip() if value else ""


def split_csv(text):
    return [item.strip() for item in text.split(",") if item.strip()]


def get_or_create_by_name(model, name, **defaults):
    return model.get_or_create(name=name.strip(), defaults=defaults)
