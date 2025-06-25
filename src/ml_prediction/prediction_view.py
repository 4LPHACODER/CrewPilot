import flet as ft
from flet_core import colors
from database.db_connection import DatabaseConnection
from ml_prediction.predictor import WorkerPredictor

def create_prediction_view(db: DatabaseConnection, page: ft.Page):
    """Create the prediction view"""
    
    # Initialize predictor
    predictor = WorkerPredictor(db)
    
    def refresh_data(e):
        """Refresh prediction data"""
        worker_dropdown.options = get_worker_options()
        history_table.rows = get_prediction_rows()
        page.update()

    def create_prediction_form():
        # Form fields
        worker_dropdown = ft.Dropdown(
            label="Select Worker",
            width=300,
            options=get_worker_options()
        )
        
        hours_field = ft.TextField(
            label="Hours Worked",
            border=ft.InputBorder.UNDERLINE,
            width=300,
            hint_text="Enter hours worked"
        )
        
        tasks_field = ft.TextField(
            label="Tasks Completed",
            border=ft.InputBorder.UNDERLINE,
            width=300,
            hint_text="Enter number of tasks"
        )
        
        efficiency_field = ft.TextField(
            label="Efficiency Rate",
            border=ft.InputBorder.UNDERLINE,
            width=300,
            hint_text="Enter efficiency rate (0-100)"
        )
        
        # Submit button
        submit_button = ft.ElevatedButton(
            "Generate Prediction",
            icon=ft.Icons.ANALYTICS,
            on_click=lambda e: generate_prediction(e, worker_dropdown, hours_field, tasks_field, efficiency_field)
        )
        
        return ft.Column([
            ft.Text("Make Prediction", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([worker_dropdown]),
            ft.Row([hours_field, tasks_field]),
            ft.Row([efficiency_field]),
            ft.Row([submit_button])
        ])

    def create_results_section():
        return ft.Column([
            ft.Text("Prediction Results", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Prediction Score:", size=16),
                        ft.Text("", size=16, weight=ft.FontWeight.BOLD, id="prediction_score")
                    ]),
                    ft.Row([
                        ft.Text("Confidence Score:", size=16),
                        ft.Text("", size=16, weight=ft.FontWeight.BOLD, id="confidence_score")
                    ]),
                    ft.Row([
                        ft.Text("Features Used:", size=16),
                        ft.Text("", size=16, id="features_used")
                    ])
                ]),
                padding=20,
                border_radius=10,
                bgcolor=colors.SURFACE_VARIANT
            )
        ])

    def create_history_table():
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Worker")),
                ft.DataColumn(ft.Text("Hours")),
                ft.DataColumn(ft.Text("Tasks")),
                ft.DataColumn(ft.Text("Efficiency")),
                ft.DataColumn(ft.Text("Predicted Score")),
                ft.DataColumn(ft.Text("Confidence"))
            ],
            rows=get_prediction_rows()
        )

    def get_worker_options():
        try:
            workers = db.fetch_all("SELECT id, name FROM workers WHERE status = 'active'")
            return [
                ft.dropdown.Option(str(worker['id']), worker['name'])
                for worker in workers
            ]
        except Exception as e:
            print(f"Error getting worker options: {e}")
            return []

    def get_prediction_rows():
        try:
            predictions = db.fetch_all("""
                SELECT p.*, w.name as worker_name 
                FROM performance_predictions p
                JOIN workers w ON p.worker_id = w.id
                ORDER BY p.created_at DESC
                LIMIT 10
            """)
            return [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(pred['worker_name'])),
                        ft.DataCell(ft.Text(str(pred['hours_worked']))),
                        ft.DataCell(ft.Text(str(pred['tasks_completed']))),
                        ft.DataCell(ft.Text(f"{pred['efficiency_rate']}%")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    f"{pred['predicted_score']:.1f}",
                                    color=colors.WHITE
                                ),
                                bgcolor=get_score_color(pred['predicted_score']),
                                padding=5,
                                border_radius=5
                            )
                        ),
                        ft.DataCell(ft.Text(f"{pred['confidence_score']:.1f}"))
                    ]
                ) for pred in predictions
            ]
        except Exception as e:
            print(f"Error getting prediction rows: {e}")
            return []

    def generate_prediction(e, worker_dropdown, hours_field, tasks_field, efficiency_field):
        try:
            # Get form data
            worker_id = int(worker_dropdown.value)
            hours_worked = float(hours_field.value)
            tasks_completed = int(tasks_field.value)
            efficiency_rate = float(efficiency_field.value)
            
            # Generate prediction
            prediction = predictor.predict_performance(
                worker_id,
                hours_worked,
                tasks_completed,
                efficiency_rate
            )
            
            # Update results
            page.get_control("prediction_score").value = f"{prediction['predicted_score']:.1f}"
            page.get_control("confidence_score").value = f"{prediction['confidence_score']:.1f}"
            page.get_control("features_used").value = ", ".join(prediction['features_used'])
            
            # Refresh history table
            history_table.rows = get_prediction_rows()
            page.update()
            
        except Exception as e:
            print(f"Error generating prediction: {e}")
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error generating prediction. Please check the input data."))
            )

    def get_score_color(score: float) -> str:
        if score >= 8:
            return colors.GREEN
        elif score >= 6:
            return colors.ORANGE
        else:
            return colors.RED

    # Create header
    header = ft.Row([
        ft.Text("Performance Prediction", size=30, weight=ft.FontWeight.BOLD),
        ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh",
            on_click=refresh_data
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Create prediction form
    prediction_form = create_prediction_form()

    # Create results section
    results_section = create_results_section()

    # Create history table
    history_table = create_history_table()

    # Create main container
    return ft.Container(
        content=ft.Column([
            header,
            ft.Container(
                content=prediction_form,
                padding=20,
                border_radius=10,
                bgcolor=colors.SURFACE_VARIANT
            ),
            ft.Container(
                content=results_section,
                padding=20,
                border_radius=10,
                bgcolor=colors.SURFACE_VARIANT
            ),
            ft.Container(
                content=history_table,
                padding=20,
                border_radius=10,
                bgcolor=colors.SURFACE_VARIANT
            )
        ]),
        padding=20
    ) 