from django import template
from sections.models import Section


register = template.Library()


def _render_template(categories, obj, sections, i):
    path = obj["path"]
    title = eval(path[path.rfind("["):])[0]

    obj["html"] = obj.get("html", f'''
        <div class="category">
            <button class="category_btn"><a>{title}<span>&rsaquo;</span></a></button>
            <div class="subcategories">
                {path}
            </div>
        </div>
    ''')
    obj["html_is_completed"] = obj.get("html_is_completed", False)
    obj["html_is_fetched"] = obj.get("html_is_fetched", False)

    keys = obj.keys()
    html_is_fetched = []
    for j in keys:
        if j in ["html", "html_is_completed", "html_is_fetched", "path"]:
            continue
        else:
            if obj[j].get("html_is_completed") and not obj[j].get("html_is_fetched"):
                html_is_fetched.append(True)
                obj[j]["html_is_fetched"] = True
                obj["html"] = obj["html"].replace(path, obj[j]["html"]+"\n"+path)
            elif obj[j].get("html_is_completed") and obj[j].get("html_is_fetched"):
                html_is_fetched.append(True)

    if len(html_is_fetched) == len(keys) - 4:
        obj["html_is_completed"] = True
        obj["html"] = obj["html"].replace(path, "")

    obj = obj['path']
    obj = obj[:obj.rfind("[")]
    obj = eval(f"{obj}")

    if i - 1 != -1:
        _render_template(categories, obj, sections, i-1)


def _fill_dictionary_with_categories(categories, obj, sections, i, path=None):
    if len(sections) - 1 == i:
        obj[sections[i].title] = {"html": f'<button class="section_btn"><a href="{sections[i].get_absolute_url()}">{sections[i].title}</a></button>', "html_is_completed": True, "html_is_fetched": False, "section_pk": sections[i].pk}
    else:
        obj[sections[i].title] = obj.get(sections[i].title, {"html_is_completed": False, "html_is_fetched": False})
        if i == 0:
            path = f"categories['{sections[i].title}']"
        else:
            path += f"['{sections[i].title}']"

        obj[sections[i].title]["path"] = path
        _fill_dictionary_with_categories(categories, obj[sections[i].title], sections, i+1, path=path)


def _get_parent_sections(section):
    if not section.category:
        return [section]

    parent_sections = [section, section.category]

    while parent_sections[len(parent_sections) - 1].parent_category is not None:
        parent_sections.append(parent_sections[len(parent_sections)-1].parent_category)

    parent_sections.reverse()
    return parent_sections


def get_sections_tree():
    categories = {}
    sections = list(Section.objects.all())

    for i in range(len(sections)):
        sections[i] = _get_parent_sections(sections[i])
        _fill_dictionary_with_categories(categories, categories, sections[i], 0)

    for section in sections:
        path = "categories"
        if len(section) != 1:
            for i in section:
                path += f"['{i.title}']"

            obj = path[:path.rfind("[")]
            obj = eval(f"{obj}")
            _render_template(categories, obj, section, len(section) - 2)

    return categories


@register.simple_tag(name="get_sections_tree")
def get_sections_tree_tag():
    categories = get_sections_tree()
    categories_html = ""
    for i in categories.keys():
        categories_html += categories[i]["html"] + "\n"

    return categories_html
