import flet as ft
from flet_core import colors
from database.db_connection import DatabaseConnection
from authentication.auth_utils import (
    hash_password, verify_password, validate_email,
    validate_password, validate_username
)
import logging

logger = logging.getLogger(__name__)

class AuthView:
    def __init__(self, page: ft.Page, db: DatabaseConnection):
        self.page = page
        self.db = db
        self.current_user = None
        logger.info("AuthView initialized")
        
    def create_login_view(self):
        """Create the login view"""
        logger.info("Creating login view")
        try:
            # Form fields
            username_field = ft.TextField(
                label="Username",
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=colors.BLUE,
                width=300
            )
            
            password_field = ft.TextField(
                label="Password",
                password=True,
                can_reveal_password=True,
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
            
            def login(e):
                try:
                    username = username_field.value
                    password = password_field.value
                    
                    # Validate fields
                    if not username or not password:
                        error_text.value = "Please fill in all fields"
                        error_text.visible = True
                        self.page.update()
                        return
                    
                    # Get user from database
                    user = self.db.fetch_one(
                        "SELECT * FROM users WHERE username = %s",
                        (username,)
                    )
                    
                    if not user or not verify_password(password, user['password_hash']):
                        error_text.value = "Invalid username or password"
                        error_text.visible = True
                        self.page.update()
                        return
                    
                    # Set current user
                    self.current_user = user
                    logger.info(f"User logged in: {username}")
                    
                    # Update last login
                    self.db.execute_query(
                        "UPDATE users SET last_login = NOW() WHERE id = %s",
                        (user['id'],)
                    )
                    
                    # Clear form
                    username_field.value = ""
                    password_field.value = ""
                    error_text.visible = False
                    
                    # Navigate to main app
                    self.page.go("/")
                    
                except Exception as e:
                    logger.error(f"Login error: {str(e)}")
                    error_text.value = "An error occurred during login"
                    error_text.visible = True
                    self.page.update()
            
            # Create login form
            login_form = ft.Column([
                ft.Text("Login", size=30, weight=ft.FontWeight.BOLD),
                username_field,
                password_field,
                error_text,
                ft.ElevatedButton(
                    "Login",
                    on_click=login,
                    style=ft.ButtonStyle(
                        color=colors.WHITE,
                        bgcolor=colors.BLUE,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    )
                ),
                ft.TextButton(
                    "Don't have an account? Sign Up",
                    on_click=lambda _: self.page.go("/signup")
                )
            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
            
            # Create side-by-side layout
            layout = ft.Row(
                [
                    # Left side - Logo
                    ft.Container(
                        content=ft.Image(
                            src="assets/images/System_Logo.png",
                            width=400,
                            height=400,
                            fit=ft.ImageFit.CONTAIN,
                            error_content=ft.Text("Logo not found", color=colors.RED)
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                        bgcolor=colors.BLUE_50,
                    ),
                    # Right side - Login form
                    ft.Container(
                        content=login_form,
                        alignment=ft.alignment.center,
                        expand=True,
                        padding=40,
                    ),
                ],
                expand=True,
            )
            
            logger.info("Login view created successfully")
            return layout
            
        except Exception as e:
            logger.error(f"Error creating login view: {str(e)}")
            return ft.Text(f"Error creating login view: {str(e)}")
    
    def create_signup_view(self):
        """Create the signup view"""
        # Form fields
        username_field = ft.TextField(
            label="Username",
            border=ft.InputBorder.UNDERLINE,
            focused_border_color=colors.BLUE,
            width=300
        )
        
        email_field = ft.TextField(
            label="Email",
            border=ft.InputBorder.UNDERLINE,
            focused_border_color=colors.BLUE,
            width=300
        )
        
        password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            border=ft.InputBorder.UNDERLINE,
            focused_border_color=colors.BLUE,
            width=300
        )
        
        confirm_password_field = ft.TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
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
        
        def signup(e):
            try:
                username = username_field.value
                email = email_field.value
                password = password_field.value
                confirm_password = confirm_password_field.value
                
                # Validate fields
                if not all([username, email, password, confirm_password]):
                    error_text.value = "Please fill in all fields"
                    error_text.visible = True
                    self.page.update()
                    return
                
                # Validate username
                is_valid, error = validate_username(username)
                if not is_valid:
                    error_text.value = error
                    error_text.visible = True
                    self.page.update()
                    return
                
                # Validate email
                if not validate_email(email):
                    error_text.value = "Invalid email format"
                    error_text.visible = True
                    self.page.update()
                    return
                
                # Validate password
                is_valid, error = validate_password(password)
                if not is_valid:
                    error_text.value = error
                    error_text.visible = True
                    self.page.update()
                    return
                
                # Check if passwords match
                if password != confirm_password:
                    error_text.value = "Passwords do not match"
                    error_text.visible = True
                    self.page.update()
                    return
                
                # Check if username or email already exists
                existing_user = self.db.fetch_one(
                    "SELECT * FROM users WHERE username = %s OR email = %s",
                    (username, email)
                )
                
                if existing_user:
                    error_text.value = "Username or email already exists"
                    error_text.visible = True
                    self.page.update()
                    return
                
                # Hash password
                password_hash = hash_password(password)
                
                # Create user
                self.db.execute_query(
                    "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    (username, email, password_hash, 'user')
                )
                
                # Clear form
                username_field.value = ""
                email_field.value = ""
                password_field.value = ""
                confirm_password_field.value = ""
                error_text.visible = False
                
                # Navigate to login
                self.page.go("/login")
                
            except Exception as e:
                logger.error(f"Signup error: {str(e)}")
                error_text.value = "An error occurred during signup"
                error_text.visible = True
                self.page.update()
        
        # Create signup form
        signup_form = ft.Column([
            ft.Text("Sign Up", size=30, weight=ft.FontWeight.BOLD),
            username_field,
            email_field,
            password_field,
            confirm_password_field,
            error_text,
            ft.ElevatedButton(
                "Sign Up",
                on_click=signup,
                style=ft.ButtonStyle(
                    color=colors.WHITE,
                    bgcolor=colors.BLUE,
                    shape=ft.RoundedRectangleBorder(radius=10)
                )
            ),
            ft.TextButton(
                "Already have an account? Login",
                on_click=lambda _: self.page.go("/login")
            )
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        
        # Create side-by-side layout with scrollable form
        layout = ft.Row(
            [
                # Left side - Logo
                ft.Container(
                    content=ft.Image(
                        src="assets/images/System_Logo.png",
                        width=400,
                        height=400,
                        fit=ft.ImageFit.CONTAIN,
                        error_content=ft.Text("Logo not found", color=colors.RED)
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                    bgcolor=colors.BLUE_50,
                ),
                # Right side - Scrollable signup form
                ft.Container(
                    content=ft.ListView(
                        controls=[signup_form],
                        spacing=20,
                        padding=40,
                        expand=True,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ],
            expand=True,
        )
        
        return layout 