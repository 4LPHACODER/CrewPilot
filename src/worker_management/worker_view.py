import flet as ft
from flet_core import colors
from database.db_connection import DatabaseConnection
from utils.utils import validate_worker_data, format_currency

def create_worker_view(db: DatabaseConnection, page: ft.Page):
    """Create the worker management view"""
    
    def refresh_data(e):
        """Refresh worker data"""
        worker_table.rows = get_worker_rows()
        page.update()

    def create_worker_form():
        # Form fields
        name_field = ft.TextField(
            label="Full Name",
            border=ft.InputBorder.UNDERLINE,
            width=300
        )
        
        position_field = ft.TextField(
            label="Position",
            border=ft.InputBorder.UNDERLINE,
            width=300
        )
        
        salary_field = ft.TextField(
            label="Salary",
            border=ft.InputBorder.UNDERLINE,
            width=300,
            prefix_text="$"
        )
        
        status_dropdown = ft.Dropdown(
            label="Status",
            width=300,
            options=[
                ft.dropdown.Option("active", "Active"),
                ft.dropdown.Option("inactive", "Inactive"),
                ft.dropdown.Option("on_leave", "On Leave")
            ]
        )
        
        performance_field = ft.TextField(
            label="Performance Score",
            border=ft.InputBorder.UNDERLINE,
            width=300,
            hint_text="0-10"
        )
        
        # Form buttons
        submit_button = ft.ElevatedButton(
            "Add Worker",
            icon=ft.Icons.PERSON_ADD,
            on_click=lambda e: submit_worker(e, name_field, position_field, salary_field, status_dropdown, performance_field)
        )
        
        clear_button = ft.OutlinedButton(
            icon=ft.Icons.CLEAR,
            text="Clear Form",
            on_click=lambda e: clear_form(e, name_field, position_field, salary_field, status_dropdown, performance_field, submit_button)
        )
        
        return ft.Column([
            ft.Text("Add New Worker", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([name_field, position_field]),
            ft.Row([salary_field, status_dropdown]),
            ft.Row([performance_field]),
            ft.Row([submit_button, clear_button])
        ])

    def get_worker_rows():
        try:
            workers = db.fetch_all("SELECT * FROM workers ORDER BY name")
            return [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(worker['name'])),
                        ft.DataCell(ft.Text(worker['position'])),
                        ft.DataCell(ft.Text(format_currency(worker['salary']))),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    worker['status'].title(),
                                    color=colors.WHITE
                                ),
                                bgcolor=get_status_color(worker['status']),
                                padding=5,
                                border_radius=5
                            )
                        ),
                        ft.DataCell(ft.Text(f"{worker['performance_score']:.1f}")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color=colors.BLUE,
                                    tooltip="Edit",
                                    data=worker['id'],
                                    on_click=lambda e, w=worker: edit_worker(e, w, name_field, position_field, salary_field, status_dropdown, performance_field, submit_button)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=colors.RED,
                                    tooltip="Delete",
                                    data=worker['id'],
                                    on_click=lambda e, w=worker: delete_worker(e, w)
                                )
                            ])
                        )
                    ]
                ) for worker in workers
            ]
        except Exception as e:
            print(f"Error getting worker rows: {e}")
            return []

    def get_status_color(status: str) -> str:
        colors = {
            'active': colors.GREEN,
            'inactive': colors.RED,
            'on_leave': colors.ORANGE
        }
        return colors.get(status, colors.GREY)

    def submit_worker(e, name_field, position_field, salary_field, status_dropdown, performance_field):
        try:
            # Get form data
            worker_data = {
                'name': name_field.value,
                'position': position_field.value,
                'salary': float(salary_field.value.replace('$', '').replace(',', '')),
                'status': status_dropdown.value,
                'performance_score': float(performance_field.value)
            }
            
            # Validate data
            if validate_worker_data(worker_data):
                # Insert into database
                query = """
                    INSERT INTO workers (name, position, salary, status, performance_score)
                    VALUES (%s, %s, %s, %s, %s)
                """
                db.execute_query(query, (
                    worker_data['name'],
                    worker_data['position'],
                    worker_data['salary'],
                    worker_data['status'],
                    worker_data['performance_score']
                ))
                
                # Log activity
                db.execute_query(
                    "INSERT INTO activities (worker_id, description, type) VALUES (%s, %s, %s)",
                    (db.lastrowid, f"Added new worker: {worker_data['name']}", "worker_added")
                )
                
                # Clear form and refresh table
                clear_form(None, name_field, position_field, salary_field, status_dropdown, performance_field, submit_button)
                worker_table.rows = get_worker_rows()
                page.update()
                
        except Exception as e:
            print(f"Error submitting worker: {e}")
            # Show error message
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error adding worker. Please check the form data."))
            )

    def edit_worker(e, worker, name_field, position_field, salary_field, status_dropdown, performance_field, submit_button):
        try:
            # Populate form with worker data
            name_field.value = worker['name']
            position_field.value = worker['position']
            salary_field.value = str(worker['salary'])
            status_dropdown.value = worker['status']
            performance_field.value = str(worker['performance_score'])
            
            # Update submit button
            submit_button.text = "Update Worker"
            submit_button.data = worker['id']
            submit_button.on_click = lambda e: update_worker(e, worker['id'], name_field, position_field, salary_field, status_dropdown, performance_field, submit_button)
            
            page.update()
            
        except Exception as e:
            print(f"Error editing worker: {e}")
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error loading worker data."))
            )

    def update_worker(e, worker_id, name_field, position_field, salary_field, status_dropdown, performance_field, submit_button):
        try:
            worker_data = {
                'name': name_field.value,
                'position': position_field.value,
                'salary': float(salary_field.value.replace('$', '').replace(',', '')),
                'status': status_dropdown.value,
                'performance_score': float(performance_field.value)
            }
            
            if validate_worker_data(worker_data):
                # Update database
                query = """
                    UPDATE workers 
                    SET name = %s, position = %s, salary = %s, status = %s, performance_score = %s
                    WHERE id = %s
                """
                db.execute_query(query, (
                    worker_data['name'],
                    worker_data['position'],
                    worker_data['salary'],
                    worker_data['status'],
                    worker_data['performance_score'],
                    worker_id
                ))
                
                # Log activity
                db.execute_query(
                    "INSERT INTO activities (worker_id, description, type) VALUES (%s, %s, %s)",
                    (worker_id, f"Updated worker: {worker_data['name']}", "worker_updated")
                )
                
                # Reset form and refresh table
                clear_form(None, name_field, position_field, salary_field, status_dropdown, performance_field, submit_button)
                worker_table.rows = get_worker_rows()
                page.update()
                
        except Exception as e:
            print(f"Error updating worker: {e}")
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error updating worker. Please check the form data."))
            )

    def delete_worker(e, worker):
        try:
            # Show confirmation dialog
            def confirm_delete(e):
                try:
                    # Delete worker
                    db.execute_query("DELETE FROM workers WHERE id = %s", (worker['id'],))
                    
                    # Log activity
                    db.execute_query(
                        "INSERT INTO activities (worker_id, description, type) VALUES (%s, %s, %s)",
                        (worker['id'], f"Removed worker: {worker['name']}", "worker_removed")
                    )
                    
                    # Refresh table
                    worker_table.rows = get_worker_rows()
                    page.update()
                    
                    # Close dialog
                    dlg.open = False
                    page.update()
                    
                except Exception as e:
                    print(f"Error deleting worker: {e}")
                    page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("Error deleting worker."))
                    )
            
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Delete"),
                content=ft.Text(f"Are you sure you want to delete {worker['name']}?"),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, 'open', False)),
                    ft.TextButton("Delete", on_click=confirm_delete)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            
            page.dialog = dlg
            dlg.open = True
            page.update()
            
        except Exception as e:
            print(f"Error preparing delete: {e}")
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error preparing delete operation."))
            )

    def clear_form(e, name_field, position_field, salary_field, status_dropdown, performance_field, submit_button):
        name_field.value = ""
        position_field.value = ""
        salary_field.value = ""
        status_dropdown.value = None
        performance_field.value = ""
        
        # Reset submit button
        submit_button.text = "Add Worker"
        submit_button.data = None
        submit_button.on_click = lambda e: submit_worker(e, name_field, position_field, salary_field, status_dropdown, performance_field)
        
        page.update()

    # Create header
    header = ft.Row([
        ft.Text("Worker Management", size=30, weight=ft.FontWeight.BOLD),
        ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh",
            on_click=refresh_data
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Create worker form
    worker_form = create_worker_form()

    # Create worker table
    worker_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Position")),
            ft.DataColumn(ft.Text("Salary")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Performance")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=get_worker_rows()
    )

    # Create main container
    return ft.Container(
        content=ft.Column([
            header,
            ft.Container(
                content=worker_form,
                padding=20,
                border_radius=10,
                bgcolor=colors.SURFACE_VARIANT
            ),
            ft.Container(
                content=worker_table,
                padding=20,
                border_radius=10,
                bgcolor=colors.SURFACE_VARIANT
            )
        ]),
        padding=20
    ) 