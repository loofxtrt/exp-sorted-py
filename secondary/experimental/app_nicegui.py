from nicegui import ui, app

app.add_static_files('/static', 'static')
ui.add_head_html('<link rel="stylesheet" type="text/css" href="/static/style.css">')

# ui.add_css('''
#     .red {
#         color: red;
#         background-color: red;
#     }
# ''')
ui.add_head_html('<link rel="stylesheet" href="/static/custom.css">')
ui.label('Hello NiceGUI!').classes('red')
ui.button('sarelos').classes('red')

ui.run()