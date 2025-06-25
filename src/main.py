import flet as ft
from flet import (
    Page, View, AppBar, NavigationRail, NavigationRailDestination,
    Text, Icon, Container, Column, Row, ElevatedButton, Card, DataTable, DataColumn, DataRow, DataCell,
    TextField, Dropdown, dropdown, AlertDialog, IconButton, LineChart, LineChartData, LineChartDataPoint,
    TextButton, ChartAxis, ChartGridLines, border, ListView, BoxShadow, RoundedRectangleBorder
)
from flet_core import colors
from database.db_connection import DatabaseConnection
from utils.utils import setup_logging, log_error, format_percentage
import logging
from authentication.auth_view import AuthView
from chatbot.chatbot_view import get_chatbot_view

def get_activity_icon(activity_type: str) -> str:
    """Get the appropriate icon for an activity type"""
    icons = {
        'task_completed': ft.Icons.CHECK_CIRCLE,
        'task_assigned': ft.Icons.ASSIGNMENT,
        'performance_review': ft.Icons.STAR,
        'training': ft.Icons.SCHOOL,
        'incident': ft.Icons.WARNING,
        'leave': ft.Icons.EVENT_BUSY,
        'return': ft.Icons.EVENT_AVAILABLE
    }
    return icons.get(activity_type.lower(), ft.Icons.INFO)

def get_activity_color(activity_type: str) -> str:
    """Get the appropriate color for an activity type"""
    color_map = {
        'task_completed': colors.GREEN,
        'task_assigned': colors.BLUE,
        'performance_review': colors.AMBER,
        'training': colors.PURPLE,
        'incident': colors.RED,
        'leave': colors.ORANGE,
        'return': colors.TEAL
    }
    return color_map.get(activity_type.lower(), colors.GREY)

def main(page: ft.Page):
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting application")
    
    # Configure page
    page.title = "CrewPilot"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600
    page.padding = 0
    page.spacing = 0
    page.bgcolor = colors.BLUE_GREY_900
    
    # Initialize database connection
    db = DatabaseConnection()
    logger.info("Database connection initialized")
    
    # Initialize auth view
    auth_view = AuthView(page, db)
    logger.info("Auth view initialized")
    
    def route_change(e):
        """Handle route changes"""
        try:
            route = e.route if hasattr(e, 'route') else e
            logger.info(f"Route change to: {route}")
            page.views.clear()
            
            if route == "/login":
                logger.info("Creating login view")
                login_view = auth_view.create_login_view()
                page.views.append(
                    ft.View(
                        route="/login",
                        controls=[login_view],
                        padding=0,
                    )
                )
                logger.info("Login view added to page")
            elif route == "/signup":
                logger.info("Creating signup view")
                signup_view = auth_view.create_signup_view()
                page.views.append(
                    ft.View(
                        route="/signup",
                        controls=[signup_view],
                        padding=0,
                    )
                )
                logger.info("Signup view added to page")
            else:
                # Check if user is authenticated
                if not auth_view.current_user:
                    logger.info("User not authenticated, redirecting to login")
                    page.go("/login")
                    return
                
                # Add main view
                logger.info("Creating main view")
                page.views.append(
                    ft.View(
                        route="/",
                        controls=[main_layout],
                        padding=0,
                    )
                )
                logger.info("Main view added to page")
            
            page.update()
            logger.info("Page updated")
        except Exception as e:
            logger.error(f"Route change error: {str(e)}")
            page.views.clear()
            page.views.append(
                ft.View(
                    route="/error",
                    controls=[ft.Text(f"Error: {str(e)}")],
                    padding=20,
                )
            )
            page.update()
    
    # Create navigation rail
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PEOPLE_OUTLINE,
                selected_icon=ft.Icons.PEOPLE,
                label="Developers"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CHAT_OUTLINED,
                selected_icon=ft.Icons.CHAT,
                label="Chatbot"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings"
            ),
        ],
        on_change=lambda e: handle_navigation(e.control.selected_index)
    )
    
    # Create main content area
    content = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Image(
                    src="assets/images/System_Logo.png",
                    width=200,
                    height=200,
                    fit=ft.ImageFit.CONTAIN,
                    error_content=ft.Text("Logo not found", color=colors.RED)
                ),
                alignment=ft.alignment.center,
                padding=20,
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Welcome to CrewPilot",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=colors.WHITE,
                        ),
                        ft.Text(
                            "Please select a section from the navigation rail to begin",
                            size=16,
                            color=colors.BLUE_GREY_300,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    ),
                    padding=20,
                ),
                elevation=2,
                color=colors.BLUE_GREY_800,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        ),
        expand=True,
        padding=20,
        bgcolor=colors.BLUE_GREY_900,
    )
    
    # Create main layout
    main_layout = ft.Row(
        [
            nav_rail,
            ft.VerticalDivider(width=1),
            content,
        ],
        expand=True,
    )
    
    def handle_navigation(index):
        """Handle navigation rail selection"""
        try:
            if index == 0:
                content.content = create_dashboard()
            elif index == 1:
                content.content = create_workers_view()
            elif index == 2:
                content.content = get_chatbot_view(page)
            elif index == 3:
                content.content = create_settings_view()
            page.update()
        except Exception as e:
            logger.error(f"Navigation error: {str(e)}")
            show_error(f"Navigation error: {str(e)}")
    
    # Set up routing
    page.on_route_change = route_change
    logger.info("Routing set up")
    
    # Initialize with login view
    logger.info("Navigating to login view")
    page.go("/login")
    
    def create_stat_card(title: str, value: int, icon: str, color: str) -> Card:
        """Create a statistics card"""
        return Card(
            content=Container(
                content=Column([
                    Row([
                        Icon(icon, color=color, size=30),
                        Text(title, size=16, weight=ft.FontWeight.BOLD)
                    ], spacing=10),
                    Text(str(value), size=24, weight=ft.FontWeight.BOLD)
                ], spacing=10),
                padding=20
            ),
            elevation=2,
            shadow_color=colors.with_opacity(0.1, colors.BLACK),
            expand=True
        )
    
    def create_dashboard():
        try:
            # Get statistics
            total_workers = db.fetch_one("SELECT COUNT(*) as count FROM workers")['count']
            active_workers = db.fetch_one("SELECT COUNT(*) as count FROM workers WHERE status = 'active'")['count']
            high_performance = db.fetch_one("SELECT COUNT(*) as count FROM workers WHERE performance_score >= 8.0")['count']
            
            # Get recent activities
            activities = db.fetch_all("SELECT * FROM activities ORDER BY created_at DESC LIMIT 5")
            
            # Get worker names
            workers = {w['id']: w['name'] for w in db.fetch_all("SELECT id, name FROM workers")}
            
            # Create statistics cards
            stats_row = Row([
                create_stat_card("Total Developers", total_workers, ft.Icons.PEOPLE, colors.BLUE),
                create_stat_card("Active Developers", active_workers, ft.Icons.PERSON, colors.GREEN),
                create_stat_card("High Performance", high_performance, ft.Icons.STAR, colors.AMBER)
            ], spacing=20)
            
            # Create activity list with enhanced styling
            activity_list = Column([
                Text("Recent Activities", size=20, weight=ft.FontWeight.BOLD),
                *[
                    Card(
                        content=Container(
                            content=Row([
                                Icon(get_activity_icon(activity['activity_type']), 
                                     color=get_activity_color(activity['activity_type']), 
                                     size=30),
                                Column([
                                    Text(activity['description'], size=16),
                                    Text(f"Developer: {workers.get(activity['worker_id'], 'Unknown')}", 
                                         size=12, 
                                         color=colors.GREY_700)
                                ], spacing=5)
                            ], spacing=10),
                            padding=15
                        ),
                        elevation=1,
                        shadow_color=colors.with_opacity(0.1, colors.BLACK)
                    ) for activity in activities
                ]
            ], spacing=10)
            
            # Create main dashboard layout
            return Container(
                content=Column([
                    # Header
                    Container(
                        content=Text("Dashboard", size=30, weight=ft.FontWeight.BOLD),
                        padding=ft.padding.only(bottom=20)
                    ),
                    # Statistics cards
                    Container(
                        content=stats_row,
                        padding=ft.padding.only(bottom=20)
                    ),
                    # Activity list
                    Container(
                        content=activity_list,
                        expand=True
                    )
                ], spacing=0),
                expand=True
            )
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return Container(
                content=Text("Error loading dashboard", color=colors.RED),
                alignment=ft.alignment.center,
                expand=True
            )
    
    def show_error(message: str):
        """Show error message in a dialog"""
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(page, 'dialog', None))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.update()

    def create_analytics():
        """Create the analytics and predictions view"""
        try:
            # Form fields
            start_date = ft.TextField(
                label="Start Date",
                hint_text="YYYY-MM-DD",
                border=ft.InputBorder.UNDERLINE,
                width=300
            )
            
            end_date = ft.TextField(
                label="End Date",
                hint_text="YYYY-MM-DD",
                border=ft.InputBorder.UNDERLINE,
                width=300
            )
            
            # Get workers for dropdown
            workers = db.fetch_all("SELECT id, name FROM workers ORDER BY name")
            task_worker_dropdown = ft.Dropdown(
                label="Select Developer",
                options=[
                    ft.dropdown.Option(str(w['id']), w['name'])
                    for w in workers
                ],
                width=300
            )
            
            metrics_dropdown = ft.Dropdown(
                label="Select Metric",
                options=[
                    ft.dropdown.Option("performance", "Code Quality Score"),
                    ft.dropdown.Option("efficiency", "Development Efficiency"),
                    ft.dropdown.Option("tasks", "Features Completed"),
                    ft.dropdown.Option("hours", "Coding Hours"),
                    ft.dropdown.Option("prediction", "Performance Prediction")
                ],
                value="performance",
                width=300
            )
            
            # Prediction results container
            prediction_results = ft.Container(
                content=ft.Column([
                    ft.Text("Analytics Results", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Select parameters and click 'Generate Analytics' to see results.")
                ]),
                padding=20,
                bgcolor=colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=colors.with_opacity(0.1, colors.BLACK),
                )
            )
            
            def validate_date(date_str: str) -> bool:
                """Validate date format (YYYY-MM-DD)"""
                try:
                    from datetime import datetime
                    datetime.strptime(date_str, '%Y-%m-%d')
                    return True
                except ValueError:
                    return False
            
            def generate_analytics(e):
                try:
                    # Validate inputs
                    if not start_date.value or not end_date.value:
                        show_error("Please select both start and end dates")
                        return
                    
                    if not validate_date(start_date.value) or not validate_date(end_date.value):
                        show_error("Invalid date format. Please use YYYY-MM-DD")
                        return
                    
                    # Get selected metric and worker
                    metric = metrics_dropdown.value
                    worker_id = task_worker_dropdown.value
                    
                    # Map metric to database column
                    metric_columns = {
                        "performance": "w.performance_score",
                        "efficiency": "pp.efficiency_rate",
                        "tasks": "w.tasks_completed",
                        "hours": "pp.hours_worked",
                        "prediction": "pp.predicted_score"
                    }
                    
                    column = metric_columns[metric]
                    
                    # Build query based on selected worker
                    worker_filter = f"AND w.id = {worker_id}" if worker_id else ""
                    
                    # Fetch historical data
                    query = f"""
                        SELECT 
                            DATE(pp.created_at) as date,
                            AVG({column}) as value,
                            AVG(pp.confidence_score) as confidence,
                            COUNT(DISTINCT t.id) as total_tasks,
                            SUM(CASE WHEN t.is_completed = 1 THEN 1 ELSE 0 END) as completed_tasks
                        FROM workers w
                        LEFT JOIN performance_predictions pp ON w.id = pp.worker_id
                        LEFT JOIN tasks t ON w.id = t.worker_id
                        WHERE pp.created_at BETWEEN %s AND %s {worker_filter}
                        GROUP BY DATE(pp.created_at)
                        ORDER BY date
                    """
                    historical_data = db.fetch_all(query, (start_date.value, end_date.value))
                    
                    if not historical_data:
                        show_error("No data available for the selected date range")
                        return
                    
                    # Calculate simple moving average as prediction
                    window_size = 3
                    predictions = []
                    for i in range(len(historical_data)):
                        if i < window_size:
                            predictions.append(None)
                        else:
                            window = historical_data[i-window_size:i]
                            avg = sum(d['value'] for d in window) / window_size
                            predictions.append(avg)
                    
                    # Create chart data
                    chart_data = [
                        ft.LineChartData(
                            data_points=[
                                ft.LineChartDataPoint(
                                    x=float(i),
                                    y=float(d['value'])
                                ) for i, d in enumerate(historical_data)
                            ],
                            stroke_width=2,
                            color=colors.BLUE,
                            curved=True,
                            stroke_cap_round=True,
                        ),
                        ft.LineChartData(
                            data_points=[
                                ft.LineChartDataPoint(
                                    x=float(i),
                                    y=float(p) if p is not None else None
                                ) for i, p in enumerate(predictions)
                            ],
                            stroke_width=2,
                            color=colors.RED,
                            curved=True,
                            stroke_cap_round=True,
                        )
                    ]
                    
                    # Calculate statistics
                    avg_confidence = sum(d['confidence'] for d in historical_data) / len(historical_data)
                    total_tasks = sum(d['total_tasks'] for d in historical_data)
                    completed_tasks = sum(d['completed_tasks'] for d in historical_data)
                    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                    
                    # Create chart
                    chart = ft.LineChart(
                        data_series=chart_data,
                        border=ft.border.all(1, colors.GREY_400),
                        horizontal_grid_lines=ft.ChartGridLines(
                            interval=1,
                            color=colors.with_opacity(0.2, colors.GREY_400),
                        ),
                        vertical_grid_lines=ft.ChartGridLines(
                            interval=1,
                            color=colors.with_opacity(0.2, colors.GREY_400),
                        ),
                        left_axis=ft.ChartAxis(
                            labels=[str(i) for i in range(0, 101, 10)],
                            labels_size=40,
                        ),
                        bottom_axis=ft.ChartAxis(
                            labels=[d['date'] for d in historical_data],
                            labels_size=40,
                        ),
                        tooltip_bgcolor=colors.with_opacity(0.8, colors.BLUE_GREY),
                        min_y=0,
                        max_y=100,
                        expand=True,
                        height=300
                    )
                    
                    # Create statistics cards
                    stats_cards = ft.Row([
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Task Completion", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{completion_rate:.1f}%", size=24, color=colors.GREEN)
                                ]),
                                padding=20
                            ),
                            expand=True
                        ),
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Confidence", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{avg_confidence:.1f}%", size=24, color=colors.BLUE)
                                ]),
                                padding=20
                            ),
                            expand=True
                        ),
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Total Tasks", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(str(total_tasks), size=24, color=colors.PURPLE)
                                ]),
                                padding=20
                            ),
                            expand=True
                        )
                    ], spacing=20)
                    
                    # Update results container
                    prediction_results.content = ft.Column([
                        ft.Text("Analytics Results", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Metric: {metrics_dropdown.value.title()}"),
                        ft.Text(f"Date Range: {start_date.value} to {end_date.value}"),
                        stats_cards,
                        ft.Container(
                            content=chart,
                            padding=20,
                            bgcolor=colors.WHITE,
                            border_radius=10,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=colors.with_opacity(0.1, colors.BLACK),
                            )
                        ),
                        ft.Text("Blue line: Historical Data", color=colors.BLUE),
                        ft.Text("Red line: Predicted Trend", color=colors.RED)
                    ])
                    
                    page.update()
                    
                except Exception as e:
                    logger.error(f"Error generating analytics: {str(e)}")
                    show_error(str(e))
            
            return ft.Container(
                content=ft.ListView(
                    controls=[
                        ft.Text("Analytics & Predictions", size=30, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("Generate Analytics", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Row([start_date, end_date], spacing=20),
                                        ft.Row([task_worker_dropdown, metrics_dropdown], spacing=20),
                                        ft.ElevatedButton(
                                            "Generate Analytics",
                                            icon=ft.Icons.ANALYTICS,
                                            on_click=generate_analytics,
                                            style=ft.ButtonStyle(
                                                color=colors.WHITE,
                                                bgcolor=colors.BLUE,
                                                shape=ft.RoundedRectangleBorder(radius=10)
                                            )
                                        )
                                    ]),
                                    padding=20
                                ),
                                elevation=2,
                                shadow_color=colors.with_opacity(0.1, colors.BLACK)
                            ),
                            padding=20,
                            bgcolor=colors.WHITE,
                            border_radius=10,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=colors.with_opacity(0.1, colors.BLACK),
                            )
                        ),
                        prediction_results
                    ],
                    spacing=20,
                    padding=20,
                    expand=True
                ),
                expand=True
            )
            
        except Exception as e:
            logger.error(f"Error creating analytics view: {str(e)}")
            return ft.Text(f"Error creating analytics view: {str(e)}")
    
    def create_workers_view():
        """Create the workers management view"""
        try:
            # Form fields
            name_field = ft.TextField(
                label="Developer Name",
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=colors.BLUE,
                width=300
            )
            
            role_field = ft.TextField(
                label="Development Role",
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=colors.BLUE,
                width=300
            )
            
            status_dropdown = ft.Dropdown(
                label="Status",
                options=[
                    ft.dropdown.Option("active", "Active"),
                    ft.dropdown.Option("inactive", "Inactive"),
                    ft.dropdown.Option("on_leave", "On Leave")
                ],
                value="active",
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=colors.BLUE,
                width=300
            )
            
            performance_field = ft.TextField(
                label="Code Quality Score",
                value="0.0",
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=colors.BLUE,
                width=300
            )
            
            # Task entry fields
            task_worker_dropdown = ft.Dropdown(
                label="Select Developer",
                options=[],
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=colors.BLUE,
                width=300
            )
            
            task_description = ft.TextField(
                label="Feature Description",
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=colors.BLUE,
                width=300,
                multiline=True,
                min_lines=2,
                max_lines=4
            )
            
            # Selected worker for editing
            selected_worker = None
            
            def update_worker_dropdown():
                """Update the worker dropdown options"""
                try:
                    workers = db.fetch_all("SELECT id, name FROM workers ORDER BY name")
                    task_worker_dropdown.options = [
                        ft.dropdown.Option(str(w['id']), w['name'])
                        for w in workers
                    ]
                    if workers:
                        task_worker_dropdown.value = str(workers[0]['id'])
                    page.update()
                except Exception as e:
                    logger.error(f"Error updating worker dropdown: {str(e)}")
                    show_error("Failed to update worker list")
            
            def load_workers():
                """Load and display workers with their tasks"""
                try:
                    # Get all workers with their task counts and efficiency
                    workers = db.fetch_all("""
                        SELECT 
                            w.*,
                            COALESCE(COUNT(DISTINCT t.id), 0) as total_tasks,
                            COALESCE(SUM(CASE WHEN t.is_completed = 1 THEN 1 ELSE 0 END), 0) as completed_tasks,
                            COALESCE(AVG(pp.efficiency_rate), 0) as avg_efficiency
                        FROM workers w
                        LEFT JOIN tasks t ON w.id = t.worker_id
                        LEFT JOIN performance_predictions pp ON w.id = pp.worker_id
                        GROUP BY w.id, w.name, w.role, w.status, w.performance_score, w.created_at, w.tasks_completed, w.tasks_to_complete
                        ORDER BY w.name
                    """)
                    
                    # Get incomplete tasks for each worker
                    for worker in workers:
                        incomplete_tasks = db.fetch_all("""
                            SELECT id, task_description, created_at
                            FROM tasks
                            WHERE worker_id = %s AND is_completed = 0
                            ORDER BY created_at DESC
                        """, (worker['id'],))
                        worker['incomplete_tasks'] = incomplete_tasks
                    
                    # Create worker cards
                    worker_cards = []
                    for worker in workers:
                        # Create task list
                        task_list = ft.ListView(
                            controls=[
                                ft.Container(
                                    content=ft.Row([
                                        ft.Column([
                                            ft.Text(task['task_description'], size=14),
                                            ft.Text(f"Created: {task['created_at']}", size=12, color=colors.GREY_400)
                                        ], spacing=5),
                                        ft.ElevatedButton(
                                            "Done",
                                            icon=ft.Icons.CHECK_CIRCLE,
                                            on_click=lambda e, t=task, w=worker: complete_task(w, t),
                                            style=ft.ButtonStyle(
                                                color=colors.WHITE,
                                                bgcolor=colors.GREEN,
                                                shape=ft.RoundedRectangleBorder(radius=10)
                                            )
                                        )
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    padding=10,
                                    bgcolor=colors.BLUE_GREY_800,
                                    border_radius=5
                                ) for task in worker['incomplete_tasks']
                            ],
                            spacing=5,
                            height=200
                        ) if worker['incomplete_tasks'] else ft.Text("No pending features", color=colors.GREY_400)
                        
                        # Create worker card
                        worker_card = ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text(worker['name'], size=20, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=ft.Text(
                                                worker['status'].upper(),
                                                color=colors.WHITE,
                                                size=12
                                            ),
                                            bgcolor=colors.GREEN if worker['status'] == 'active' else colors.RED,
                                            padding=5,
                                            border_radius=5
                                        )
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Text(f"Role: {worker['role']}", size=16),
                                    ft.Text(f"Code Quality Score: {worker['performance_score']:.1f}", size=16),
                                    ft.Text(f"Features Completed: {worker['tasks_completed']}/{worker['total_tasks']}", size=16),
                                    ft.Text(f"Development Efficiency: {worker['avg_efficiency']:.1f}%", size=16),
                                    ft.Text("Pending Features:", size=16, weight=ft.FontWeight.BOLD),
                                    task_list,
                                    ft.Row([
                                        ft.ElevatedButton(
                                            "Edit",
                                            icon=ft.Icons.EDIT,
                                            on_click=lambda e, w=worker: edit_worker(w)
                                        ),
                                        ft.ElevatedButton(
                                            "Delete",
                                            icon=ft.Icons.DELETE,
                                            on_click=lambda e, w=worker: delete_worker(w),
                                            color=colors.RED
                                        )
                                    ], alignment=ft.MainAxisAlignment.END)
                                ], spacing=10),
                                padding=20
                            ),
                            elevation=2
                        )
                        worker_cards.append(worker_card)
                    
                    return ft.ListView(
                        controls=worker_cards,
                        spacing=20,
                        padding=20,
                        expand=True
                    )
                except Exception as e:
                    logger.error(f"Error loading workers: {str(e)}")
                    return ft.Text("Error loading workers", color=colors.RED)
            
            def complete_task(worker, task):
                """Complete a task for the worker"""
                try:
                    # Start transaction
                    db.execute_query("START TRANSACTION")
                    
                    try:
                        # Update task status
                        db.execute_query("""
                            UPDATE tasks 
                            SET is_completed = 1
                            WHERE id = %s
                        """, (task['id'],))
                        
                        # Update worker's tasks_completed count
                        db.execute_query("""
                            UPDATE workers 
                            SET tasks_completed = tasks_completed + 1
                            WHERE id = %s
                        """, (worker['id'],))
                        
                        # Generate new performance prediction
                        import random
                        hours_worked = random.uniform(4, 8)
                        efficiency_rate = random.uniform(70, 95)
                        predicted_score = (efficiency_rate + worker['performance_score']) / 2
                        confidence_score = random.uniform(80, 95)
                        
                        db.execute_query("""
                            INSERT INTO performance_predictions 
                            (worker_id, hours_worked, tasks_completed, efficiency_rate, 
                             predicted_score, confidence_score)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            worker['id'],
                            hours_worked,
                            worker['tasks_completed'] + 1,
                            efficiency_rate,
                            predicted_score,
                            confidence_score
                        ))
                        
                        # Add activity record
                        db.execute_query("""
                            INSERT INTO activities 
                            (worker_id, activity_type, description)
                            VALUES (%s, %s, %s)
                        """, (
                            worker['id'],
                            'task_completed',
                            f"Completed feature: {task['task_description']}"
                        ))
                        
                        # Commit transaction
                        db.execute_query("COMMIT")
                        
                        # Refresh workers table
                        workers_table = load_workers()
                        workers_section.content = workers_table
                        page.update()
                        
                    except Exception as e:
                        # Rollback transaction on error
                        db.execute_query("ROLLBACK")
                        raise e
                    
                except Exception as e:
                    logger.error(f"Error completing task: {str(e)}")
                    show_error(str(e))
            
            def clear_form():
                nonlocal selected_worker
                name_field.value = ""
                role_field.value = ""
                status_dropdown.value = "active"
                performance_field.value = "0.0"
                selected_worker = None
                page.update()
            
            def submit_worker(e):
                try:
                    if selected_worker:
                        # Update existing worker
                        db.execute_query("""
                            UPDATE workers 
                            SET name = %s, role = %s, status = %s, performance_score = %s
                            WHERE id = %s
                        """, (
                            name_field.value,
                            role_field.value,
                            status_dropdown.value,
                            float(performance_field.value),
                            selected_worker['id']
                        ))
                    else:
                        # Add new worker
                        db.execute_query("""
                            INSERT INTO workers (name, role, status, performance_score)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            name_field.value,
                            role_field.value,
                            status_dropdown.value,
                            float(performance_field.value)
                        ))
                    
                    # Refresh workers table and dropdown
                    workers_table = load_workers()
                    workers_section.content = workers_table
                    update_worker_dropdown()
                    clear_form()
                    page.update()
                    
                except Exception as e:
                    logger.error(f"Error submitting worker: {str(e)}")
                    show_error(str(e))
            
            def edit_worker(worker):
                """Edit a worker's details"""
                nonlocal selected_worker
                selected_worker = worker
                name_field.value = worker['name']
                role_field.value = worker['role']
                status_dropdown.value = worker['status']
                performance_field.value = str(worker['performance_score'])
                page.update()
            
            def delete_worker(worker):
                """Delete a worker"""
                def confirm_delete(e):
                    try:
                        # Start transaction
                        db.execute_query("START TRANSACTION")
                        
                        try:
                            # Delete related records first
                            db.execute_query("DELETE FROM performance_predictions WHERE worker_id = %s", (worker['id'],))
                            db.execute_query("DELETE FROM tasks WHERE worker_id = %s", (worker['id'],))
                            db.execute_query("DELETE FROM workers WHERE id = %s", (worker['id'],))
                            
                            # Commit transaction
                            db.execute_query("COMMIT")
                            
                            # Refresh UI
                            workers_table = load_workers()
                            workers_section.content = workers_table
                            update_worker_dropdown()
                            page.update()
                            
                        except Exception as e:
                            # Rollback transaction on error
                            db.execute_query("ROLLBACK")
                            raise e
                            
                    except Exception as e:
                        logger.error(f"Error deleting worker: {str(e)}")
                        show_error(str(e))
                    finally:
                        page.dialog = None
                        page.update()
                
                page.dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirm Delete"),
                    content=ft.Text(f"Are you sure you want to delete {worker['name']}?"),
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda e: setattr(page, 'dialog', None)),
                        ft.TextButton("Delete", on_click=confirm_delete)
                    ],
                    actions_alignment=ft.MainAxisAlignment.END
                )
                page.update()
            
            def submit_task(e):
                try:
                    if not task_worker_dropdown.value:
                        show_error("Please select a worker")
                        return
                    
                    if not task_description.value:
                        show_error("Please enter a task description")
                        return
                    
                    worker_id = int(task_worker_dropdown.value)
                    
                    # Start transaction
                    db.execute_query("START TRANSACTION")
                    
                    try:
                        # Get worker's current stats
                        worker = db.fetch_one("""
                            SELECT 
                                performance_score,
                                tasks_completed,
                                tasks_to_complete
                            FROM workers 
                            WHERE id = %s
                            FOR UPDATE
                        """, (worker_id,))
                        
                        if not worker:
                            raise Exception("Worker not found")
                        
                        # Add task
                        db.execute_query("""
                            INSERT INTO tasks (worker_id, task_description, is_completed)
                            VALUES (%s, %s, 0)
                        """, (worker_id, task_description.value))
                        
                        # Generate performance prediction
                        import random
                        hours_worked = random.uniform(4, 8)
                        tasks_completed = worker['tasks_completed']
                        efficiency_rate = random.uniform(70, 95)
                        predicted_score = (efficiency_rate + worker['performance_score']) / 2
                        confidence_score = random.uniform(80, 95)
                        
                        db.execute_query("""
                            INSERT INTO performance_predictions 
                            (worker_id, hours_worked, tasks_completed, efficiency_rate, 
                             predicted_score, confidence_score)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            worker_id,
                            hours_worked,
                            tasks_completed,
                            efficiency_rate,
                            predicted_score,
                            confidence_score
                        ))
                        
                        # Update worker's task count
                        db.execute_query("""
                            UPDATE workers 
                            SET tasks_to_complete = tasks_to_complete + 1
                            WHERE id = %s
                        """, (worker_id,))
                        
                        # Commit transaction
                        db.execute_query("COMMIT")
                        
                        # Refresh workers table
                        workers_table = load_workers()
                        workers_section.content = workers_table
                        
                        # Clear task form
                        task_description.value = ""
                        page.update()
                        
                    except Exception as e:
                        # Rollback transaction on error
                        db.execute_query("ROLLBACK")
                        raise e
                    
                except Exception as e:
                    logger.error(f"Error adding task: {str(e)}")
                    show_error(str(e))
            
            # Initialize worker dropdown
            update_worker_dropdown()
            
            # Create workers section
            workers_section = ft.Container(
                content=load_workers(),
                expand=True,
                padding=20,
                bgcolor=colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=colors.with_opacity(0.1, colors.BLACK),
                )
            )
            
            return ft.Container(
                content=ft.ListView(
                    controls=[
                        ft.Text("Developer Management", size=30, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("Add/Edit Developer", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Row([name_field, role_field], spacing=20),
                                        ft.Row([status_dropdown, performance_field], spacing=20),
                                        ft.Row([
                                            ft.ElevatedButton(
                                                "Submit",
                                                icon=ft.Icons.SAVE,
                                                on_click=submit_worker,
                                                style=ft.ButtonStyle(
                                                    color=colors.WHITE,
                                                    bgcolor=colors.BLUE,
                                                    shape=ft.RoundedRectangleBorder(radius=10)
                                                )
                                            ),
                                            ft.ElevatedButton(
                                                "Clear",
                                                icon=ft.Icons.CLEAR,
                                                on_click=lambda e: clear_form(),
                                                style=ft.ButtonStyle(
                                                    color=colors.WHITE,
                                                    bgcolor=colors.GREY,
                                                    shape=ft.RoundedRectangleBorder(radius=10)
                                                )
                                            )
                                        ], spacing=10)
                                    ]),
                                    padding=20
                                ),
                                elevation=2,
                                shadow_color=colors.with_opacity(0.1, colors.BLACK)
                            ),
                            padding=20,
                            bgcolor=colors.WHITE,
                            border_radius=10,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=colors.with_opacity(0.1, colors.BLACK),
                            )
                        ),
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("Assign Feature", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Row([task_worker_dropdown, task_description], spacing=20),
                                        ft.ElevatedButton(
                                            "Assign Feature",
                                            icon=ft.Icons.ADD_TASK,
                                            on_click=submit_task,
                                            style=ft.ButtonStyle(
                                                color=colors.WHITE,
                                                bgcolor=colors.GREEN,
                                                shape=ft.RoundedRectangleBorder(radius=10)
                                            )
                                        )
                                    ]),
                                    padding=20
                                ),
                                elevation=2,
                                shadow_color=colors.with_opacity(0.1, colors.BLACK)
                            ),
                            padding=20,
                            bgcolor=colors.WHITE,
                            border_radius=10,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=colors.with_opacity(0.1, colors.BLACK),
                            )
                        ),
                        ft.Text("Developer List", size=20, weight=ft.FontWeight.BOLD),
                        workers_section
                    ],
                    spacing=20,
                    padding=20,
                    expand=True
                ),
                expand=True
            )
            
        except Exception as e:
            logger.error(f"Error creating workers view: {str(e)}")
            return ft.Text(f"Error creating workers view: {str(e)}")

    def create_settings_view():
        """Create the settings view"""
        try:
            # Get current user information
            user = auth_view.current_user
            
            # Create editable fields
            username_field = ft.TextField(
                label="Username",
                value=user['username'],
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=colors.BLUE,
                width=300
            )
            
            email_field = ft.TextField(
                label="Email",
                value=user['email'],
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=colors.BLUE,
                width=300
            )
            
            # Error message
            error_text = ft.Text(
                color=colors.RED,
                size=12,
                visible=False
            )
            
            # Success message
            success_text = ft.Text(
                color=colors.GREEN,
                size=12,
                visible=False
            )
            
            def save_changes(e):
                """Save user information changes"""
                try:
                    new_username = username_field.value
                    new_email = email_field.value
                    
                    # Validate fields
                    if not new_username or not new_email:
                        error_text.value = "Please fill in all fields"
                        error_text.visible = True
                        success_text.visible = False
                        page.update()
                        return
                    
                    # Validate username
                    is_valid, error = validate_username(new_username)
                    if not is_valid:
                        error_text.value = error
                        error_text.visible = True
                        success_text.visible = False
                        page.update()
                        return
                    
                    # Validate email
                    if not validate_email(new_email):
                        error_text.value = "Invalid email format"
                        error_text.visible = True
                        success_text.visible = False
                        page.update()
                        return
                    
                    # Check if username or email already exists (excluding current user)
                    existing_user = db.fetch_one(
                        "SELECT * FROM users WHERE (username = %s OR email = %s) AND id != %s",
                        (new_username, new_email, user['id'])
                    )
                    
                    if existing_user:
                        error_text.value = "Username or email already exists"
                        error_text.visible = True
                        success_text.visible = False
                        page.update()
                        return
                    
                    # Update user information
                    db.execute_query(
                        "UPDATE users SET username = %s, email = %s WHERE id = %s",
                        (new_username, new_email, user['id'])
                    )
                    
                    # Update current user
                    auth_view.current_user['username'] = new_username
                    auth_view.current_user['email'] = new_email
                    
                    # Show success message
                    success_text.value = "Changes saved successfully"
                    success_text.visible = True
                    error_text.visible = False
                    
                    page.update()
                    
                except Exception as e:
                    logger.error(f"Error saving changes: {str(e)}")
                    error_text.value = "An error occurred while saving changes"
                    error_text.visible = True
                    success_text.visible = False
                    page.update()
            
            # Create user info card
            user_info = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Edit User Information", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        username_field,
                        email_field,
                        ft.Row([
                            ft.Icon(ft.Icons.BADGE, color=colors.BLUE),
                            ft.Text(f"Role: {user['role'].title()}", size=16)
                        ], spacing=10),
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY, color=colors.BLUE),
                            ft.Text(f"Member since: {user['created_at'].strftime('%Y-%m-%d')}", size=16)
                        ], spacing=10),
                        ft.Row([
                            ft.Icon(ft.Icons.LOGIN, color=colors.BLUE),
                            ft.Text(f"Last login: {user['last_login'].strftime('%Y-%m-%d %H:%M') if user['last_login'] else 'N/A'}", size=16)
                        ], spacing=10),
                        error_text,
                        success_text,
                        ft.ElevatedButton(
                            "Save Changes",
                            icon=ft.Icons.SAVE,
                            on_click=save_changes,
                            style=ft.ButtonStyle(
                                color=colors.WHITE,
                                bgcolor=colors.BLUE,
                                shape=ft.RoundedRectangleBorder(radius=10)
                            )
                        )
                    ]),
                    padding=20
                ),
                elevation=2,
                shadow_color=colors.with_opacity(0.1, colors.BLACK)
            )
            
            # Create logout button
            logout_button = ft.ElevatedButton(
                "Logout",
                icon=ft.Icons.LOGOUT,
                on_click=lambda e: handle_logout(),
                style=ft.ButtonStyle(
                    color=colors.WHITE,
                    bgcolor=colors.RED,
                    shape=ft.RoundedRectangleBorder(radius=10)
                )
            )
            
            def handle_logout():
                """Handle user logout"""
                try:
                    auth_view.current_user = None
                    page.go("/login")
                except Exception as e:
                    logger.error(f"Logout error: {str(e)}")
                    show_error("Error during logout")
            
            return ft.Container(
                content=ft.Column([
                    ft.Text("Settings", size=30, weight=ft.FontWeight.BOLD),
                    user_info,
                    ft.Container(
                        content=logout_button,
                        alignment=ft.alignment.center,
                        padding=20
                    )
                ]),
                padding=20,
                expand=True
            )
            
        except Exception as e:
            logger.error(f"Error creating settings view: {str(e)}")
            return ft.Text(f"Error creating settings view: {str(e)}")

ft.app(target=main) 