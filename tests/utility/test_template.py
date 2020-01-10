from app.api.utility.utils import TemplateEngine

def test_render():
    template_dir_path = "app/api/reports/templates"
    template_name = "daily_reports"
    data = {
        "greeting": "some greeting",
        "message": "some message"
    }
    template = TemplateEngine(template_name, data, template_dir_path)
    html_result = template.render()
    assert "some greeting" in html_result
    assert "some message" in html_result
