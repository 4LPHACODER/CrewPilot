import flet as ft
from flet_core import colors
from database.db_connection import DatabaseConnection
from utils.utils import format_currency, format_percentage

def create_dashboard_view(db: DatabaseConnection, page: ft.Page):
    """Create the dashboard view"""
    
    def refresh_data(e):
        """Refresh dashboard data"""
        stats_row.controls = [
            create_stat_card("Total Workers", get_total_workers(), ft.Icons.PEOPLE, colors.BLUE),
            create_stat_card("Active Workers", get_active_workers(), ft.Icons.PERSON, colors.GREEN),
            create_stat_card("High Performance", get_high_performance_workers(), ft.Icons.STAR, colors.AMBER)
        ]
        activity_list.content = create_activity_list()
        page.update()

    def create_stat_card(title: str, value: int, icon: str, color: str):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color),
                    ft.Text(title, size=16)
                ]),
                ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD)
            ]),
            padding=20,
            border_radius=10,
            bgcolor=colors.SURFACE_VARIANT,
            width=200
        )

    def get_total_workers() -> int:
        try:
            result = db.fetch_one("SELECT COUNT(*) as count FROM workers")
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting total workers: {e}")
            return 0

    def get_active_workers() -> int:
        try:
            result = db.fetch_one("SELECT COUNT(*) as count FROM workers WHERE status = 'active'")
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting active workers: {e}")
            return 0

    def get_high_performance_workers() -> int:
        try:
            result = db.fetch_one("SELECT COUNT(*) as count FROM workers WHERE performance_score >= 8")
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting high performance workers: {e}")
            return 0

    def create_activity_list():
        try:
            activities = db.fetch_all("""
                SELECT a.*, w.name as worker_name 
                FROM activities a
                LEFT JOIN workers w ON a.worker_id = w.id
                ORDER BY a.timestamp DESC
                LIMIT 10
            """)
            
            return ft.Column([
                ft.ListTile(
                    leading=ft.Icon(get_activity_icon(activity['type']), color=get_activity_color(activity['type'])),
                    title=ft.Text(activity['description']),
                    subtitle=ft.Text(f"Worker: {activity['worker_name']}" if activity['worker_name'] else "System"),
                    trailing=ft.Text(activity['timestamp'].strftime("%Y-%m-%d %H:%M"))
                ) for activity in activities
            ])
        except Exception as e:
            print(f"Error creating activity list: {e}")
            return ft.Column([ft.Text("Error loading activities")])

    def get_activity_icon(activity_type: str) -> str:
        icons = {
            'worker_added': ft.Icons.PERSON_ADD,
            'worker_updated': ft.Icons.EDIT,
            'worker_removed': ft.Icons.DELETE,
            'performance_updated': ft.Icons.TRENDING_UP,
            'system': ft.Icons.SETTINGS
        }
        return icons.get(activity_type, ft.Icons.INFO)

    def get_activity_color(activity_type: str) -> str:
        activity_colors = {
            'worker_added': colors.GREEN,
            'worker_updated': colors.BLUE,
            'worker_removed': colors.RED,
            'performance_updated': colors.AMBER,
            'system': colors.GREY
        }
        return activity_colors.get(activity_type, colors.GREY)

    # Create header
    header = ft.Row([
        ft.Text("Dashboard", size=30, weight=ft.FontWeight.BOLD),
        ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh",
            on_click=refresh_data
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Create statistics row
    stats_row = ft.Row([
        create_stat_card("Total Workers", get_total_workers(), ft.Icons.PEOPLE, colors.BLUE),
        create_stat_card("Active Workers", get_active_workers(), ft.Icons.PERSON, colors.GREEN),
        create_stat_card("High Performance", get_high_performance_workers(), ft.Icons.STAR, colors.AMBER)
    ], alignment=ft.MainAxisAlignment.SPACE_AROUND)

    # Create activity section
    activity_section = ft.Container(
        content=ft.Column([
            ft.Text("Recent Activities", size=20, weight=ft.FontWeight.BOLD),
            create_activity_list()
        ]),
        padding=20,
        border_radius=10,
        bgcolor=colors.SURFACE_VARIANT
    )

    # Create quick actions
    quick_actions = ft.Container(
        content=ft.Column([
            ft.Text("Quick Actions", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.ElevatedButton(
                    "Add Worker",
                    icon=ft.Icons.PERSON_ADD,
                    on_click=lambda e: page.go("/workers")
                )
            ])
        ]),
        padding=20,
        border_radius=10,
        bgcolor=colors.SURFACE_VARIANT
    )

    # Create main container
    return ft.Container(
        content=ft.Column([
            header,
            stats_row,
            ft.Row([
                activity_section,
                quick_actions
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]),
        padding=20
    ) 